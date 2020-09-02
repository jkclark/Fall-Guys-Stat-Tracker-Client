import os
from pathlib import Path
import re
import time


def get_fall_guys_log_location():
    return os.path.join(Path.home(), 'AppData', 'LocalLow', 'Mediatonic', 'FallGuys_client', 'Player.log')


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
    num_qualifying_pattern = re.compile(
        TIMESTAMP_REGEX + r'\[ClientGameSession\] NumPlayersAchievingObjective=([0-9]+)'
    )
    episode_over_pattern = re.compile(
        TIMESTAMP_REGEX + r'== \[CompletedEpisodeDto\] =='
    )
    round_info_pattern = re.compile(r'^\[Round [0-9]{1} \| (\S+)\]')

    round_qualifiers = []
    qualified_currently = 0

    with open(get_fall_guys_log_location(), 'r') as log_file:
        log_contents = follow_file(log_file)
        for line in log_contents:

            # Try to get a number of qualifying players out of this line
            match = num_qualifying_pattern.match(line)
            if match:
                prev_qualified = qualified_currently
                qualified_currently = int(match.group(1))

                # NOTE: What if you don't make it to the last round? Will this
                #       condition trigger for the last round you played?
                if qualified_currently < prev_qualified:
                    round_qualifiers.append(prev_qualified)

                continue

            # Try to get end-of-episode information
            match = episode_over_pattern.match(line)
            if match:
                round_names = []

                for line in log_contents:
                    if timestamp_pattern.match(line):
                        break

                    round_info_match = round_info_pattern.match(line)
                    if round_info_match:
                        round_names.append(round_info_match.group(1))

                yield {
                    'round_names':      round_names,
                    'round_qualifiers': round_qualifiers
                }

                # Reset for a new episode
                round_qualifiers = []
                qualified_currently = prev_qualified = 0


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
