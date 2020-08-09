import json
import os
import psycopg2
import discord
from discord.ext import commands

connection = psycopg2.connect(
    user = os.environ['DATABASE_USER'], 
    password = os.environ['DATABASE_PASS'], 
    host = os.environ['DATABASE_HOST'], 
    database = os.environ['DATABASE'], 
    port = 5432)
bot = commands.Bot(command_prefix='.')
script_dir = os.path.dirname(__file__)

@bot.event
async def on_ready():
    print('Logobot is logged in and ready to lock and load.')

@bot.event
async def on_message(message):
    if bot.user == message.author:
        return
    if message.content == 'ping':
        await message.channel.send('pong')
    await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
    rel_dir = f'server-specific-data/{guild.id}.json'
    json_str = '{"domain": "@gmail.com", "users": []}'
    data = json.loads(json_str)
    with open(os.path.join(script_dir, rel_dir), 'w') as f:
        f.seek(0)
        json.dump(data, f)
        f.truncate()

@bot.command()
async def confirm(ctx, tagline):
    await ctx.send('boop')
    
@bot.command()
async def setdomain(ctx, domain):
    rel_dir = f'server-specific-data/{ctx.guild.id}.json'
    with open(os.path.join(script_dir, rel_dir), 'r+') as f:
        data = json.load(f)
        data['domain'] = domain
        f.seek(0)
        json.dump(data, f)
        f.truncate()

bot.run(os.environ['BOT_TOKEN'])
