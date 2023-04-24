from led_controller import LedController
from time import sleep as time_sleep
from os import environ
from json import load
from jsonschema import validate as json_validate
from jsonschema.exceptions import ValidationError
from environment_variables import ALARM_JSONSCHEMA

class AlarmRunner:
    def __init__(self, config_path="alarm.json"):
        self.config_path = config_path
        self.parsed_config = load(open(self.config_path, "r", encoding="UTF-8"))
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

    @staticmethod
    def clever_sleep(val: float):
        PIALARM_RUNNING = environ.get("PIALARM_RUNNING", "False")
        if PIALARM_RUNNING == "False":
            LedController()
            return False
        else:
            if val > 2: 
                time_sleep(2)
                return AlarmRunner.clever_sleep(val-2)
            else: time_sleep(val)
            return True