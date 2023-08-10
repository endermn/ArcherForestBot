import discord
from discord import app_commands
from typing import List
import datetime
import asyncio
from discord.ext import tasks, commands
import time

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

TEXT_CHANNEL_ID = 1131166841587376128
nearest = None
version = "1.1.0"

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    loop.start()
    await client.tree.sync()

def get_nearest(items, date):
    return min(items, key=lambda x: x - date)

@tasks.loop(seconds=1)
async def loop():
    global TEXT_CHANNEL_ID, nearest
    
    morning_boss_time = datetime.datetime.now().replace(hour=5,minute=49,second=0,microsecond=0)
    day_boss_time = datetime.datetime.now().replace(hour=13,minute=49,second=0,microsecond=0)
    night_boss_time = datetime.datetime.now().replace(hour=21,minute=49,second=0,microsecond=0)
    
    if datetime.datetime.now() > morning_boss_time:
        morning_boss_time = morning_boss_time + datetime.timedelta(days=1)
    if datetime.datetime.now() > day_boss_time:
        day_boss_time = day_boss_time + datetime.timedelta(days=1)
    if datetime.datetime.now() > night_boss_time:
        night_boss_time = night_boss_time + datetime.timedelta(days=1)

    nearest = get_nearest([morning_boss_time, day_boss_time, night_boss_time], datetime.datetime.now())

    while True:
        
        now = datetime.datetime.now()
        
        if nearest <= now:
            if TEXT_CHANNEL_ID != None:
                await client.get_channel(TEXT_CHANNEL_ID).send('@everyone The world boss is spawning <t:' + str(int(time.time() + 600)) + ':R>')
            break
        await asyncio.sleep(5)


@client.event
async def on_message(message):
    global TEXT_CHANNEL_ID, nearest  

    if message.author == client.user:
        return

    if message.content.startswith('!setTimer'):
        TEXT_CHANNEL_ID = message.channel.id
        await message.channel.send("Timer channel set!")
        
    if message.content == '!purge':
        await message.channel.purge(limit=20)
        await message.channel.send("purged 20 messages")
        await asyncio.sleep(5)
        await message.channel.purge(limit=1)
        
    if message.content.startswith('!purgeall'):
        await message.channel.purge(limit = 10000000)
        await message.channel.send("purged all")
        await asyncio.sleep(5)
        await message.channel.purge(limit=1)
    
    if message.content.startswith('!nearestBoss'):
        time_diff = int(nearest.timestamp() + 600)
        await message.channel.send("Nearest world boss is at " + (nearest + datetime.timedelta(minutes=10)).strftime("%H:%M") + " or <t:" + str(time_diff) + ":R>")
    
    if message.content.startswith("!status"):
        await message.channel.send("online")
    

@client.tree.command(name="status")
async def status(ctx: discord.Interaction):
    await ctx.response.send_message(embed=discord.Embed(title="Bot Status", description=":white_check_mark: Online", color=discord.Colour.brand_green()))
@client.tree.command(name="epochtime")
@app_commands.describe(amount = "in how much time")
async def epoch_time(ctx: discord.Interaction, amount: int):
    await ctx.response.send_message(embed=discord.Embed(title="Time", color=discord.Colour.brand_green(), description=":alarm_clock: The epoch time in " + str(amount) + "s is " + str(int(datetime.datetime.now().timestamp() + amount))))
@client.tree.command(name="nearestboss")
async def boss(ctx: discord.Interaction):
    time_diff = int(nearest.timestamp() + 600)
    await ctx.response.send_message(embed=discord.Embed(title="Next Boss",color=discord.Colour.brand_green(), description=":bat: Nearest world boss is at " + (nearest + datetime.timedelta(minutes=10)).strftime("%H:%M") + " or <t:" + str(time_diff) + ":R>"))
