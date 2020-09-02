# External
from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Internal
from FootballPredictionsBot.utils import env
from FootballPredictionsBot.utils.data_interface_base import Base


class Prediction(Base):
    """ORM for prediction objects from the database."""

    __tablename__ = "predictions"

    fixture_id = Column(Integer, ForeignKey("fixtures.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.discord_id", onupdate="CASCADE"), primary_key=True)
    guild_id = Column(Integer, primary_key=True)
    home_goals = Column(Integer, nullable=False)
    away_goals = Column(Integer, nullable=False)
    updated = Column(String, nullable=False)  # We are entrusted to keep this in check, NOT a trigger in the db
    user = relationship("User")
    fixture = relationship("Fixture")

    def __repr__(self):
        return (
            f"<Prediction(fixture={self.fixture}, user_id={self.user_id},"
            f" score={self.home_goals}-{self.away_goals}, updated={self.updated})>"
        )

    def get_prediction_string(self):
        return f"{self.fixture.home_team.name} {self.home_goals}-{self.away_goals} {self.fixture.away_team.name}"


class PredictionOutcome(Enum):
    SCORE = env.get_cfg("POINTS_SCORE")
    RESULT = env.get_cfg("POINTS_RESULT")
    INCORRECT = 0
    FORMULA = f"Points = (<scores> * {SCORE}) + (<results> * {RESULT})"

    @classmethod
    def determine_outcome(cls, prediction, fixture):
        if fixture.home_goals == prediction.home_goals and fixture.away_goals == prediction.away_goals:
            return cls.SCORE
        elif (
            (fixture.home_goals == fixture.away_goals and prediction.home_goals == prediction.away_goals)
            or (fixture.home_goals > fixture.away_goals and prediction.home_goals > prediction.away_goals)
            or (fixture.home_goals < fixture.away_goals and prediction.home_goals < prediction.away_goals)
        ):
            return cls.RESULT
        else:
            return cls.INCORRECT
