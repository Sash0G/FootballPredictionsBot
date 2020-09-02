# External
from datetime import datetime
from discord import Embed

from FootballPredictionsBot.models.prediction import PredictionOutcome


def generate_status_embed(ctx, remaining_api_calls, last_refresh_times, boot_time, ram_used, avg_cpu, table_sizes):
    """Generates a Discord embed for displaying various status signals for the bot.

    Args:
        ctx (Context): The bot context.
        remaining_api_calls (int): The number of API calls remaining for the day.
        last_refresh_times (dict): The last time each data type was refreshed.
        boot_time (str): The time the bot started as a UTC string.
        ram_used (int): The amount of RAM the bot is currently using.
        avg_cpu (int): The amount of CPU currently busy.
        table_sizes (dict): The count of rows in each table.

    Returns:
        Embed: An embed displaying various status signals for the bot.
    """

    embed = Embed(color=0xEBE134)
    embed.set_thumbnail(url=ctx.bot.user.avatar_url)
    embed.add_field(name="Last boot", value=boot_time, inline=True)
    embed.add_field(name="Last refresh", value="\n".join([f"{k}: {time}" for k, time in last_refresh_times.items()]))
    embed.add_field(name="RAM Used", value=f"{ram_used:.2f} MB", inline=True)
    embed.add_field(name="CPU Used", value=f"{avg_cpu:.2f} %", inline=True)
    embed.add_field(name="Remaining API Calls", value=f"{remaining_api_calls} until midnight", inline=True)
    embed.add_field(
        name="Table sizes", value="\n".join([f"{table}: {size}" for table, size in table_sizes.items()]), inline=True
    )
    return embed


def generate_fixtures_embed(fixtures):
    """Generates a Discord embed for displaying a list of fixtures.

    Args:
        fixtures (list): The list of Fixture objects.

    Returns:
        Embed: An embed displaying a list of fixtures.
    """

    embed = Embed(color=0xFF0000)

    dates = {}
    for fixture in fixtures:
        date = datetime.fromisoformat(fixture.date).date()
        time = datetime.fromisoformat(fixture.date).strftime("%H:%M")
        aliases = " ".join([f"`{alias.value}`" for alias in fixture.aliases])
        f_str = f"{time} - {fixture.get_fixture_string()} `{fixture.id}` {aliases}"
        dates.setdefault(date, []).append(f_str)

    for date, f_strs in sorted(dates.items()):
        embed.add_field(name=f"{date.strftime('%d/%m/%Y')}", value="\n".join(f_strs), inline=False)

    return embed


def generate_leagues_embed(leagues):
    """Generates a Discord embed for displaying a list of leagues.

    Args:
        leagues (list): The list of League objects.

    Returns:
        Embed: An embed displaying a list of leagues.
    """

    embed = Embed(color=0x0080FF)

    countries = {}
    for league in leagues:
        l_str = f"{league.name} `{league.id}` {' '.join([f'`{alias.value}`' for alias in league.aliases])}"
        countries.setdefault(league.country, []).append(l_str)

    for country, l_strs in sorted(countries.items()):
        embed.add_field(name=f"{country}", value="\n".join(l_strs), inline=True)

    return embed


def generate_teams_embed(leagues):
    """Generates a Discord embed for displaying a list of teams.

    Args:
        leagues (list): The list of League objects.

    Returns:
        Embed: An embed displaying a list of teams.
    """

    embed = Embed(color=0xF5A623)

    for league in leagues:
        t_strs = []
        for team in sorted(league.teams, key=lambda team: team.name):
            t_strs.append(f"{team.name} `{team.id}` {' '.join([f'`{alias.value}`' for alias in team.aliases])}")

        if t_strs:
            embed.add_field(name=f"{league.name}", value="\n".join(t_strs), inline=True)

    return embed


def generate_predictions_embed(predictions):
    """Generates a Discord embed for displaying a list of predictions.

    Args:
        predictions (list): The list of Prediction objects.

    Returns:
        Embed: An embed displaying a list of predictions.
    """

    embed = Embed(color=0x9013FE)

    dates = {}
    for prediction in predictions:
        date = datetime.fromisoformat(prediction.fixture.date).date()
        time = datetime.fromisoformat(prediction.fixture.date).strftime("%H:%M")
        aliases = " ".join([f"`{alias.value}`" for alias in prediction.fixture.aliases])
        p_str = f"{time} - {prediction.get_prediction_string()} `{prediction.fixture.id}` {aliases}"
        dates.setdefault(date, []).append(p_str)

    for date, p_strs in dates.items():
        embed.add_field(name=f"{date.strftime('%d/%m/%Y')}", value="\n".join(p_strs), inline=False)

    return embed


def generate_leaderboard_embed(user_scores, table=False):
    """Generates a Discord embed for displaying the users with the highest prediction scores for the given league.

    If table=False, will return the top 3 users in an inline form. If table=True, will return a tabular
    view of all users in a large code block. Table view does not look good on mobile.

    Args:
        user_scores (dict): A map of users to their prediction score information.
        table (bool): Whether to display the output as a table or not.

    Returns:
        Embed: An embed displaying the leaderboard either as a top 3 or a table.
    """

    if table:
        return _generate_leaderboard_table_embed(user_scores)

    embed = Embed(color=0x12E34A)

    awards = {0: {"medal": "🥇", "title": "1st"}, 1: {"medal": "🥈", "title": "2nd"}, 2: {"medal": "🥉", "title": "3rd"}}
    for i, (user, info) in enumerate(sorted(user_scores.items(), key=lambda user: user[1]["points"], reverse=True)[:3]):
        embed.add_field(
            name=f"{awards[i]['medal']} {awards[i]['title']} Place: {user}",
            value=f"Points: {info['points']}\nCorrect scores: {info['scores']}\nCorrect results: {info['results']}",
            inline=True,
        )
    embed.set_footer(text=PredictionOutcome.FORMULA.value)
    return embed


def _generate_leaderboard_table_embed(user_scores):
    """Generates a tabular view of all users and their scores in a large code block.

    Args:
        user_scores (dict): A map of users to their prediction score information.

    Returns:
        Embed: An embed displaying the leaderboard as a table.
    """

    table_rows = ""
    for user, info in sorted(user_scores.items(), key=lambda user: user[1]["points"], reverse=True):
        table_rows += f"{user:20} | {info['points']:6} | {info['scores']:6} | {info['results']:7}\n"

    table_headers = f"{'Username':20} | {'Points':6} | {'Scores':6} | {'Results':7}\n{'=' * 48}"
    embed = Embed(color=0x12E34A, description=f"```{table_headers}\n{table_rows}```")
    embed.set_footer(text=PredictionOutcome.FORMULA.value)
    return embed
