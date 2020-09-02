# External
from discord.ext import commands
import os

# Internal
from FootballPredictionsBot.utils import env


class FootballPredictionsBot(commands.AutoShardedBot):
    """Discord bot with custom extensions loaded and access to the database.

    Attributes:
        data_interface (DataInterface): A DataInterface instance.
        data_loader (DataLoader): A DataLoader instance.
    """

    def __init__(self, data_interface, data_loader, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_interface = data_interface
        self.data_loader = data_loader
        self.load_cogs()

    def load_cogs(self):
        """Loads all Cogs from the 'cogs' directory as extensions for the bot."""

        cogs_dir = os.path.join("FootballPredictionsBot", "cogs")
        for file in os.listdir(cogs_dir):
            if file.endswith(".py"):
                name = file[:-3]
                self.load_extension(f"FootballPredictionsBot.cogs.{name}")
                env.log.info(f"Loaded cog {name}")
