import re


class LogParser(object):

    """Docstring for LogParser. """

    def __init__(self, log_contents):
        """TODO: to be defined. """
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

    def parse(self):
        for line in self.log_contents:
            if self.begin_matchmaking_pattern.match(line) is not None:
                yield self.parse_episode_info()

    def get_episode_round_names(self):
        minigames = []

        for line in self.log_contents:
            if self.timestamp_pattern.match(line):
                break

            round_info_match = self.round_info_pattern.match(line)
            if round_info_match:
                minigames.append(round_info_match.group(1))

        return minigames

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

                minigames = self.get_episode_round_names()

                return {
                    'episode_id': episode_id,
                    'minigames': minigames,
                    'round_qualifiers': round_qualifiers
                }
