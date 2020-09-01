#  import os
import sys
import winreg


def get_num_system_bits():
    if sys.maxsize == 2_147_483_647:
        return 32
    elif sys.maxsize == 9_223_372_036_854_775_807:
        return 64
    else:
        assert False, 'System is neither 32bit nor 64-bit.'


def get_steam_installation_folder():
    NUM_SYSTEM_BITS = get_num_system_bits()
    if NUM_SYSTEM_BITS == 32:
        KEY_NAME = r'HKEY_LOCAL_MACHINE\SOFTWARE\Valve\Steam'
    else:
        KEY_NAME = r'HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Valve\Steam'

    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_NAME, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, 'InstallPath')
        winreg.closeKey(registry_key)
    except WindowsError:
        return ''


def get_steam_username():
    print('Steam installation:', get_steam_installation_folder())
