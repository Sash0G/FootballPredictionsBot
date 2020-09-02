# External
import json
from datetime import datetime, timedelta
from discord.ext import commands
import pytz

# Internal
from FootballPredictionsBot.models.fixture import Fixture
from FootballPredictionsBot.models.league import League
from FootballPredictionsBot.models.prediction import Prediction, PredictionOutcome
from FootballPredictionsBot.models.user import User
from FootballPredictionsBot.utils import checks
from FootballPredictionsBot.utils import env
from FootballPredictionsBot.utils import embed_formatter
from FootballPredictionsBot.utils.converters import TextMatchConverter, PredictionInputConverter, DateConverter
from FootballPredictionsBot.utils.errors import CommandDataError


class Predictions(commands.Cog):
    """Commands for making and viewing predictions.

    Attributes:
        bot (Bot): The bot instance.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="predict",
        brief="Make predictions.",
        help=(
            "Make predictions.\nFormat: !predict <fixture_id>:<home_goals>-<away_goals> ...\n"
            "e.g. !predict 1234:1-1 1235:3-0 1236:2-2"
        ),
    )
    @checks.guild_only_if_in_multiple_guilds()
    async def predict(self, ctx, *args: PredictionInputConverter):
        """Add or update a set of Prediction entities.

        Args:
            ctx (Context): The bot context.
            *args (list): A set of predictions.

        Returns:
            None.

        Raises:
            UserInputError: If there are no predictions in the input arguments.
        """

        await self.predict_for(ctx, str(ctx.author), False, *args)

    @commands.command(name="predict_for", help="Make predictions for the given user.")
    @commands.guild_only()
    @commands.is_owner()
    async def predict_for(self, ctx, username_or_alias, skip_time_check, *args: PredictionInputConverter):
        """Add or update a set of Prediction entities.

        Args:
            ctx (Context): The bot context.
            username_or_alias (str): The user's discord username + discriminator (e.g. KeithyDee#1234) or alias.
            skip_time_check (bool): Whether to ignore the time validation.
            *args (list): A set of predictions.

        Returns:
            None.

        Raises:
            UserInputError: If there are no predictions in the input arguments.
        """

        if not args:
            raise commands.UserInputError("At least one prediction is required")

        user, guild = self._get_user(ctx, username_or_alias)
        user = self.bot.data_interface.add_or_update(user)

        predictions = []
        for (fixture_id_or_alias, home_goals, away_goals) in args:
            fixture = self.bot.data_interface.get(Fixture, fixture_id_or_alias)
            fixture = self._validate_prediction_fixture(fixture_id_or_alias, fixture, skip_time_check=skip_time_check)

            prediction = Prediction(
                fixture_id=fixture.id,
                user_id=user.discord_id,
                guild_id=guild.id,
                home_goals=home_goals,
                away_goals=away_goals,
                updated=datetime.now(),
            )
            predictions.append(self.bot.data_interface.add_or_update(prediction))

        embed = embed_formatter.generate_predictions_embed(predictions)
        embed.title = f"Set the following predictions for {username_or_alias}"
        await ctx.send(embed=embed)

    @commands.command(name="predictions", help="Get a list of your predictions between the given dates.")
    @checks.guild_only_if_in_multiple_guilds()
    async def my_predictions(self, ctx, start_date=None, end_date=None):
        """Gets all predictions made by the requesting user between the given dates.

        Args:
            ctx (Context): The bot context.
            start_date (str): The lower bound date.
            end_date (str): The upper bound date.

        Returns:
            None.

        Raises:
            CommandDataError: If the user could not be found in the database.
        """

        await self.predictions_for(ctx, str(ctx.author), start_date=start_date, end_date=end_date)

    @commands.command(name="predictions_for", help="Get a list of any users predictions between the given dates.")
    @commands.guild_only()
    @commands.is_owner()
    async def predictions_for(self, ctx, username_or_alias, start_date=None, end_date=None):
        """Gets all predictions made by the given user between the given dates.

        Args:
            ctx (Context): The bot context.
            username_or_alias (str): The user's discord username + discriminator (e.g. KeithyDee#1234) or alias.
            start_date (str): The lower bound date.
            end_date (str): The upper bound date.

        Returns:
            None.

        Raises:
            CommandDataError: If the user could not be found in the database.
        """

        start_date, end_date = DateConverter.get_dates(start_date, end_date)
        user, guild = self._get_user(ctx, username_or_alias)

        predictions = self.bot.data_interface.get_predictions_by_user_between_date(
            user.discord_id, guild.id, start_date, end_date
        )

        embed = embed_formatter.generate_predictions_embed(predictions)
        embed.title = (
            f"{username_or_alias}'s predictions between {start_date.strftime('%d/%m/%Y')} and"
            f" {end_date.strftime('%d/%m/%Y')}"
        )
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", help="Gets the leaderboard for the given league")
    @commands.guild_only()
    async def leaderboard(self, ctx, league_id_or_alias, table: TextMatchConverter("table") = False):
        """Generates a leaderboard for users with the highest prediction scores for the given league.

        If table=False, will return the top 3 users in an inline form. If table=True, will return a tabular
        view of all users in a large code block.

        Args:
            ctx (Context): The bot context.
            league_id_or_alias (str): The ID or alias referencing the League entity.
            table (bool): Whether to display the output as a table or not.

        Returns:
            None.
        """

        league = self._get_league(league_id_or_alias)
        results = self.bot.data_interface.get_results_by_league(league.id)
        predictions = self.bot.data_interface.get_predictions_by_league(league.id)

        internal_scores = {}
        final_scores = {}
        user_info = {"points": 0, "results": 0, "scores": 0}

        # Backload scores from a different predictions site
        with open(env.get_cfg("SPFL_SCORES")) as f:
            spfl_scores = json.load(f)

        for prediction in [p for p in predictions if p.fixture in results]:
            prediction_result = PredictionOutcome.determine_outcome(prediction, prediction.fixture)

            if prediction_result == PredictionOutcome.SCORE:
                internal_scores.setdefault(prediction.user, user_info.copy())["points"] += PredictionOutcome.SCORE.value
                internal_scores[prediction.user]["scores"] += 1
            elif prediction_result == PredictionOutcome.RESULT:
                internal_scores.setdefault(prediction.user, user_info.copy())["points"] += PredictionOutcome.RESULT.value
                internal_scores[prediction.user]["results"] += 1
            elif prediction_result == PredictionOutcome.INCORRECT:
                internal_scores.setdefault(prediction.user, user_info.copy())

        for user, values in internal_scores.items():
            env.log.info(internal_scores)
            user_info = ctx.bot.get_user(user.discord_id)
            final_scores[f"{user_info.name}#{user_info.discriminator}"] = values

        # Combine scores from a different predictions site
        for user, values in spfl_scores.items():
            points = (values["scores"] * PredictionOutcome.SCORE.value) + (
                        values["results"] * PredictionOutcome.RESULT.value)
            if user in final_scores.keys():
                final_scores[user]["scores"] += values["scores"]
                final_scores[user]["results"] += values["results"]
                final_scores[user]["points"] += points
            else:
                final_scores[user] = {
                    "scores": values["scores"],
                    "results": values["results"],
                    "points": points
                }

        embed = embed_formatter.generate_leaderboard_embed(final_scores, table=table)
        embed.title = f"Leaderboard for {league.name} predictions"
        await ctx.send(embed=embed)

    # Internal protected methods

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

    def _get_user(self, ctx, username_or_alias):
        """Gets the User entity and user's guild from the database for a given user identifier.

        Note: A 'member' is a User in a particular guild. For predictions, we need to know which guild the user is
        a part of. That's easy if the command was executed within a guild, but if the command was executed in a DM
        then we need to look at the members of every guild where the bot runs to work out which guild the user is from.
        For this reason, the bot has already rejected a DM prediction if the user is a member of multiple guilds.

        Args:
            username_or_alias (str): The user's discord username + discriminator (e.g. KeithyDee#1234) or alias.

        Returns:
            User: The User entity matching the given username or alias.

        Raises:
            CommandDataError: If no matching User entity is found either in the database or in any guild.
        """

        user = self.bot.data_interface.get(User, username_or_alias)
        if user is not None:
            members = [member for member in self.bot.get_all_members() if member.id == user.discord_id]
        else:
            members = [member for member in self.bot.get_all_members() if str(member) == username_or_alias]

        if len(members) == 0:
            raise CommandDataError(f"No user {username_or_alias} found in any guild where this bot runs.")
        member = members[0]

        if ctx.message.guild is not None:
            guild = ctx.message.guild
        else:
            guild = member.guild

        if user is not None:
            return user, guild
        else:
            return User(discord_id=member.id), guild

    @staticmethod
    def _validate_prediction_fixture(fixture_id_or_alias, fixture, skip_time_check=False):
        """Determines whether the given fixture is valid for setting a prediction on.

        Args:
            fixture_id_or_alias (str): The ID or alias referencing a Fixture entity.
            fixture (Fixture): A Fixture entity
            skip_time_check (bool): Whether to ignore the time validation.

        Returns:
            Fixture: A fixture entity if valid for setting a prediction on

        Raises:
            CommandDataError: If a Fixture entity could not be found or the deadline for setting a prediction
                for this entity has passed.
        """

        if fixture is None:
            raise CommandDataError(f"No fixture found with id or alias '{fixture_id_or_alias}'")
        else:
            if not skip_time_check:
                time_cutoff = datetime.fromisoformat(fixture.date) - timedelta(hours=1)
                if datetime.now(tz=pytz.timezone(env.get_cfg("BOT_TIMEZONE"))) > time_cutoff:
                    raise CommandDataError(
                        f"Deadline for setting a prediction for {fixture.get_fixture_string()} has passed!"
                    )

        return fixture


def setup(bot):
    bot.add_cog(Predictions(bot))
