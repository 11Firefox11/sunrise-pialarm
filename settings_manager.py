from pathlib import Path as pathlib_Path
from json import load as json_load
from json import dumps as json_dumps
from datetime import datetime
from hashlib import sha1

class SettingsManager:
    def __init__(self, when_yellow, passcodes_path="codes.json", config_path="settings.json") -> None:
        self.when_yellow = when_yellow
        self.passcodes_path = passcodes_path
        self.config_path = config_path
        self.turn_on_at = []
        self.turn_off_at = []
        self.load_config()

    def load_config(self):
        settings = json_load(open(self.config_path, encoding="UTF-8"))
        for key, val in settings["server_state"].items():
            if type(val) == str: getattr(self, "turn_on_at" if "on" in key else "turn_off_at").append([int(v) for v in val.split(":")])
            else: setattr(self, key, val)
        self.turn_on_at.append([])
        self.alarm_at = settings["alarm_at"]
        self.passcodes = json_load(open(self.passcodes_path, encoding="UTF-8"))

    def set_alarm(self, listTime: list):
        self.alarm_at = listTime
        with open(self.config_path, "w") as f: f.write(self.json)

    def stop_alarm(self, passcode: str): return sha1(passcode.encode()).hexdigest() == self.today_passcode

    @property
    def today_passcode(self): return self.passcodes[datetime.now().day-1]

    @property
    def alarm_at(self): return self._alarm_at

    @alarm_at.setter
    def alarm_at(self, val: str):
        self._alarm_at = [int(v) for v in val.split(":")]
        self.turn_on_at[1] = self.extract_secs_from_time_list(self.alarm_at, self.turn_on_before_alarm + self.when_yellow)

    @property
    def realalarm_at(self):
        return self.extract_secs_from_time_list(self.alarm_at, self.when_yellow)

    def extract_secs_from_time_list(self, t: list, secs: int):
        s = self.time_list_to_secs(t) - secs
        h = s//(60*60)
        s = s - h*60*60
        return [int(h), int(s//60), int(round(s%60))]

    @staticmethod
    def time_list_to_secs(t: list) -> float: return t[0]*60*60 + t[1]*60 + (0 if len(t) == 2 else t[2])

    @staticmethod
    def list_time_to_str(l: list):
        extendInt = lambda n :  ("0" if n < 10 else "") + str(n)
        return f"{extendInt(l[0])}:{extendInt(l[1])}"

    @property
    def json(self):
        return json_dumps({"alarm_at": self.list_time_to_str(self.alarm_at), "server_state": {"turn_on_at": self.list_time_to_str(self.turn_on_at[0]), "turn_off_at": self.list_time_to_str(self.turn_off_at[0]), "turn_on_before_alarm": self.turn_on_before_alarm}})
