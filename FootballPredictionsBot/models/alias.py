# External
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

# Internal
from FootballPredictionsBot.utils.data_interface_base import Base


class Alias(Base):
    """ORM for alias objects from the database."""

    __tablename__ = "aliases"

    value = Column(String(collation="NOCASE", length=30), primary_key=True)
    fixture_id = Column(Integer, ForeignKey("fixtures.id"))
    league_id = Column(Integer, ForeignKey("leagues.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    user_id = Column(Integer, ForeignKey("users.discord_id"))
    fixture = relationship("Fixture")
    league = relationship("League")
    team = relationship("Team")
    user = relationship("User")

    def __repr__(self):
        return (
            f"<Alias(value={self.value}, fixture={self.fixture}, league={self.league}, team={self.team},"
            f" user={self.user})>"
        )
