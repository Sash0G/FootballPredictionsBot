# External
from discord.ext import commands


def guild_only_if_in_multiple_guilds():
    """See predicate()"""

    async def predicate(ctx):
        """Determines whether the message is a DM and if the member is part of only one guild where the bot runs.
        If none or multiple, reject the request as some commands are guild-specific.

        Args:
            ctx (discord.ext.commands.Context): The context of the request.

        Returns:
            bool: True if member is part of one guild where the bot runs and this is a DM.
        """

        if ctx.guild is None:
            matching_members = [member for member in ctx.bot.get_all_members() if str(member) == str(ctx.author)]
            if len(matching_members) != 1:
                raise commands.CheckFailure(
                    "You must run this command from within a guild as you are part of multiple guilds where this bot "
                    "runs. Some commands like setting predictions are guild-specific."
                )
        return True

    return commands.check(predicate)
