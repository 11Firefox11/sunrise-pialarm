from secrets import token_urlsafe as secrets_token_urlsafe
from hashlib import sha1
from environment_variables import PASSCODES_JSON_PATH

passcodes_file = open(PASSCODES_JSON_PATH, "w")
passcodes_file.write("[")
hashes_generated = []
for day_num in range(31):
    passcode_raw = secrets_token_urlsafe(4)
    while (passcode_hashed:=sha1(passcode_raw.encode()).hexdigest()) in hashes_generated: passcode_raw = secrets_token_urlsafe(4)
    hashes_generated.append(passcode_hashed)
    passcodes_file.write(f"\"{passcode_hashed}\"{',' if day_num != 30 else ''}")
    print(f"{str(day_num+1).zfill(2)} | {passcode_raw}", end="")
    input()
passcodes_file.write("]")