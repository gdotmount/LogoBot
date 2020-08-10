import os
import random
import psycopg2
import discord
from discord.ext import commands
from discord.utils import get

connection = psycopg2.connect(
    user = os.environ['DATABASE_USER'], 
    password = os.environ['DATABASE_PASS'], 
    host = os.environ['DATABASE_HOST'], 
    database = os.environ['DATABASE'], 
    port = 5432)
cursor = connection.cursor()
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
    sql = "CREATE TABLE IF NOT EXISTS s%d (domain varchar(100), userid BIGINT PRIMARY KEY, code INT, tagline varchar(100), verified BOOLEAN);" % guild.id
    cursor.execute(sql)
    sql = "INSERT INTO s%d (domain, userid) VALUES('@gmail.com', 0);" & guild.id
    cursor.execute(sql)
    for member in guild.members:
        sql = 'INSERT INTO s%d (userid, verified) VALUES(%d, TRUE);' % (guild.id, member.id)
        cursor.execute(sql)
    connection.commit()

@bot.command()
async def initdb(ctx):
    sql = "CREATE TABLE IF NOT EXISTS s%d (domain varchar(100), userid BIGINT PRIMARY KEY, code INT, tagline varchar(100), verified BOOLEAN);" % ctx.guild.id
    cursor.execute(sql)
    sql = "INSERT INTO s%d (domain, userid) VALUES('@gmail.com', 0);" % ctx.guild.id
    cursor.execute(sql)
    for member in ctx.guild.members:
        sql = 'INSERT INTO s%d (userid, verified) VALUES(%d, TRUE);' % (ctx.guild.id, member.id)
        cursor.execute(sql)
    connection.commit()

@bot.command()
async def confirm(ctx, tag):
    sql = 'select domain from s%d where userid = 0' % ctx.guild.id
    cursor.execute(sql)
    domain = cursor.fetchall()[0][0]
    sql = 'SELECT * FROM s%d' % (ctx.guild.id)
    cursor.execute(sql)
    results = cursor.fetchall()
    exists = False
    for row in results:
        if(ctx.author.id == row[1]):
            if(tag == str(row[2]) and not row[4]):
                try:
                    role = get(ctx.guild.roles, name="Verified")
                    await ctx.author.add_roles(role)
                except:
                    await ctx.send('Your code was correct, but Logobot encountered an error.')
                    message = '''A server admin must specify a verified role to be given upon verification since the default role that Logobot creates upon joining does not exist.'''
                    await ctx.send(message)
            elif(not row[4]):
                await ctx.send(f"Resending verification code to {tag}{domain}")
                if(tag != row[2]):
                    sql = "update s%d set tagline = '%s' where userid = %d" % (ctx.guild.id, tag, ctx.author.id)
                    cursor.execute(sql)
                    connection.commit()
            elif(row[4]):
                await ctx.send('You are already verified dummy.')
                await ctx.send('jesus i sound like dr berger')
            exists = True
            break
    if(exists == False):
        code = random.randint(100000, 999999)
        print(code)
        sql = "INSERT INTO s%d(userid, code, tagline, verified) VALUES(%d, %d, '%s', FALSE);" % (ctx.guild.id, ctx.author.id, code, tag)
        cursor.execute(sql)
        connection.commit()
        await ctx.send(f'Sending verification code to {tag}{domain}')
    
@bot.command()
async def setdomain(ctx, domain):
    sql = "UPDATE s%d SET domain = '%s' where userid = 0;" % (ctx.guild.id, domain)
    cursor.execute(sql)
    connection.commit()

    sql = 'SELECT domain FROM s%d where userid = 0' % ctx.guild.id
    cursor.execute(sql)
    results = cursor.fetchall()
    print(f'New domain for server "{ctx.guild.name}": ' + str(results))
   
@bot.command()
async def test(ctx):
    return

bot.run(os.environ['BOT_TOKEN'])
