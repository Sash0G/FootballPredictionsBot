# External
from discord.ext import commands
import traceback

# Internal
from FootballPredictionsBot.utils import env
from FootballPredictionsBot.utils.errors import CommandDataError, APIError


class Events(commands.Cog):
    """Listeners to perform actions on bot events.

    Attributes:
        bot (Bot): The bot instance.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Log when the bot is ready."""

        guild_strs = [f"{guild.name} (id: {guild.id})" for guild in self.bot.guilds]
        env.log.info(f"{'CONNECTED':10s} > {self.bot.user} > {', '.join(guild_strs)}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Log when the bot has joined a guild.

        Args:
            guild (Guild): The guild which the bot has joined

        Returns:
            None.
        """

        env.log.info(f"{'ADDED':10s} > {guild.name} (id: {guild.id})")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Log when the bot has received a command."""

        msg_loc = self._guild_or_dm(ctx)
        env.log.info(f"{'RECEIVED':10s} > {msg_loc} > {ctx.author} > '{ctx.message.clean_content}'")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Log when the bot has successfully completed a command."""

        msg_loc = self._guild_or_dm(ctx)
        env.log.info(f"{'COMPLETE':10s} > {msg_loc} > {ctx.author} > '{ctx.message.clean_content}'")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Log when the bot has encountered an error performing a command and return a message to the user
        where applicable.

        Args:
            ctx (Context): The bot context.
            error (Exception): The error raised by a command.

        Returns:
            None.
        """
        msg_loc = self._guild_or_dm(ctx)
        env.log.warning(f"{'ERROR':10s} > {msg_loc} > {ctx.author} > '{ctx.message.clean_content}': '{error}'")

        if isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"⚠ **Error**: {error}")

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⚠ **Cooldown error**: This command is on cooldown, retry in {error.retry_after:.2f}s.")

        elif isinstance(error, commands.MissingPermissions):
            missing = [perm.replace("_", " ").replace("guild", "server").title() for perm in error.missing_perms]
            await ctx.send(f"⛔ **Permission error**: You need the {','.join(missing)} perm(s) to use this command.")

        elif isinstance(error, commands.errors.NotOwner):
            await ctx.send(f"⛔ **Permission error**: Only {self.bot.owner} can run this command.")

        elif (
            isinstance(error, commands.UserInputError)
            or isinstance(error, commands.MissingRequiredArgument)
            or isinstance(error, commands.BadArgument)
        ):
            await ctx.send(f"⚠ **Invalid input**: {error}")
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(error, CommandDataError):
            await ctx.send(f"⚠ **Data error**: {error}")

        elif isinstance(error, APIError):
            await ctx.send(f"⚠ **API-Football error**: {error}")

        else:
            if "2000 or fewer" in str(error) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(f"⚠ **Error**: Response >2,000 characters. Please reduce command parameters.")

            await ctx.send(f"⚠ **Error**: Bot encountered an unexpected error. Go tell Keith to fix this:\n`{error}`")
            traceback.print_exception(type(error), error, error.__traceback__)

    # Internal protected methods #

    @staticmethod
    def _guild_or_dm(ctx):
        """Determines whether a message was sent in a guild or DM.

        Args:
            ctx (Context): The bot context.

        Returns:
            str: The guild name or 'Direct Message'
        """
        try:
            return ctx.guild.name
        except AttributeError:
            return "Direct Message"


def setup(bot):
    bot.add_cog(Events(bot))
