# External
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz

# Internal
from FootballPredictionsBot.utils import env


class RefreshManager:
    """Schedules and executes the refresh tasks from API-Football to the database."""

    def __init__(self, background_scheduler, data_loader):
        """Initialises the RefreshManager instance.

        Args:
            background_scheduler (BackgroundScheduler): The scheduler instance which is managing the refresh jobs.
            data_loader (DataLoader): The data loader instance which performs the refresh.
        """

        self.scheduler = background_scheduler
        self.data_loader = data_loader

    def schedule_refresh(self):
        """Schedules a refresh of the data to occur from API-Football at midnight each night."""

        tz = pytz.timezone(env.get_cfg("BOT_TIMEZONE"))
        midnight = (datetime.now(tz) + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        self.scheduler.add_job(self.do_refresh, "interval", days=1, next_run_time=midnight, id="Refresh")
        self.scheduler.start()
        env.log.info(f"Next scheduled refresh: {self.scheduler.get_job('Refresh').next_run_time.isoformat()}")

    def do_refresh(self):
        """Performs a data refresh from API-Football to the database."""

        env.log.info("Performing a data refresh")
        self.data_loader.load_all()

        if env.get_arg("scheduled_refresh"):
            env.log.info(f"Next scheduled refresh: {self.scheduler.get_job('Refresh').next_run_time.isoformat()}")
