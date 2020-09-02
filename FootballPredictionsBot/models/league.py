# External
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

# Internal
from FootballPredictionsBot.utils.data_interface_base import Base
from FootballPredictionsBot.models.team import teams_leagues_association


class League(Base):
    """ORM for league objects from the database."""

    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    season = Column(Integer, nullable=False)
    is_current = Column(Boolean, nullable=False)
    rank = Column(Integer, nullable=True)  # Column manually updated, not present in API-Football
    teams = relationship("Team", secondary=teams_leagues_association)
    fixtures = relationship("Fixture", backref="leagues_fixtures")
    aliases = relationship("Alias", backref="rel_alias_league")

    def __repr__(self):
        return f"<League(id={self.id}, name={self.name}, country={self.country}, season={self.season})>"

    @classmethod
    def from_api(cls, league_item):
        id = league_item["league_id"]
        name = league_item["name"]
        country = league_item["country"]
        season = league_item["season"]
        is_current = league_item["is_current"]
        cls = League(id=id, name=name, country=country, season=season, is_current=is_current)
        return cls
