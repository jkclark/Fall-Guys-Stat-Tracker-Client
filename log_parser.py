from datetime import datetime
import re


class LogParser(object):
    def __init__(self, log_contents):
        self.log_contents = log_contents

        self.regexes = {
            'timestamp': r'^([0-9]{2}:[0-9]{2}:[0-9]{2})\.[0-9]{3}: ',
            'matchmaking': r'\[StateMatchmaking] Begin matchmaking',
            'num_players': r'\[ClientGameManager\] .+\. ([0-9]+) players in system.',
            'round_over': r'\[StateGameInProgress\] .+ admission to stage [0-9]+ of episode ([a-z0-9\-]+)',
            'episode_over': r'== \[CompletedEpisodeDto\] ==',
            'round_info': r'^\[Round [0-9]{1} \| (\S+)\]',
            'round_stat': r'^> ([^:]+): (.+)$'
        }

        # These regexes always appear with timestamps at the beginning of the line
        self.regexes_with_timestamp_prefix = {'matchmaking', 'num_players', 'round_over', 'episode_over'}

        self.patterns = {
            name: re.compile(regex)
            if name not in self.regexes_with_timestamp_prefix
            else re.compile(self.regexes['timestamp'] + regex)
            for name, regex in self.regexes.items()
        }

    def parse(self):
        for line in self.log_contents:
            if self.patterns['matchmaking'].match(line) is not None:
                yield self.parse_episode_info()

    def parse_episode_info(self):
        num_players = episode_id = None
        round_qualifiers = []
        round_end_times = []

        for line in self.log_contents:
            # Try to get a number of qualifying players out of this line
            match = self.patterns['num_players'].match(line)
            if match:
                num_players = int(match.group(2))

                continue

            # Check to see if the round ended
            match = self.patterns['round_over'].match(line)
            if match:
                round_end_times.append(' '.join((datetime.now().strftime('%Y-%m-%d'), match.group(1))))

                if not episode_id and match.group(2):
                    episode_id = match.group(2)

                if num_players is not None:
                    round_qualifiers.append(num_players)

                num_players = None

                continue

            # Try to get end-of-episode information
            match = self.patterns['episode_over'].match(line)
            if match:
                if num_players:
                    round_qualifiers.append(num_players)

                # If you get eliminated before a round actually ends, append the current date/time
                if len(round_qualifiers) > len(round_end_times):
                    round_end_times.append(' '.join((datetime.now().strftime('%Y-%m-%d'), match.group(1))))

                return {
                    'episode_id': episode_id,
                    'round_qualifiers': round_qualifiers,
                    'round_end_times': round_end_times,
                    **self.get_round_info()
                }

    def get_round_info(self):
        minigames = []
        positions = []

        for line in self.log_contents:
            # If we see a timestamp, we're done with end-of-episode info
            if self.patterns['timestamp'].match(line):
                break

            round_info_match = self.patterns['round_info'].match(line)
            if round_info_match:
                minigames.append(round_info_match.group(1))
                qualified = None

                # Get info about this round
                just_saw_blank = False
                for line in self.log_contents:
                    # If we see two blank lines in a row, we're done with this round
                    if line == '\n':
                        if just_saw_blank:
                            break
                        just_saw_blank = True

                    elif self.patterns['timestamp'].match(line):
                        break

                    else:
                        just_saw_blank = False

                        round_stat_match = self.patterns['round_stat'].match(line)
                        if round_stat_match:
                            stat = round_stat_match.group(1)
                            if stat == 'Qualified':
                                qualified = True if round_stat_match.group(2) == 'True' else False
                            elif stat == 'Position' and qualified:
                                positions.append(int(round_stat_match.group(2)))

        return {
            'minigames': minigames,
            'positions': positions,
            'victory': len(positions) == len(minigames)
        }
