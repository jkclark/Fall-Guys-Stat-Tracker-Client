import os
from pathlib import Path
import re
import time


TIMESTAMP_REGEX = r'^[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}: '

timestamp_pattern = re.compile(TIMESTAMP_REGEX)

begin_matchmaking_pattern = re.compile(
    TIMESTAMP_REGEX + r'\[StateMatchmaking] Begin matchmaking'
)

num_players_pattern = re.compile(
    TIMESTAMP_REGEX + r'\[ClientGameManager\] .+\. ([0-9]+) players in system.'
)

round_over_pattern = re.compile(
    TIMESTAMP_REGEX + r'\[StateGameInProgress\] Storing ticket for admission to stage [0-9]+ of episode ([a-z0-9\-]+)'
)

episode_over_pattern = re.compile(
    TIMESTAMP_REGEX + r'== \[CompletedEpisodeDto\] =='
)

round_info_pattern = re.compile(r'^\[Round [0-9]{1} \| (\S+)\]')


def get_fall_guys_log_location():
    return os.path.join(Path.home(), 'AppData', 'LocalLow', 'Mediatonic', 'FallGuys_client', 'Player.log')


def follow_file(f):
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.1)
            continue

        yield line


def get_episode_round_names(log_contents):
    round_names = []

    for line in log_contents:
        if timestamp_pattern.match(line):
            break

        round_info_match = round_info_pattern.match(line)
        if round_info_match:
            round_names.append(round_info_match.group(1))

    return round_names


def parse_episode_info(log_contents):
    num_players = episode_id = None
    round_qualifiers = []

    for line in log_contents:
        # Try to get a number of qualifying players out of this line
        match = num_players_pattern.match(line)
        if match:
            num_players = int(match.group(1))

            continue

        # Check to see if the round ended
        match = round_over_pattern.match(line)
        if match:
            if not episode_id and match.group(1):
                episode_id = match.group(1)

            if num_players is not None:
                round_qualifiers.append(num_players)

            num_players = None

            continue

        # Try to get end-of-episode information
        match = episode_over_pattern.match(line)
        if match:
            if num_players:
                round_qualifiers.append(num_players)

            round_names = get_episode_round_names(log_contents)

            return {
                'episode_id':       episode_id,
                'round_names':      round_names,
                'round_qualifiers': round_qualifiers
            }


def parse_player_log():
    with open(get_fall_guys_log_location(), 'r') as log_file:
        log_contents = follow_file(log_file)
        for line in log_contents:
            if begin_matchmaking_pattern.match(line) is not None:
                yield parse_episode_info(log_contents)


if __name__ == "__main__":
    for episode in parse_player_log():
        print("**********")
        for field in episode:
            print(f'{field}: {episode[field]}')
        print("**********")

'''
    def thingy(s):
        try:
            return int(s[:s.find(':')])
        except ValueError:
            return -999999999

    with open('./player_lines.txt', 'r') as f:
        for l in sorted(f.readlines(), key=thingy):
            print(l)
'''
