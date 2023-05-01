from werkzeug.serving import make_server
from datetime import datetime, timedelta
from time import sleep
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from flask import render_template, request, jsonify
from threading import Thread
from os import environ, path

from environment_variables import PASSCODES_JSON_PATH, ALARM_JSON_PATH, SETTINGS_JSON_PATH, WEB_SERVER_IP, WEB_SERVER_PORT
from settings_manager import SettingsManager
from alarm_runner import AlarmRunner

class flaskManager:

    def __init__(self) -> None:
        self.alarm_schedule = None
        environ["PIALARM_RUNNING"] = "False"

    def start(self, night=False):
        global manager, settings, app
        if night:
            create_scheduler(manager.stop, settings.turn_off_at[0], [True])
        else:
            environ["PIALARM_RUNNING"] = "True"
        start_server()

    def stop(self, night=False):
        global settings, alarm
        stop_server()
        if night:
            settings.load_config()
            self.alarm_schedule = create_scheduler(alarm.start, settings.realalarm_at)
            create_scheduler(self.start, settings.turn_on_at[1])
        else:
            create_scheduler(self.start, settings.turn_on_at[0], [True])


class ServerThread(Thread):

    def __init__(self, app):
        Thread.__init__(self)
        self.server = make_server(WEB_SERVER_IP, WEB_SERVER_PORT, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


def start_server():
    global server
    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    def main_get():
        global alarm
        return render_template(("waiting" if not environ["PIALARM_RUNNING"] == "True" else "running") + ".html", alarm_at=settings.time_list_to_str(settings.alarm_at))

    @app.route("/", methods=["POST"])
    def main_post():
        global settings, manager, alarm
        data = dict(request.json)
        if not data or (environ["PIALARM_RUNNING"] == "False" and "alarm_at" not in data) or (environ["PIALARM_RUNNING"] == "True" and "code" not in data):
            return jsonify({"status": False})
        if environ["PIALARM_RUNNING"] == "True":
            if not settings.stop_alarm(data["code"]):
                return jsonify({"status": False})
            environ["PIALARM_RUNNING"] = "False"
            manager.alarm_schedule.shutdown(wait=False)
            to_stop_at = datetime.now() + timedelta(seconds=1)
            create_scheduler(manager.stop, [to_stop_at.hour, to_stop_at.minute, to_stop_at.second])
        else:
            settings.set_alarm(data["alarm_at"])
        return jsonify({"status": True})

    server = ServerThread(app)
    server.start()

def stop_server():
    global server
    server.shutdown()

def create_scheduler(func: callable, timeList: list, args: list = []):
    global settings
    sch = BackgroundScheduler()
    sch.configure()
    now = datetime.now()
    if len(timeList) == 2:
        timeList.append(0)
    to_run_at = datetime(now.year, now.month, now.day, *timeList)
    if settings.time_list_to_secs([now.hour, now.minute, now.second]) > settings.time_list_to_secs([timeList[0], timeList[1], timeList[2]]):
        to_run_at = to_run_at + timedelta(days=1)
    sch.add_job(func, "date", args=args, run_date=to_run_at)
    sch.start()
    return sch


if __name__ == "__main__":
    this_dir = path.dirname(path.realpath(__file__))
    generate_full_path = lambda p: path.join(this_dir, p)
    alarm = AlarmRunner(generate_full_path(ALARM_JSON_PATH))
    settings = SettingsManager(alarm.when_yellow, generate_full_path(PASSCODES_JSON_PATH), generate_full_path(SETTINGS_JSON_PATH))
    manager = flaskManager()
    now = datetime.now()
    now = settings.time_list_to_secs([now.hour, now.minute])
    if ((settings.time_list_to_secs(settings.turn_on_at[0]) < now and now < settings.time_list_to_secs(settings.turn_off_at[0]))):
        manager.start(True)
    else:
        create_scheduler(manager.start, settings.turn_on_at[0], [True])
    while True:
        sleep(5)
