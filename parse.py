import os
from pathlib import Path
import re
import time


def get_fall_guys_log_location():
    return os.path.join(Path.home(), 'AppData', 'LocalLow', 'Mediatonic', 'FallGuys_client', 'Player.log')
    #  return os.path.join(Path.home(), 'AppData', 'LocalLow', 'Mediatonic', 'FallGuys_client', 'Player-prev.log')


def follow_file(f):
    #  f.seek(0, 2)  # Start at the end of f
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.1)
            continue

        yield line


def parse_player_log():
    print(get_fall_guys_log_location())

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

    in_episode = False
    episode_id = num_players = None
    round_qualifiers = []

    with open(get_fall_guys_log_location(), 'r') as log_file:
        log_contents = follow_file(log_file)
        for line in log_contents:

            # We're not yet in a game, only check if we've started a game
            if not in_episode:
                match = begin_matchmaking_pattern.match(line)
                if match:
                    in_episode = True

            # We're in a game
            else:

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

                    round_names = []

                    for line in log_contents:
                        if timestamp_pattern.match(line):
                            break

                        round_info_match = round_info_pattern.match(line)
                        if round_info_match:
                            round_names.append(round_info_match.group(1))

                    yield {
                        'episode_id':       episode_id,
                        'round_names':      round_names,
                        'round_qualifiers': round_qualifiers
                    }

                    # Reset for a new episode
                    in_episode = False
                    round_qualifiers = []
                    episode_id = num_players = None


if __name__ == "__main__":
    for episode in parse_player_log():
        print("**********")
        print(episode)
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
