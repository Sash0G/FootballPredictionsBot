# External
from datetime import date, timedelta
import json
import os
import requests

# Internal
from FootballPredictionsBot.models.fixture import Fixture
from FootballPredictionsBot.models.league import League
from FootballPredictionsBot.models.team import Team
from FootballPredictionsBot.utils import env
from FootballPredictionsBot.utils.errors import APIError


class FootballAPI:
    """Provides methods for retrieving data from the API-Football API."""

    def __init__(self):
        self.host = env.get_cfg("API_FOOTBALL_HOST")
        self.api_key = env.get_cfg("API_FOOTBALL_API_KEY")
        self.api_backup_dir = env.get_cfg("PATH_BACKUP_API")
        self.endpoints = FootballAPIEndpoints()

    def get_leagues(self, countries, seasons, use_backup=False):
        """Gets all leagues matching the given countries and seasons.

        Args:
            countries (list): A list of countries to filter results on.
            seasons (list): A list of seasons to filter results on.
            use_backup (bool): Get the data from backup files if True, else use API-Football.

        Returns:
            list: A list of League objects matching the criteria.
        """
        if use_backup:
            leagues = self._read_backup("leagues")
        else:
            endpoint = self.endpoints.GET_ALL_LEAGUES
            leagues = self._do(endpoint)
            self._write_backup(leagues, "leagues")

        leagues = [
            League.from_api(league)
            for league in leagues["api"]["leagues"]
            if league["type"] == "League" and league["season"] in seasons and league["country"] in countries
        ]
        return leagues

    def get_fixtures_by_league(self, league_id, use_backup=False):
        """Gets all fixtures for the given league.

        Args:
            league_id (int): The id of the league.
            use_backup (bool): Get the data from backup files if True, else use API-Football.

        Returns:
            list: A list of Fixture objects matching the criteria.
        """

        if use_backup:
            fixtures = self._read_backup(f"fixtures.{league_id}")
        else:
            endpoint = self.endpoints.GET_FIXTURES_BY_LEAGUE.format(league_id=league_id, tz=env.get_cfg("BOT_TIMEZONE"))
            fixtures = self._do(endpoint)
            self._write_backup(fixtures, f"fixtures.{league_id}")

        return [Fixture.from_api(fixture) for fixture in fixtures["api"]["fixtures"]]

    def get_teams_by_league(self, league_id, use_backup=False):
        """Gets all teams for the given league.

        Args:
            league_id (int): The id of the league.
            use_backup (bool): Get the data from backup files if True, else use API-Football.

        Returns:
            list: A list of Team objects matching the criteria.
        """

        if use_backup:
            teams = self._read_backup(f"teams.{league_id}")
        else:
            endpoint = self.endpoints.GET_TEAMS_BY_LEAGUE.format(league_id=league_id)
            teams = self._do(endpoint)
            self._write_backup(teams, f"teams.{league_id}")

        return [Team.from_api(team) for team in teams["api"]["teams"]]

    def get_status(self):
        """Gets the plan status.

        Returns:
            dict: The plan status JSON object as a dict
        """

        endpoint = self.endpoints.GET_STATUS
        status = self._do(endpoint)["api"]["status"]
        return status

    # Internal protected methods #

    def _do(self, endpoint):
        """Performs an HTTP GET request on the given endpoint.

        Args:
            endpoint (str): The endpoint to request.

        Returns:
            dict: JSON data returned from the GET request.
        """

        headers = {"X-RapidAPI-Key": self.api_key}
        url = self.host + endpoint
        env.log.debug(f"GET request to: {url}")

        r = requests.get(url, headers=headers)
        r.raise_for_status()
        resp_json = r.json()

        if "error" in resp_json["api"]:
            raise APIError(resp_json["api"]["error"])

        return resp_json

    def _write_backup(self, data, data_id):
        """Writes a backup of the API response data to a JSON file. Used in the event that the database becomes
        corrupted AND the API is down.

        Args:
            data (dict): Dict representing the JSON to write to the file.
            data_id (str): The type of data and its ID, e.g. leagues, team.123.

        Returns:
            None.
        """

        filename = f'{data_id}.{date.today().strftime("%Y%m%d")}.json'
        filepath = os.path.join(self.api_backup_dir, filename)
        with open(filepath, "w") as f:
            f.write(json.dumps(data, indent=4))

    def _read_backup(self, data_id):
        """Reads a backup file and returns its JSON data as a dict.

        Args:
            data_id (str): The type of data and its ID, e.g. leagues, team.123.

        Returns:
            dict: The backup file's json data.
        """

        today = date.today()
        yesterday = today - timedelta(days=1)
        todays_file = os.path.join(self.api_backup_dir, f'{data_id}.{today.strftime("%Y%m%d")}.json')
        yesterdays_file = os.path.join(self.api_backup_dir, f'{data_id}.{yesterday.strftime("%Y%m%d")}.json')

        if os.path.exists(todays_file):
            with open(todays_file) as f:
                return json.load(f)
        elif os.path.exists(yesterdays_file):
            with open(yesterdays_file) as f:
                return json.load(f)
        else:
            return None


class FootballAPIEndpoints:
    """Static values representing API-Football endpoints."""

    GET_ALL_LEAGUES = "/leagues"
    GET_FIXTURES_BY_LEAGUE = "/fixtures/league/{league_id}?timezone={tz}"
    GET_STATUS = "/status"
    GET_TEAMS_BY_LEAGUE = "/teams/league/{league_id}"
