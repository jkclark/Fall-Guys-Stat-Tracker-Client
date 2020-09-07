from json import dumps
from requests import post

from log_parser import LogParser
from file_system import follow_file, get_fall_guys_log_location, get_steam_id


def main():
    STEAM_ID = get_steam_id()

    with open(get_fall_guys_log_location(), 'r') as log_file:
        print('*****')
        for episode in LogParser(follow_file(log_file)).parse():
            #  for field in episode:
                #  print(f'{field}: {episode[field]}')
            #  print('*****')

            post(
                'http://localhost:5000/client/',
                data=dumps({'steam_id': STEAM_ID, 'episode_info': episode})
            )


if __name__ == "__main__":
    main()
