from json import dumps
from multiprocessing import Queue
import os
from requests import post
from requests.exceptions import RequestException
from time import sleep

from log_parser import LogParser
from file_system import (
    add_path_to_registry_startup_key,
    follow_file,
    get_fall_guys_log_location,
    get_steam_user_info,
)


# TODO: Need to handle for internet errors so that program doesn't go down
def main():
    add_path_to_registry_startup_key(os.getenv('LOCALAPPDATA') + r'\FGStats_Client\fgstats_client.exe' )

    STEAM_ID, STEAM_ACCOUNT_NAME = get_steam_user_info()

    while True:
        for episode in LogParser(follow_file(get_fall_guys_log_location())).parse():
            while True:
                try:
                    post(
                        'https://api.fgstats.com/client',
                        data=dumps({
                            'steam_id': STEAM_ID,
                            'steam_account_name': STEAM_ACCOUNT_NAME,
                            'episode_info': episode,
                        })
                    )

                    break

                # Don't error if connection issue
                except RequestException:
                    sleep(30)
                    continue


if __name__ == "__main__":
    main()
