# External
from contextlib import contextmanager
from datetime import date, datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.pool import StaticPool

# Internal
from FootballPredictionsBot.utils.data_interface_base import Base
from FootballPredictionsBot.models.league import League
from FootballPredictionsBot.models.fixture import Fixture
from FootballPredictionsBot.models.prediction import Prediction
from FootballPredictionsBot.models.user import User
from FootballPredictionsBot.models.alias import Alias
from FootballPredictionsBot.utils import env


class DataInterface:
    """Provides an interface to the database and methods for getting/inserting/updating data.

    Attributes:
        db (str): The database connection string.
        Session (Session): A session class which sessions can be spawned from.
        session (Session): A single session.
    """

    def __init__(self):
        self.db = env.get_cfg("PATH_DB")
        engine = create_engine(self.db, echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False},)
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""

        session = self.session
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise

    def close(self):
        """Closes the open session."""

        self.session.close()

    # Meta methods #

    def get_table_sizes(self):
        """Gets the sizes of all tables in the database."""

        sizes = {}
        with self.session_scope() as session:
            for table in Base.metadata.tables:
                query = Base.metadata.tables.get(table).count()
                sizes[table] = session.scalar(query)
        return sizes

    # Generic methods #

    def add_or_update(self, item):
        """Adds or updates the given item to the persistent datastore.

        Args:
            item: The mapped entity.

        Returns:
            The mapped entity.
        """

        with self.session_scope() as session:
            return session.merge(item)

    def get(self, cls, id_or_alias):
        """Gets the mapped entity matching the given class and id.

        An alias can be used in place of an identifier.

        Args:
            cls: The class of the mapped entity to retrieve.
            id_or_alias: Either the primary identifier of the mapped entity or an alias representing it.

        Returns:
            The mapped entity.
        """

        with self.session_scope() as session:
            if cls == Alias:
                return session.query(Alias).get(id_or_alias)
            else:
                try:
                    alias = session.query(Alias).filter_by(value=id_or_alias).join(cls).add_entity(cls).one()
                    return alias._asdict()[cls.__name__]
                except NoResultFound:
                    return session.query(cls).get(id_or_alias)

    def get_all(self, cls):
        """Gets all mapped entities matching the given class.

        Args:
            cls: The class of the mapped entities to retrieve.

        Returns:
            The mapped entities.
        """

        with self.session_scope() as session:
            return session.query(cls)

    def delete(self, cls, id_or_alias):
        """Deletes the mapped entity matching the given class and id.

        An alias can be used in place of an identifier.

        Args:
            cls: The class of the mapped entity to delete.
            id_or_alias: Either the primary identifier of the mapped entity or an alias representing it.

        Returns:
            bool: True if the mapped entity was found in the datastore and deleted, else False.
        """

        with self.session_scope() as session:
            item = self.get(cls, id_or_alias)
            if item is not None:
                session.delete(item)
                return True
            else:
                return False

    # Insert/update methods #

    def add_team_to_league(self, team, league):
        """Adds a Team entity to a League entity.

        Args:
            team (Team): The mapped Team entity.
            league (League): The mapped League entity.

        Returns:
            The updated League entity.
        """

        with self.session_scope() as session:
            league.teams.append(team)
            return session.merge(league)

    # Select methods #

    def get_current_leagues(self):
        """Gets all League entities which are currently in play.

        Returns:
            list: All League entities which are currently in play.
        """

        with self.session_scope() as session:
            return session.query(League).filter_by(is_current=True).order_by(League.rank).all()

    def get_upcoming_fixtures_by_league(self, league_id, limit=-1):
        """Gets the next Fixture entities which are yet to be played for the given league.

        Args:
            league_id (int): The id of a League entity to match.
            limit (int): How many results to retrieve.

        Returns:
            list: All Fixture entities which are yet to be played for the given league.
        """

        with self.session_scope() as session:
            return (
                session.query(Fixture)
                .filter_by(league_id=league_id)
                .filter(func.DATETIME(Fixture.date) >= datetime.now())
                .order_by(Fixture.date)
                .limit(limit)
                .all()
            )

    def get_results_by_league(self, league_id, limit=-1):
        """Gets the most recent Fixture entities which have already been played.

        Args:
            league_id (int): The id of a League entity to match.
            limit (int): How many results to retrieve.

        Returns:
            list: The most recent Fixture entities which have already been played.
        """

        with self.session_scope() as session:
            return (
                session.query(Fixture)
                .filter_by(league_id=league_id)
                .filter(Fixture.home_goals.isnot(None))
                .order_by(Fixture.date.desc())
                .limit(limit)
                .from_self()
                .order_by(Fixture.date)
                .all()
            )

    def get_fixtures_by_league_between_date(self, league_id, start_date, end_date):
        """Gets all Fixture entities between the given dates.

        Args:
            league_id (int): The id of a League entity to match.
            start_date (date): The lower bound date.
            end_date (date): The upper bound date.

        Returns:
            list: All Fixture entities between the given dates.
        """

        with self.session_scope() as session:
            return (
                session.query(Fixture)
                .filter_by(league_id=league_id)
                .filter(func.DATE(Fixture.date) >= start_date)
                .filter(func.DATE(Fixture.date) <= end_date)
                .order_by(Fixture.date)
                .all()
            )

    def get_predictions_by_user_between_date(self, user_id, guild_id, start_date, end_date):
        """Gets all Prediction entities between the given dates for the given user.

        Args:
            user_id (int): The id of a User entity to match.
            guild_id (int): The id of the guild to match.
            start_date (date): The lower bound date.
            end_date (date): The upper bound date.

        Returns:
            list: All Prediction entities between the given dates for the given user.
        """

        with self.session_scope() as session:
            return (
                session.query(Prediction)
                .filter_by(user_id=user_id)
                .filter_by(guild_id=guild_id)
                .join(Prediction.fixture)
                .filter(func.DATE(Fixture.date) >= start_date)
                .filter(func.DATE(Fixture.date) <= end_date)
                .order_by(Fixture.date)
                .all()
            )

    def get_predictions_by_league(self, league_id, limit=-1):
        """Gets all Prediction entities for a given league.

        Args:
            league_id (int): The id of a League entity to match.
            limit (int): How many results to retrieve.

        Returns:
            list: All Prediction entities for a given league.
        """

        with self.session_scope() as session:
            return (
                session.query(Prediction)
                .join(Prediction.fixture)
                .filter(Fixture.league_id == league_id)
                .limit(limit)
                .all()
            )
