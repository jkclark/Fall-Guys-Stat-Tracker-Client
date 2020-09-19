from json import dumps
from requests import post

from log_parser import LogParser
from file_system import follow_file, get_fall_guys_log_location, get_steam_user_info


def main():
    STEAM_ID, STEAM_ACCOUNT_NAME = get_steam_user_info()

    while True:
        for episode in LogParser(follow_file(get_fall_guys_log_location())).parse():
            print('****')
            for x in episode:
                print(f'{x}: {episode[x]}')
            print('****')
            #  post(
                #  #  'https://flask-env-2.eba-mwwfrvk5.us-east-1.elasticbeanstalk.com/client/',
                #  'http://localhost:5000/client/',
                #  data=dumps({
                    #  'steam_id': STEAM_ID,
                    #  'steam_account_name': STEAM_ACCOUNT_NAME,
                    #  'episode_info': episode,
                #  })
            #  )


if __name__ == "__main__":
    main()
