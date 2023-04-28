from colour import Color
from environment_variables import RGB_PINS, DEV_MODE
from math import floor
if not DEV_MODE: from pigpio import pi 
if DEV_MODE: 
    import PySimpleGUI as sg
    from threading import Thread

def rgb_value_checker(func):
    def wrapper(self, val):
        if val < 0: val = 0
        elif val > 255: val = 255
        elif type(val) == float:
            val = round(val)
        return func(self, val)
    return wrapper

class LedController:
    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        self._r = self._g = self._b = 0
        self.pi = pi() if not DEV_MODE else None
        if DEV_MODE:
            def gui_thread():
                try:
                    window = sg.Window("Sunrise Pi Alarm Development", [[]], grab_anywhere=True, resizable=True, size=(100, 100))
                    while True:
                        event, values = window.Read(timeout=10)
                        window.TKroot.configure(background="#{:02x}{:02x}{:02x}".format(self.red, self.green, self.blue))
                        if event == sg.WIN_CLOSED:
                            break
                    window.Close()
                except Exception as x:
                    window.Close()
            gui_thread = Thread(target=gui_thread, daemon=True)
            gui_thread.start()
        self.red = r
        self.green = g
        self.blue = b

    def reset(self): self.red = self.green = self.blue = 0

    def transition(self, r=None, g=None, b=None, steps=255):
        if not r: r = self.red
        if not g: g = self.green
        if not b: b = self.blue
        t = Color(rgb=(self.red/255, self.green/255, self.blue/255)).range_to(Color(rgb=(r/255, g/255, b/255)), steps)
        toReturn = []
        for c in t:
            if c not in toReturn: toReturn.append(c)
        return [[255*c.red, 255*c.green, 255*c.blue] for c in toReturn]

    @property
    def red(self): return self._r

    @red.setter
    @rgb_value_checker
    def red(self, val):
        self._r = floor(val)
        if not DEV_MODE: self.pi.set_PWM_dutycycle(RGB_PINS["red"], self._r)

    @property
    def green(self): return self._g

    @green.setter
    @rgb_value_checker
    def green(self, val):
        self._g = floor(val)
        if not DEV_MODE: self.pi.set_PWM_dutycycle(RGB_PINS["green"], self._g)

    @property
    def blue(self): return self._b

    @blue.setter
    @rgb_value_checker
    def blue(self, val):
        self._b = floor(val)
        if not DEV_MODE: self.pi.set_PWM_dutycycle(RGB_PINS["blue"], self._b)