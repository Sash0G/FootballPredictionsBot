# External
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

# Internal
from FootballPredictionsBot.utils.data_interface_base import Base


class Fixture(Base):
    """ORM for fixture objects from the database."""

    __tablename__ = "fixtures"

    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    date = Column(String, nullable=False)
    round = Column(String, nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    status = Column(String, nullable=False)
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    league = relationship("League")
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    aliases = relationship("Alias", backref="rel_alias_fixture")

    def __repr__(self):
        return (
            f"<Fixture(id={self.id}, league={self.league.name}, date={self.date},"
            f" home_team={self.home_team.name}, away_team={self.away_team.name})>"
        )

    @classmethod
    def from_api(cls, fixture_item):
        id = fixture_item["fixture_id"]
        league_id = fixture_item["league_id"]
        date = fixture_item["event_date"]
        round = fixture_item["round"]
        home_team_id = fixture_item["homeTeam"]["team_id"]
        away_team_id = fixture_item["awayTeam"]["team_id"]
        status = fixture_item["status"]
        home_goals = fixture_item["goalsHomeTeam"]
        away_goals = fixture_item["goalsAwayTeam"]
        cls = Fixture(
            id=id,
            league_id=league_id,
            date=date,
            round=round,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            status=status,
            home_goals=home_goals,
            away_goals=away_goals,
        )
        return cls

    def get_fixture_string(self):
        if self.home_goals is not None:
            return f"{self.home_team.name} {self.home_goals}-{self.away_goals} {self.away_team.name}"
        else:
            return f"{self.home_team.name} v {self.away_team.name}"
