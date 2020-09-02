# External
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Internal
from FootballPredictionsBot.football_predictions_bot import FootballPredictionsBot
from FootballPredictionsBot.data_interface import DataInterface
from FootballPredictionsBot.data_loader import DataLoader
from FootballPredictionsBot.football_api import FootballAPI
from FootballPredictionsBot.utils import env
from FootballPredictionsBot.utils.refresh_manager import RefreshManager


def startup():
    """Bot startup sequence which may include refreshing data, scheduling a refresh, and eventually starting the bot.

    Returns:
        None.
    """

    if env.get_arg("scheduled_refresh"):
        refresh_manager.schedule_refresh()
    if env.get_arg("startup_refresh"):
        refresh_manager.do_refresh()

    bot = FootballPredictionsBot(data_interface, data_loader, command_prefix=env.get_cfg("BOT_COMMAND_PREFIX"))
    bot.run(env.get_cfg("DISCORD_TOKEN"))


def shutdown():
    """Called on script exit to shut down any dangling connections.

    Returns:
        None.
    """

    if env.get_arg("scheduled_refresh"):
        scheduler.shutdown()
        env.log.info("Refresh thread closed")
    data_interface.close()
    env.log.info("Database connection closed")


# Initialise the various utility classes used by the bot
env.log.info("Starting up FootballPredictionsBot")
data_interface = DataInterface()
football_api = FootballAPI()
data_loader = DataLoader(data_interface, football_api)
scheduler = BackgroundScheduler()
refresh_manager = RefreshManager(scheduler, data_loader)

# Register our shutdown hook to cleanup threads/connections and off we go!
atexit.register(shutdown)
startup()
