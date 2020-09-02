# External
from datetime import datetime, timedelta
from discord.ext import commands
from discord.ext.commands import UserInputError
import pytz

# Internal
from FootballPredictionsBot.utils import env


class TextMatchConverter(commands.Converter):
    """Converts keyword arguments to booleans if they match the keyword name.

    We don't use the built-in boolean converter as it converts things like 'True' and 'y', which is
    a bit confusing in a bot command. This command converts 'overwrite' to True if the kwarg name is
    'overwrite', False if nothing is present, and throws an error for anything else.
    """

    def __init__(self, text_to_match):
        self.text_to_match = text_to_match

    async def convert(self, ctx, argument):
        """Converts keyword arguments to booleans if they match the keyword name.

        Args:
            ctx (Context): The bot context.
            argument (str): The argument value.

        Returns:
            bool: Whether the argument matches the expected text.

        Raises:
            UserInputError: If the argument doesn't match and is not None.
        """

        if argument == self.text_to_match:
            return True
        elif argument is None:
            return False
        else:
            raise UserInputError(
                f"{self.text_to_match.capitalize()} arg can only be `{self.text_to_match}` or nothing. Does your"
                " command have an unquoted alias?"
            )


class PredictionInputConverter(commands.Converter):
    """Converts a prediction input string to a PredictionInput class."""

    async def convert(self, ctx, argument):
        """Converts a prediction input string to a PredictionInput class.

        Args:
            ctx (Context): The bot context.
            argument (str): The argument value.

        Returns:
            list: The parsed components of the prediction input.

        Raises:
            UserInputError: If the argument could not be parsed into the prediction components.
        """

        try:
            fixture_id_or_alias, score = argument.split(":")
        except ValueError:
            raise commands.UserInputError("Predictions must be of the form `<id>`:`<score>`")

        try:
            home_goals, away_goals = score.split("-")
        except ValueError:
            raise commands.UserInputError("Score string must be of format `<home_goals>`-`<away_goals>`")

        return fixture_id_or_alias, home_goals, away_goals


class DateConverter:
    """Converts a start_date or end_date argument into a Date object.

    If the object is None, returns the default look-back or look-forward date range. Not actually a standard
    type converter because we want the default start/end dates to update at runtime and not compile time.
    """

    @classmethod
    def get_dates(cls, start_date, end_date):
        """Converts a start_date or end_date argument into a Date object.

        Returns:
            list: The start date and end date arguments as Date objects.
        """

        if start_date is None:
            start_date = (datetime.now(tz=pytz.timezone(env.get_cfg("BOT_TIMEZONE"))) - timedelta(days=3)).date()
        else:
            if not isinstance(start_date, datetime):
                start_date = cls.convert(start_date)

        if end_date is None:
            end_date = (datetime.now(tz=pytz.timezone(env.get_cfg("BOT_TIMEZONE"))) + timedelta(days=5)).date()
        else:
            if not isinstance(end_date, datetime):
                end_date = cls.convert(end_date)

        return start_date, end_date

    @classmethod
    def convert(cls, argument):
        """Converts a date argument into a Date object.

        Args:
            argument (str): The argument value.

        Returns:
            A date object representing the argument
        """

        return datetime.strptime(argument, "%d/%m/%Y").date()
