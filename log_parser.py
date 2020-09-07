import re


class LogParser(object):
    def __init__(self, log_contents):
        self.log_contents = log_contents

        self.TIMESTAMP_REGEX = r'^[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}: '
        self.patterns = [
            r'\[StateMatchmaking] Begin matchmaking',
            r'\[ClientGameManager\] .+\. ([0-9]+) players in system.',
            r'\[StateGameInProgress\] Storing ticket for admission to stage [0-9]+ of episode ([a-z0-9\-]+)',
            r'== \[CompletedEpisodeDto\] ==',
            r'^\[Round [0-9]{1} \| (\S+)\]'
        ]

        self.timestamp_pattern = re.compile(self.TIMESTAMP_REGEX)

        self.begin_matchmaking_pattern = re.compile(
            self.TIMESTAMP_REGEX + r'\[StateMatchmaking] Begin matchmaking'
        )

        self.num_players_pattern = re.compile(
            self.TIMESTAMP_REGEX + r'\[ClientGameManager\] .+\. ([0-9]+) players in system.'
        )

        self.round_over_pattern = re.compile(
            self.TIMESTAMP_REGEX + r'\[StateGameInProgress\] Storing ticket for admission to stage [0-9]+ of episode ([a-z0-9\-]+)'
        )

        self.episode_over_pattern = re.compile(
            self.TIMESTAMP_REGEX + r'== \[CompletedEpisodeDto\] =='
        )

        self.round_info_pattern = re.compile(r'^\[Round [0-9]{1} \| (\S+)\]')

        self.round_stat_pattern = re.compile(r'^> ([^:]+): (.+)$')

    def parse(self):
        for line in self.log_contents:
            if self.begin_matchmaking_pattern.match(line) is not None:
                yield self.parse_episode_info()

    def get_round_info(self):
        minigames = []
        positions = []

        for line in self.log_contents:
            # If we see a timestamp, we're done with end-of-episode info
            if self.timestamp_pattern.match(line):
                break

            round_info_match = self.round_info_pattern.match(line)
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

                    elif self.timestamp_pattern.match(line):
                        break

                    else:
                        just_saw_blank = False

                        round_stat_match = self.round_stat_pattern.match(line)
                        if round_stat_match:
                            stat = round_stat_match.group(1)
                            if stat == 'Qualified':
                                qualified = True if round_stat_match.group(2) == 'True' else False
                            elif stat == 'Position' and qualified:
                                positions.append(round_stat_match.group(2))

        return {
            'minigames': minigames,
            'positions': positions,
            'victory': len(positions) == len(minigames)
        }

    def parse_episode_info(self):
        num_players = episode_id = None
        round_qualifiers = []

        for line in self.log_contents:
            # Try to get a number of qualifying players out of this line
            match = self.num_players_pattern.match(line)
            if match:
                num_players = int(match.group(1))

                continue

            # Check to see if the round ended
            match = self.round_over_pattern.match(line)
            if match:
                if not episode_id and match.group(1):
                    episode_id = match.group(1)

                if num_players is not None:
                    round_qualifiers.append(num_players)

                num_players = None

                continue

            # Try to get end-of-episode information
            match = self.episode_over_pattern.match(line)
            if match:
                if num_players:
                    round_qualifiers.append(num_players)

                return {
                    'episode_id': episode_id,
                    'round_qualifiers': round_qualifiers,
                    **self.get_round_info()
                }
