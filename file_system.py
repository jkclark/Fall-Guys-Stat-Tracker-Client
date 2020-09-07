import os
from pathlib import Path
import sys
import time
from typing import Generator
import vdf
import winreg


def _get_num_system_bits():
    if sys.maxsize == 2_147_483_647:
        return 32
    return 64


def _get_steam_install_location():
    if _get_num_system_bits() == 32:
        KEY_NAME = r'SOFTWARE\Valve\Steam'
    else:
        KEY_NAME = r'SOFTWARE\WOW6432Node\Valve\Steam'

    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, KEY_NAME)
    value, _ = winreg.QueryValueEx(registry_key, 'InstallPath')
    winreg.CloseKey(registry_key)
    return value


def get_steam_id():
    with open(os.path.join(_get_steam_install_location(), r'config\loginusers.vdf'), 'r') as logins_file:
        logins = vdf.loads(logins_file.read())

    # Return the first user's ID
    for user in logins['users']:
        return user


def get_fall_guys_log_location() -> str:
    return os.path.join(Path.home(), 'AppData', 'LocalLow', 'Mediatonic', 'FallGuys_client', 'Player.log')


def follow_file(f) -> Generator[str, None, None]:
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.1)
            continue

        yield line
