import os
import sys
import vdf
import winreg


def get_num_system_bits():
    if sys.maxsize == 2_147_483_647:
        return 32
    return 64


def get_steam_installation_location():
    if get_num_system_bits() == 32:
        KEY_NAME = r'SOFTWARE\Valve\Steam'
    else:
        KEY_NAME = r'SOFTWARE\WOW6432Node\Valve\Steam'

    registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, KEY_NAME)
    value, _ = winreg.QueryValueEx(registry_key, 'InstallPath')
    winreg.CloseKey(registry_key)
    return value


def get_steam_account_name():
    with open(os.path.join(get_steam_installation_location(), r'config\loginusers.vdf'), 'r') as logins_file:
        logins = vdf.loads(logins_file.read())

    # Return the first user's account name
    for user in logins['users']:
        return logins['users'][user]['AccountName']
