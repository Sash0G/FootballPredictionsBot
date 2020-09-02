# External
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

# Internal
from FootballPredictionsBot.utils.data_interface_base import Base

teams_leagues_association = Table(
    "teams_leagues",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("league_id", Integer, ForeignKey("leagues.id"), primary_key=True),
)


class Team(Base):
    """ORM for team objects from the database."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    leagues = relationship("League", secondary=teams_leagues_association, backref="team")
    aliases = relationship("Alias", backref="rel_alias_teams")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"

    @classmethod
    def from_api(cls, team_item):
        id = team_item["team_id"]
        name = team_item["name"]
        cls = Team(id=id, name=name)
        return cls
