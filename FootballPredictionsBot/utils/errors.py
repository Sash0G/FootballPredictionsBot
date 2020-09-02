# External
from discord.ext import commands


class CommandDataError(commands.CommandError):
    """Signifies that the data was retrieved successfully, but there is either no data or the data is malformed."""

    pass


class APIError(Exception):
    """Used to represent any error received from API-Football."""

    pass
