# Internal
from datetime import datetime

from FootballPredictionsBot.models.fixture import Fixture
from FootballPredictionsBot.utils import env


class DataLoader:
    """Provides methods for bulk loading data from FootballAPI into the database and SQLAlchemy cache.

    Attributes:
        countries (list): The countries which we want to get data for.
        seasons (list): The seasons which we want to get data for.
        use_backup (bool): Will retrieve API data from the backup files if True, else from API-Football API.
        data_interface (DataInterface): A DataInterface instance.
        football_api (FootballAPI): A FootballAPI instance.
    """

    def __init__(self, data_interface, football_api):
        self.countries = env.get_cfg("API_FOOTBALL_COUNTRIES")
        self.seasons = env.get_cfg("API_FOOTBALL_SEASONS")
        self.use_backup = env.get_arg("use_backup")
        self.data_interface = data_interface
        self.football_api = football_api
        self.last_refresh_times = {"leagues": None, "fixtures": None, "teams": None, "team_leagues": None}

    def load_all(self):
        """Refreshes all data in the database.

        Raises:
            Exception: Usually APIError, if there was any problems in refreshing the data.
        """

        try:
            env.log.info(f"Remaining API calls before the refresh: {self.get_remaining_api_calls()}")
            self.populate_leagues()
            self.populate_fixtures()
            self.populate_teams()
            self.link_teams()
            env.log.info(f"Remaining API calls after the refresh: {self.get_remaining_api_calls()}")
        except Exception as e:
            if env.get_arg("ignore_refresh_failures"):
                env.log.warning("Failed to refresh data but carrying on as --ignore_refresh_failures is set")
            else:
                raise e

    def populate_leagues(self):
        """Refreshes all League entities in the database."""

        env.log.info("Performing a refresh of the leagues")
        for league in self.football_api.get_leagues(self.countries, self.seasons, use_backup=self.use_backup):
            self.data_interface.add_or_update(league)
        self.last_refresh_times["leagues"] = datetime.now()

    def populate_fixtures(self):
        """Refreshes all Fixture entities in the database."""

        env.log.info("Performing a refresh of the fixtures")
        for league in self.data_interface.get_current_leagues():
            for fixture in self.football_api.get_fixtures_by_league(league.id, use_backup=self.use_backup):
                self.data_interface.add_or_update(fixture)
        self.last_refresh_times["fixtures"] = datetime.now()

    def populate_teams(self):
        """Refreshes all Team entities in the database."""

        env.log.info("Performing a refresh of the teams")
        for league in self.data_interface.get_current_leagues():
            for team in self.football_api.get_teams_by_league(league.id, use_backup=self.use_backup):
                self.data_interface.add_or_update(team)
        self.last_refresh_times["teams"] = datetime.now()

    def link_teams(self):
        """Refreshes the relationship between Team entities and League entities in the database."""

        env.log.info("Performing a relationship update for teams <-> leagues")
        leagues = {}

        for fixture in self.data_interface.get_all(Fixture):
            teams = {fixture.home_team, fixture.away_team}
            leagues.setdefault(fixture.league, set()).update(teams)

        for league, teams in leagues.items():
            for team in teams:
                self.data_interface.add_team_to_league(team, league)
        self.last_refresh_times["team_leagues"] = datetime.now()

    # Internal protected methods #

    def get_remaining_api_calls(self):
        """Gets the number of API calls remaining for the bot account.

        Returns:
            int: The number of API calls remaining for the bot account.
        """

        status = self.football_api.get_status()
        remaining_api_calls = status["requests_limit_day"] - status["requests"]
        return remaining_api_calls
