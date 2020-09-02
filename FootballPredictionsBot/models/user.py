# External
from sqlalchemy import Column, Integer

# Internal
from sqlalchemy.orm import relationship

from FootballPredictionsBot.utils.data_interface_base import Base


class User(Base):
    """ORM for user objects from the database. Currently we just store the discord ID of the user
    and rely on an API call to get username, but this class is here in case we want to expand on that.
    """

    __tablename__ = "users"

    discord_id = Column(Integer, primary_key=True)
    aliases = relationship("Alias", backref="rel_alias_user")

    def __repr__(self):
        return f"<User(discord_id={self.discord_id})>"
