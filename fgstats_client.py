from json import dumps
from multiprocessing import Queue
import pathlib
from requests import post

from log_parser import LogParser
from file_system import (
    add_path_to_registry_startup_key,
    follow_file,
    get_fall_guys_log_location,
    get_steam_user_info,
)


# TODO: Need to handle for internet errors so that program doesn't go down
def main():
    # TODO: Check if windows registry contains this script already. If it doesn't, add it.
    add_path_to_registry_startup_key(str(pathlib.Path(__file__).parent.absolute()) + r'\fgstats_client.exe' )

    STEAM_ID, STEAM_ACCOUNT_NAME = get_steam_user_info()

    while True:
        for episode in LogParser(follow_file(get_fall_guys_log_location())).parse():
            post(
                # TODO: When we get a non-self-signed cert, use HTTPS
                'http://flask-env.eba-mwwfrvk5.us-east-1.elasticbeanstalk.com/client',
                data=dumps({
                    'steam_id': STEAM_ID,
                    'steam_account_name': STEAM_ACCOUNT_NAME,
                    'episode_info': episode,
                })
            )


if __name__ == "__main__":
    main()
