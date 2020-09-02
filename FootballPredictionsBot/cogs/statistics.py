# External
from datetime import datetime
from discord.ext import commands

# Internal
from FootballPredictionsBot.models.league import League
from FootballPredictionsBot.utils import embed_formatter
from FootballPredictionsBot.utils.converters import DateConverter
from FootballPredictionsBot.utils.errors import CommandDataError


class Statistics(commands.Cog):
    """Commands for viewing information about fixtures and results.

    Attributes:
        bot (Bot): The bot instance.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fixtures", help="Get fixtures for a league between the dates provided.")
    async def fixtures(self, ctx, league_id_or_alias, start_date=None, end_date=None):
        """Gets all Fixture entities between the given dates for a given league.

        Args:
            ctx (Context): The bot context.
            league_id_or_alias (str): The ID or alias referencing a League entity.
            start_date (str): The lower bound date.
            end_date (str): The upper bound date.

        Returns:
            None.

        Raises:
            CommandDataError: If no Fixture entities are found.
        """

        start_date, end_date = DateConverter.get_dates(start_date, end_date)
        league = self._get_league(league_id_or_alias)
        fixtures = self.bot.data_interface.get_fixtures_by_league_between_date(league.id, start_date, end_date)
        if len(fixtures) == 0:
            raise CommandDataError(f"No fixtures found between '{start_date}' and '{end_date}' for {league.name}!")

        embed = embed_formatter.generate_fixtures_embed(fixtures)
        embed.title = (
            f"{league.name} fixtures between {start_date.strftime('%d/%m/%Y')} and {end_date.strftime('%d/%m/%Y')}"
        )
        await ctx.send(embed=embed)

    @commands.command(name="leagues", help="Lists all the supported leagues.")
    async def leagues(self, ctx):
        """Gets all League entities.

        Args:
            ctx (Context): The bot context.

        Returns:
            None.
        """

        leagues = self.bot.data_interface.get_current_leagues()
        embed = embed_formatter.generate_leagues_embed(leagues)
        embed.title = "Current leagues"
        await ctx.send(embed=embed)

    @commands.command(name="teams", help="Lists all the supported teams.")
    async def teams(self, ctx):
        """Gets all Team entities.

        Args:
            ctx (Context): The bot context.

        Returns:
            None.
        """

        leagues = self.bot.data_interface.get_current_leagues()
        embed = embed_formatter.generate_teams_embed(leagues)
        embed.title = "Current teams"
        await ctx.send(embed=embed)

    @commands.command(name="upcoming", help="Get the next <limit> fixtures for a given league.")
    async def upcoming(self, ctx, league_id_or_alias, limit=10):
        """Gets the next Fixture entities which are yet to be played for the given league.

        Args:
            ctx (Context): The bot context.
            league_id_or_alias (str): The ID or alias referencing the League entity.
            limit (int): How many Fixture entities to retrieve.

        Returns:
            None.

        Raises:
            CommandDataError: If no Fixture entities are found.
        """

        league = self._get_league(league_id_or_alias)
        fixtures = self.bot.data_interface.get_upcoming_fixtures_by_league(league.id, limit=limit)
        if len(fixtures) == 0:
            raise CommandDataError(f"No upcoming fixtures found for {league.name}!")

        embed = embed_formatter.generate_fixtures_embed(fixtures)
        embed.title = f"Next {limit} {league.name} fixtures"
        await ctx.send(embed=embed)

    @commands.command(name="today", help="Get today's fixtures for a given league.")
    async def today(self, ctx, league_id_or_alias):
        """Gets today's Fixture entities.

        Args:
            ctx (Context): The bot context.
            league_id_or_alias (str): The ID or alias referencing the League entity.

        Returns:
            None.

        Raises:
            CommandDataError: If no Fixture entities are found.
        """

        today_str = datetime.now().strftime("%d/%m/%Y")
        await self.fixtures(ctx, league_id_or_alias, start_date=today_str, end_date=today_str)

    @commands.command(name="results", help="Get the latest <limit> results for a given league.")
    async def results(self, ctx, league_id_or_alias, limit=10):
        """Gets the most recent Fixture entities which have already been played.

        Args:
            ctx (Context): The bot context.
            league_id_or_alias (str): The ID or alias referencing the League entity.
            limit (int): How many Fixture entities to retrieve.

        Returns:
            None.

        Raises:
            CommandDataError: If no completed Fixture entities are found.
        """

        league = self._get_league(league_id_or_alias)
        fixtures = self.bot.data_interface.get_results_by_league(league.id, limit=limit)
        if len(fixtures) == 0:
            raise CommandDataError(f"No completed fixtures found for {league.name}!")

        embed = embed_formatter.generate_fixtures_embed(fixtures)
        embed.title = f"Latest {limit} {league.name} results"
        await ctx.send(embed=embed)

    # Internal protected methods #

    def _get_league(self, league_id_or_alias):
        """Gets the League entity from the database for a given league identifier.

        Args:
            league_id_or_alias (str): The ID of the League entity.

        Returns:
            League: The League entity matching the given league identifier.

        Raises:
            CommandDataError: If no matching League entity is found.
        """

        league = self.bot.data_interface.get(League, league_id_or_alias)
        if league is None:
            raise CommandDataError(f"No league found with id or alias '{league_id_or_alias}'. Run `!leagues` for help.")
        else:
            return league


def setup(bot):
    bot.add_cog(Statistics(bot))
