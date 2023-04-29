from led_controller import LedController
from time import sleep as time_sleep
from os import environ
from json import load
from jsonschema import validate as json_validate
from jsonschema.exceptions import ValidationError
from numexpr import evaluate as ne_eval

from environment_variables import CLEVER_SLEEP_SECS_SEGMENTS

ALARM_MODIFY_REGEX_PATTERN = "^(\(|\)|\d+\.\d+|\d+|red|blue|green|[+\-*/%]|i|\s)*$"
ALARM_JSONSCHEMA = {
    "type": "object",
    "properties": {
        "wait_time": { "type": "number" },
        "when_yellow": { "type": "number" },
        "repeat_last": { "type": "number" },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sleep": { "oneOf": [ { "type": "string" }, { "type": "number" } ] },
                    "range": {
                        "type": "object",
                        "properties": {
                        "start": { "type": "number", "pattern": ALARM_MODIFY_REGEX_PATTERN },
                        "stop": { "type": "number", "pattern": ALARM_MODIFY_REGEX_PATTERN },
                        "step": { "type": "number", "pattern": ALARM_MODIFY_REGEX_PATTERN }
                        },
                        "required": [],
                        "additionalProperties": False
                    },
                    "transition": {
                        "type": "object",
                        "properties": {
                        "red": { "type": "number" },
                        "green": { "type": "number" },
                        "blue": { "type": "number" },
                        "steps": { "type": "number" }
                        },
                        "required": [],
                        "additionalProperties": False
                    },
                    "modify": {
                        "type": "object",
                        "properties": {
                        "red": { "type": "string" },
                        "green": { "type": "string" },
                        "blue": { "type": "string" }
                        },
                        "required": [],
                        "additionalProperties": False
                    }
                },
                "required": ["sleep"],
                "additionalProperties": False
            }
        }
    },
    "required": ["wait_time", "when_yellow", "steps"],
    "additionalProperties": False,
}

class AlarmRunner:
    def __init__(self, config_path="alarm.json"):
        self.config_path = config_path
        self.parsed_config = load(open(self.config_path, "r", encoding="UTF-8"))
        self.led_controller = LedController()
        try:
            json_validate(self.parsed_config, ALARM_JSONSCHEMA)
        except ValidationError as err:
            print(f"Alarm config was invalid (path: {self.config_path}). Message: {err.message}.")
            exit(1)
        self.load_config()

    def load_config(self):
        self.wait_time = self.parsed_config["wait_time"]
        self.when_yellow = self.parsed_config["when_yellow"]
        self.repeat_last = self.parsed_config.get("repeat_last")
        self.steps = self.parsed_config["steps"]

    def start(self):
        replace_vars = {"wait_time": self.wait_time, "red": lambda: self.led_controller.red, "green": lambda: self.led_controller.green, "blue": lambda: self.led_controller.blue}
        for step in self.steps:
            self.run_step(replace_vars, step)
        if self.repeat_last:
            while True:
                for step in self.steps[-self.repeat_last:]: self.run_step(replace_vars, step)

    def run_step(self, replace_vars, step):
        if (range_data:=step.get("range")) or (transition_data:=step.get("transition")):
            if range_data:
                for i in range(range_data.get("start", 0), range_data.get("stop", 10), range_data.get("step", 1)):
                    self.run_modify(step.get("modify", {}), {**replace_vars, "i":i})
                    if not self.clever_sleep(self.wait_time if step["sleep"] == "wait_time" else step["sleep"]): return
            elif transition_data:
                for rgb in self.led_controller.transition(transition_data.get("red"), transition_data.get("green"), transition_data.get("blue"), transition_data.get("steps", 255)):
                    self.run_modify(step.get("modify", {}), {**replace_vars, "r":rgb[0], "g": rgb[1], "b": rgb[2]})
                    if not self.clever_sleep(self.wait_time if step["sleep"] == "wait_time" else step["sleep"]): return
        else:
            self.run_modify(step.get("modify", {}), replace_vars)
            if not self.clever_sleep(step["sleep"]): return

    def run_modify(self, modify, replace_vars):
        for color, calc in modify.items():
            setattr(self.led_controller, color, ne_eval(calc, local_dict={var_name:var_value if not callable(var_value) else var_value() for var_name, var_value in replace_vars.items()}))

    def clever_sleep(self, val: float):
        PIALARM_RUNNING = environ.get("PIALARM_RUNNING", "True")
        if PIALARM_RUNNING == "False":
            self.led_controller.reset()
            return False
        else:
            try:
                if val > CLEVER_SLEEP_SECS_SEGMENTS: 
                    time_sleep(CLEVER_SLEEP_SECS_SEGMENTS)
                    return self.clever_sleep(val-CLEVER_SLEEP_SECS_SEGMENTS)
                else: time_sleep(val)
                return True
            except KeyboardInterrupt:
                self.led_controller.reset()
                return False