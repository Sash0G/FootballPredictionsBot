# External
from datetime import datetime
from discord.ext import commands
import os
import psutil


from FootballPredictionsBot.utils import embed_formatter


class Admin(commands.Cog):
    """Commands for administering the bot.

    Attributes:
        bot (Bot): The bot instance.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="refresh_all", help="Refreshes all entities. Same as a scheduled refresh, but now.")
    @commands.is_owner()
    async def refresh_all(self, ctx):
        """Performs a refresh of all entities."""

        self.bot.data_loader.load_all()
        await ctx.send("✅ Reloaded all entities")

    @commands.command(name="refresh_fixtures", help="Refreshes the fixture list.")
    @commands.is_owner()
    async def refresh_fixtures(self, ctx):
        """Performs a refresh of all Fixture entities."""

        self.bot.data_loader.populate_fixtures()
        await ctx.send("✅ Reloaded all fixtures")

    @commands.command(name="status", help="Gets various status signals for the bot.")
    @commands.is_owner()
    async def status(self, ctx):
        """Gets various status signals for the bot."""

        remaining_api_calls = self.bot.data_loader.get_remaining_api_calls()
        last_refresh_times = self.bot.data_loader.last_refresh_times.copy()
        table_sizes = self.bot.data_loader.data_interface.get_table_sizes()

        for datatype, refresh_time in last_refresh_times.items():
            if refresh_time is None:
                last_refresh_times[datatype] = "Never"
            else:
                last_refresh_times[datatype] = refresh_time.isoformat()

        proc = psutil.Process(os.getpid())
        ram_used = proc.memory_full_info().rss / 1024 ** 2
        cpu_used = proc.cpu_percent()
        boot_time = datetime.utcfromtimestamp(proc.create_time()).isoformat()

        embed = embed_formatter.generate_status_embed(
            ctx, remaining_api_calls, last_refresh_times, boot_time, ram_used, cpu_used, table_sizes
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Admin(bot))
