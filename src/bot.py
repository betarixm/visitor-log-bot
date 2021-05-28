import os

from datetime import datetime, timezone, timedelta
import re

from discord.ext import commands
from discord import Member, Embed, Color
from db import Database


class HelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = Embed(title="Visitor Log Bot 🤖", color=Color.blurple(), description='')
        e.set_author(name="beta", url="https://github.com/betarixm", icon_url="https://avatars.githubusercontent.com/u/26831314")

        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)


class Visit(commands.Cog):
    def __init__(self, b):
        self.bot = b

    @commands.command(aliases=["출근"], help="Add user's 'Enter' log.")
    async def enter(self, ctx: commands.context.Context):
        author: Member = ctx.author
        db.enter(author.id, author.display_name)
        await ctx.send(embed=embed_current(ctx, title=f"Welcome, {ctx.author.display_name} 💙"))

    @commands.command(aliases=["퇴근"], help="Add user's 'Leave' log.")
    async def leave(self, ctx: commands.context.Context):
        author: Member = ctx.author
        db.leave(author.id, author.display_name)
        db.current_all()
        await ctx.send(embed=embed_current(ctx, title=f"Bye, {ctx.author.display_name} 👋"))


class Search(commands.Cog):
    def __init__(self, b):
        self.bot = b

    @commands.command(aliases=["현재"])
    async def current(self, ctx: commands.context.Context):
        await ctx.send(embed=embed_current(ctx))

    @commands.command(aliases=["나"])
    async def me(self, ctx: commands.context.Context):
        await ctx.send(embed=embed_me(ctx))

    @commands.command(aliases=["조회"])
    async def search(self, ctx: commands.context.Context, str_time: str):
        await ctx.send(embed=embed_date(ctx, str_time))


def set_server_author(ctx: commands.context.Context, embed: Embed):
    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
    return embed


def set_user_author(ctx: commands.context.Context, embed: Embed):
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    return embed


def embed_all(ctx: commands.context.Context) -> Embed:
    res = db.get_all()
    description = ""

    for user_id, display_name, io, t in res:
        description += f"**{datetime.fromtimestamp(int(t), tz=UTC).astimezone(KST).strftime('%Y/%m/%d %H:%M:%S')}** `{io.upper()}` {display_name}\n"

    embed = Embed(title="Visitor Logs", color=Color.dark_teal(), description=description)
    return embed


def embed_current(ctx: commands.context.Context, title="Status quo") -> Embed:
    res = db.current_all()
    if len(res) == 0:
        embed = Embed(title=title, color=Color.red(), description="No one is here.")
        return set_server_author(ctx, embed)

    embed = Embed(title=title, color=Color.blue())

    for key, value in res.items():
        embed.add_field(
            name=value["display_name"],
            value=datetime.fromtimestamp(value["in"], tz=UTC).astimezone(KST).strftime("%Y/%m/%d %H:%M:%S")
        )

    return set_server_author(ctx, embed)


def embed_me(ctx: commands.context.Context) -> Embed:
    res = db.get_by_user_id(ctx.author.id)
    if len(res) == 0:
        embed = Embed(title="Status quo", color=Color.red(), description="No one is here.")
        return set_user_author(ctx, embed)

    embed = Embed(title="Status quo", color=Color.blue())

    for user_id, display_name, io, t in res:
        embed.add_field(
            name=io,
            value=datetime.fromtimestamp(int(t), tz=UTC).astimezone(KST).strftime("%Y/%m/%d %H:%M:%S"),
            inline=False
        )

    return set_user_author(ctx, embed)


def embed_date(ctx: commands.context.Context, str_time: str) -> Embed:
    if str_time == "모두" or str_time == "all":
        return embed_all(ctx)

    if not re.match(r"^\d\d\d\d-\d\d-\d\d$", str_time):
        return Embed(title=f"Invalid Query!", color=Color.red(), description=f"**{str_time}** is the wrong format. Use it as `!조회 {datetime.now().strftime('%Y-%m-%d')}`")

    res = db.get_by_date(str_time)
    if len(res) == 0:
        embed = Embed(title=f"{str_time}", color=Color.red(), description=f"There was no one.")
        return set_server_author(ctx, embed)

    embed = Embed(title=f"{str_time}", color=Color.blue())

    for user_id, display_name, io, t in res:
        embed.add_field(
            name=datetime.fromtimestamp(int(t), tz=UTC).astimezone(KST).strftime("%H:%M:%S"),
            value=f"`{io.upper()}` {display_name}",
            inline=False
        )

    return set_server_author(ctx, embed)


db: Database = Database("visitorLog")

bot = commands.Bot(
    command_prefix="!",
    description="I am simple visitor-log-bot for discord 🤖",
    help_command=HelpCommand()
)

bot.add_cog(Visit(bot))
bot.add_cog(Search(bot))

KST = timezone(timedelta(hours=9))
UTC = timezone(timedelta(hours=0))


@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)

if __name__ == "__main__":
    bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
