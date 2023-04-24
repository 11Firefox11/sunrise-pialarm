from led_controller import LedController
from time import sleep as time_sleep
from os import environ
from json import load
from jsonschema import validate as json_validate
from jsonschema.exceptions import ValidationError
from environment_variables import ALARM_JSONSCHEMA, CLEVER_SLEEP_SECS_SEGMENTS
from numexpr import evaluate as ne_eval

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
            if (range_data:=step.get("range")) or (transition_data:=step.get("transition")):
                if range_data:
                    for i in range(range_data.get("start", 0), range_data.get("stop", 10), range_data.get("step", 1)):
                        self.run_modify(step.get("modify", {}), {**replace_vars, "i":i})
                        if not self.clever_sleep(self.wait_time if step["sleep"] == "wait_time" else step["sleep"]): return
                elif transition_data:
                    for rgb in self.led_controller.transition(transition_data.get("red"), transition_data.get("green"), transition_data.get("blue")):
                        self.run_modify(step.get("modify", {}), {**replace_vars, "r":rgb[0], "g": rgb[1], "b": rgb[2]})
                        if not self.clever_sleep(self.wait_time if step["sleep"] == "wait_time" else step["sleep"]): return
            else:
                self.clever_sleep(step["sleep"])

    def run_modify(self, modify, replace_vars):
        for color, calc in modify.items():
            setattr(self.led_controller, color, ne_eval(calc, local_dict={var_name:var_value if not callable(var_value) else var_value() for var_name, var_value in replace_vars.items()}))

    def clever_sleep(self, val: float):
        PIALARM_RUNNING = environ.get("PIALARM_RUNNING", "True")
        if PIALARM_RUNNING == "False":
            self.led_controller.reset()
            return False
        else:
            if val > CLEVER_SLEEP_SECS_SEGMENTS: 
                time_sleep(CLEVER_SLEEP_SECS_SEGMENTS)
                return self.clever_sleep(val-CLEVER_SLEEP_SECS_SEGMENTS)
            else: time_sleep(val)
            return True