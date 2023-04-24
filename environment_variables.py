DEV_MODE = True
CODES_JSON_PATH = "codes.json"
ALARM_JSON_PATH = "alarm.json"
SETTINGS_JSON_PATH = "settings.json"
RGB_PINS = {"red": 17, "green": 22, "blue": 24}
ALARM_MODIFY_REGEX_PATTERN = "^(\(|\)|\d+\.\d+|\d+|red|blue|green|[+\-*/%]|i|\s)*$"
CLEVER_SLEEP_SECS_SEGMENTS = 1
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
                        "blue": { "type": "number" }
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