@client.tree.command(name="changelog")
async def change_log(ctx: discord.Interaction):
    await ctx.response.send_message(embed=discord.Embed(title="Change log " + version, color=discord.Colour.brand_green(), description='• added bunch of slash commands \n • fixed some bugs \n • changed embed colours'))

def guild_drop_rates(tier: discord.app_commands.Choice[str]):
    description_embed = None
    match tier.value:
        case "ancient":
            description_embed = open("guild_boss_rates/guild_boss_ancient.txt", "r").read()
        case "leg":
            description_embed = open("guild_boss_rates/guild_boss_leg.txt", "r").read()
        case "s":
            description_embed = open("guild_boss_rates/guild_boss_s.txt", "r").read()
        case "a":
            description_embed = open("guild_boss_rates/guild_boss_a.txt", "r").read()
        case "b":
            description_embed = open("guild_boss_rates/guild_boss_b.txt", "r").read()
        case "c":
            description_embed = open("guild_boss_rates/guild_boss_c.txt", "r").read()
        case "d":
            description_embed = open("guild_boss_rates/guild_boss_d.txt", "r").read()
    return description_embed


@client.tree.command(name="guildrates")
@app_commands.choices(tier=[
    app_commands.Choice(name="Ancient", value="ancient"),
    app_commands.Choice(name="Legendary", value="leg"),
    app_commands.Choice(name="S", value="s"),
    app_commands.Choice(name="A", value="a"),
    app_commands.Choice(name="B", value="b"),
    app_commands.Choice(name="C", value="c"),
    app_commands.Choice(name="D", value="d"),
])
async def drop_rates(ctx: discord.Interaction, tier: discord.app_commands.Choice[str]):
    description_embed = guild_drop_rates(tier=tier)
    await ctx.response.send_message(embed=discord.Embed(title="Guild Boss Reward Rates", color=discord.Colour.brand_red(), description=description_embed))
    
@client.tree.command(name="bows")
@app_commands.choices(choices=[
    app_commands.Choice(name="How to obtain Bows", value="obtain_bows.txt"),
    app_commands.Choice(name="Bow Pull Rates", value="bow_pull_rates.txt"),
    app_commands.Choice(name="Upgrades", value="bow_upgrades.txt"),
    app_commands.Choice(name="Bows", value="bows.txt"),
    app_commands.Choice(name="Bow Types", value="bow_types.txt"),
    app_commands.Choice(name="Bow Grades", value="bow_grades.txt"),
])
async def bows(ctx: discord.Interaction, choices: discord.app_commands.Choice[str]):
    desc = open("bows/" + choices.value, "r").read()
    await ctx.response.send_message(embed=discord.Embed(title="Bows", description=desc, color=discord.Colour.brand_red()))

@client.tree.command(name="archermines")
@app_commands.choices(choices=[
    app_commands.Choice(name="Bow Depth", value="bow_depth.txt")
])
async def archer_mines(ctx: discord.Interaction, choices: app_commands.Choice[str]):
    desc = open("archer_mines/" + choices.value, "r").read()
    await ctx.response.send_message(embed=discord.Embed(title=choices.name, description=desc, color=discord.Colour.brand_red()))

@client.tree.command(name="resets")
@app_commands.choices(choices=[
    app_commands.Choice(name="Competition Reset", value="competition_reset.txt"),
    app_commands.Choice(name="Daily Game Reset", value="daily_reset.txt"),
    app_commands.Choice(name="Seasonal Event Reset", value="seasonal_reset.txt"),
    app_commands.Choice(name="Weekly Game Reset", value="weekly_reset.txt"),
])
async def resets(ctx: discord.Interaction, choices: discord.app_commands.Choice[str]):
    desc = open("game_resets/" + choices.value, "r").read()
    await ctx.response.send_message(embed=discord.Embed(title=choices.name, description=desc, color=discord.Colour.brand_red()))
    

client.run('MTEzMDk0NDQzMjU0MDI0MTkzMA.GxqFY7.ZM96GcxOJqej2Skic0UYSegiepNG4mlMnp_1BQ')
