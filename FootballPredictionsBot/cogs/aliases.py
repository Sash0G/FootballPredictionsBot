# External
from discord.ext import commands

# Internal
from FootballPredictionsBot.models.alias import Alias
from FootballPredictionsBot.models.fixture import Fixture
from FootballPredictionsBot.models.league import League
from FootballPredictionsBot.models.team import Team
from FootballPredictionsBot.models.user import User
from FootballPredictionsBot.utils.converters import TextMatchConverter
from FootballPredictionsBot.utils.errors import CommandDataError


class Aliases(commands.Cog):
    """Commands for managing aliases.

    Attributes:
        bot (Bot): The bot instance.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="get_alias", help="Lists what an alias currently refers to if anything.", aliases=["ga"])
    async def get_alias(self, ctx, value):
        """Gets the entities referenced by a given alias value.
        
        Args:
            ctx (Context): The command context.
            value (str): The alias value.

        Returns:
            None.
            
        Raises:
            CommandDataError: If no alias is found.
        """
        
        alias = self.bot.data_interface.get(Alias, value)
        if alias is None:
            raise CommandDataError(f"No alias '{value}' found")
        else:
            await ctx.send(f"Alias: `{alias}`")

    @commands.command(name="delete_alias", help="Deletes an alias.", aliases=["da"])
    @commands.is_owner()
    async def delete_alias(self, ctx, value):
        """Deletes the given alias.
        
        Args:
            ctx (Context): The command context.
            value (str): The alias value.

        Returns:
            None.
            
        Raises:
            CommandDataError: If no alias is found.
        """
        
        deleted = self.bot.data_interface.delete(Alias, value)
        if deleted:
            await ctx.send(f"✅ Alias '{value}' deleted")
        else:
            raise CommandDataError(f"No alias '{value}' found")

    @commands.command(name="set_league_alias", help="Adds an alias to the given league.", aliases=["sla"])
    async def set_league_alias(self, ctx, alias_value, league_id, overwrite: TextMatchConverter("overwrite") = False):
        """Sets an alias value to reference the given League entity.
        
        Args:
            ctx (Context): The command context.
            alias_value (str): The alias value.
            league_id (int): The ID of the League entity.
            overwrite (bool): Whether to overwrite an existing entity if it exists.

        Returns:
            None.
        """
        
        await self._set_alias(ctx, League, alias_value, league_id, overwrite=overwrite)

    @commands.command(name="set_fixture_alias", help="Adds an alias to the given fixture.", aliases=["sfa"])
    async def set_fixture_alias(self, ctx, alias_value, fixture_id, overwrite: TextMatchConverter("overwrite") = False):
        """Sets an alias value to reference the given Fixture entity.

        Args:
            ctx (Context): The command context.
            alias_value (str): The alias value.
            fixture_id (int): The ID of the Fixture entity.
            overwrite (bool): Whether to overwrite an existing entity if it exists.

        Returns:
            None.
        """

        await self._set_alias(ctx, Fixture, alias_value, fixture_id, overwrite=overwrite)

    @commands.command(name="bulk_set_fixture_alias", help="Bulk adds a list of aliases to the given fixtures.", aliases=["bsfa"])
    @commands.is_owner()
    async def bulk_set_fixture_alias(self, ctx, overwrite: bool, *alias_fixture_strs):
        """Sets multiple alias values to reference the given Fixture entities.

        Args:
            ctx (Context): The command context.
            overwrite (bool): Whether to overwrite an existing entity if it exists.
            alias_fixture_strs (str): The alias value and fixture pair as <new_alias>:<id>

        Returns:
            None.
        """

        for alias_fixture_str in alias_fixture_strs:
            alias_value, fixture_id = alias_fixture_str.split(":")
            await self._set_alias(ctx, Fixture, alias_value, fixture_id, overwrite=overwrite)

    @commands.command(name="set_team_alias", help="Adds an alias to the given team.", aliases=["sta"])
    async def set_team_alias(self, ctx, alias_value, team_id, overwrite: TextMatchConverter("overwrite") = False):
        """Sets an alias value to reference the given Team entity.

        Args:
            ctx (Context): The command context.
            alias_value (str): The alias value.
            team_id (int): The ID of the Team entity.
            overwrite (bool): Whether to overwrite an existing entity if it exists.

        Returns:
            None.
        """

        await self._set_alias(ctx, Team, alias_value, team_id, overwrite=overwrite)
    
    @commands.command(name="bulk_set_team_alias", help="Bulk adds a list of aliases to the given teams.", aliases=["bsta"])
    @commands.is_owner()
    async def bulk_set_team_alias(self, ctx, overwrite: bool, *alias_team_strs):
        """Sets multiple alias values to reference the given Team entities.

        Args:
            ctx (Context): The command context.
            overwrite (bool): Whether to overwrite an existing entity if it exists.
            alias_team_strs (str): The alias value and team pair as <new_alias>:<id>

        Returns:
            None.
        """

        for alias_team_str in alias_team_strs:
            alias_value, team_id = alias_team_str.split(":")
            await self._set_alias(ctx, Team, alias_value, team_id, overwrite=overwrite)

    @commands.command(name="set_user_alias", help="Adds an alias to the given user.", aliases=["sua"])
    async def set_user_alias(self, ctx, alias_value, user_id, overwrite: TextMatchConverter("overwrite") = False):
        """Sets an alias value to reference the given User entity.

        Args:
            ctx (Context): The command context.
            alias_value (str): The alias value.
            user_id (int): The ID of the User entity.
            overwrite (bool): Whether to overwrite an existing entity if it exists.

        Returns:
            None.
        """

        await self._set_alias(ctx, User, alias_value, user_id, overwrite=overwrite)

    # Internal protected methods #

    async def _set_alias(self, ctx, cls, alias_value, id, overwrite=False):
        """Sets an alias value to reference the given entity.

        Args:
            ctx (Context): The command context.
            cls: The class of the entity to be referenced by this alias.
            alias_value (str): The alias value.
            id (int): The ID of the entity.
            overwrite (bool): Whether to overwrite an existing entity if it exists.

        Returns:
            None.

        Raises:
            CommandDataError: If the alias is a number, references a non-existent entity, or would overwrite
                an entity and the overwrite flag is False.
        """

        alias_ref = self._validate_and_get_alias_ref(cls, alias_value, id)
        existing_alias = self.bot.data_interface.get(Alias, alias_value)

        if existing_alias is not None and not overwrite:
            existing_ref = getattr(existing_alias, cls.__name__.lower())
            raise CommandDataError(
                f"An alias '{existing_alias.value}' already exists referencing `{existing_ref}`. Append `overwrite` to "
                "the end of your command to replace it."
            )

        alias = Alias(value=alias_value)
        setattr(alias, cls.__name__.lower(), alias_ref)
        alias = self.bot.data_interface.add_or_update(alias)

        if existing_alias is None:
            await ctx.send(f"✅ Added alias '{alias_value}' = `{alias_ref}`")
        else:
            await ctx.send(f"✅ Replaced existing alias '{alias.value}' with `{alias_ref}`")

    def _validate_and_get_alias_ref(self, cls, alias_value, id):
        """Performs validation on the given alias.

        Args:
            cls: The class of the entity to be referenced by this alias.
            alias_value (str): The alias value.
            id (int): The ID of the entity.

        Returns:
            An alias or ID representing the given Entity.

        Raises:
            CommandDataError: If the alias is a number.
        """

        if all(c.isdigit() for c in alias_value):
            raise CommandDataError(f"An alias can't be a number.")

        alias_ref = self.bot.data_interface.get(cls, id)
        if alias_ref is None:
            raise CommandDataError(f"No {cls.__name__} exists with id `{id}`")

        return alias_ref


def setup(bot):
    bot.add_cog(Aliases(bot))
