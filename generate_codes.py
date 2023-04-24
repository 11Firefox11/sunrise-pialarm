from datetime import datetime, timedelta
from secrets import token_urlsafe as secrets_token_urlsafe
from hashlib import sha1
from json import dumps as json_dumps
from environment_variables import CODES_JSON_PATH

codes_file = open(CODES_JSON_PATH, "w+")
codes_file.write("[")
hashes_generated = []
for day_num in range(1, 32):
    code_raw = secrets_token_urlsafe(4)
    while (code_hashed:=sha1(code_raw.encode()).hexdigest()) in hashes_generated: 
        code_raw = secrets_token_urlsafe(4)
    hashes_generated.append(code_hashed)
    codes_file.write(f"{json_dumps(code_hashed)}{',' if day_num != 31 else ''}")
    print(f"{str(day_num).zfill(2)} | {code_raw}", end="")
    input()
codes_file.write("]")