# Sunrise Pialarm
Python alarm running on a Raspberry Pi which controls a LED strip. An alarm clock that is not like any, it imitates the sunrise.

It has a simple web interface where the alarm time can be set, for this purpose the web server only turns on in a specified time period. The web interface turns back on before the alarm goes off, so it can be turned off without waiting. The alarm time indicates when the sunrise is at its brightest, yellow phase. To turn off the alarm a code is required which is different for each day of the month. The light goes off, the web server goes off again.

# Documentation
## Python related
It works with Python 3, install the dependencies from the `requirements.txt`.

## Configuration
### Environment variables
There are some basic settings in `environment_variables.py`
| Name | Type | Description |
| --- | --- | --- |
| `DEV_MODE` | `bool` | If it is on, then a `PySimpleGUI` window will serve as the LED instead of changing the actual PI's state (with `pigpio`). |
| `CODES_JSON_PATH` | `str` | Where the [codes](#codes) are held for each month day. |
| `ALARM_JSON_PATH` | `str` | Where the [main alarm/sunrise config](#sunrise-settings) is at. |
| `SETTINGS_JSON_PATH` | `str` | The [alarm time and web server settings](#alarm-and-web-server-settings) file path. |
| `RGB_PINS` | `dict` | The GPIO pin number for each color: `red`, `green`, `blue`. |
| `CLEVER_SLEEP_SECS_SEGMENTS` | `int` | How frequently the alarm will check if it has been turned off. |

### Codes
Before starting make sure to run `generate_codes.py`. This will write out the codes for each day. These are shown once, then they are hashed. Write these down in order to stop the alarm later. 31 codes are generated, meaning the codes are same for each month. (The hashed codes will be at `CODES_JSON_PATH`.)

### Sunrise settings
There is a basic alarm included in the repository ([`alarm.json`](alarm.json)). Which is a sunrise that is about 15 minutes long. Feel free to use this, or you can create your own one with the easy methods I made.

The JSON must be an object. It operates with steps. It has 3 settings:
- `wait_time`: This is the default wait time in seconds, it is like a variable that can be reused. This is required.
- `when_yellow`: When will the alarm turn yellow, meaning the sun came up fully. It is necessary because, based on this, the light will be completely yellow at the set alarm time. The sunrise will start at `alarm_at - when_yellow`. It is in seconds. This is required.
- `repeat_last`: A number to repeat last X steps. Not required.  

Steps change the light, the code will execute step after step. It is an array. There are two actions: `range` and `transition` each iterate and change the rgb colors based on the `modify`. Properties of a `step`:
- `sleep`: How much time should the step wait, or should it wait (if `range` or `transtion` is defined) after each modify related iteration. Can be any number or `"wait_time"`. This is required. (Note: a simple wait step can be created too.)
- `range`: `start`, `stop`, `step` these 3 properties can be set (integers), it is a [Python range](https://docs.python.org/3/library/functions.html#func-range) in a for loop where each iteration the `modify` is run.
- `transition`: To calculate the transition to a color. `red`, `green`, `blue` can be set (integers).
- `modify`: What will be modified at this step or (if `range` or `transtion` is defined) at each iteration. Any arithmetic calculation can be used (parentheses too). Few built in variables can be used:
  - `red`, `green` or `blue` to get the current color values.
  - If it is running in a `range`, then use `i` to get the current iteration's number.
  - If it is running in a `transition`, then `r` `g` `b` can be used to get the transition related values.

### Alarm and web server settings
Make sure you restart the app after editing `server_state` settings. The alarm will be scheduled after the web server goes off.
- `alarm_at`: When the alarm will go off, the web interface will change this.
- `server_state`:
  - `turn_on_at`: When the web server should turn on at, so the alarm time can be set. It is in `HH:MM` format.
  - `turn_off_at`: When the web server should turn off at, so the alarm can be scheduled. It is in `HH:MM` format.
  - `turn_on_before_alarm`: How many seconds before the sunrise start the web server should turn on, so it can be turned off before the alarm goes off. It is a number.

# Contributions
Any contribution is welcome. I made this for myself. No updates will come till someone requests it, or I need another feature // I discover something.