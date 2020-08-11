import os
import random
import psycopg2
import discord
import smtplib
import verificationemails
from cogs import Listeners, AdminCommands
from discord.ext import commands

connection = psycopg2.connect(
    user = os.environ['DATABASE_USER'], 
    password = os.environ['DATABASE_PASS'], 
    host = os.environ['DATABASE_HOST'], 
    database = os.environ['DATABASE'], 
    port = 5432)
cursor = connection.cursor()
bot = commands.Bot(command_prefix='.')

@bot.command()
async def confirm(ctx, tag):
    exists = False
    sql = 'select domain, verifiedrole, unverifiedrole, unverifiedchannel from s%d where userid = 0;' % ctx.guild.id
    cursor.execute(sql)
    results = cursor.fetchall()
    domain = results[0][0][0]
    verifiedrole = results[1][0][0]
    unverifiedrole = results[2][0][0]
    unverifiedchannel = results[3][0][0]

    if(ctx.channel.id == unverifiedchannel):
        sql = 'SELECT userid, code, tagline, verified FROM s%d;' % (ctx.guild.id)
        cursor.execute(sql)
        results = cursor.fetchall()

        for row in results:
            if(ctx.author.id == row[0]):
                if(tag == str(row[1]) and not row[3]):
                    try:
                        role = ctx.guild.get_role(verifiedrole)
                        await ctx.author.add_roles(role)
                        if(unverifiedrole is not None):
                            try:
                                role = ctx.guild.get_role(unverifiedrole)
                                await ctx.author.remove_role(role)
                            except: await ctx.send('Your code was correct, and you have been given the designated verified role; it seems you already lost your unverified role, so I am angry because I wanted to remove that from you.')
                    except:
                        await ctx.send('Your code was correct, but an administrator must specify a verified role to be given upon verification with either the "setverifiedrole" command or the "initializeroles" command.')
                        await ctx.send('Once a verified role is specified, you will ')
                    finally:
                        sql = "update s%d set verified = TRUE where userid = %d;" % (ctx.guild.id, ctx.author.id)
                        cursor.execute(sql)
                        connection.commit()
                elif(row[3]):
                    await ctx.send('You are already verified dummy.')
                    await ctx.send('jesus i sound like dr berger')
                else:
                    code = row[1]
                    receiver = f'{tag}{domain}'
                    await ctx.send(f"Resending verification code to {receiver}")
                    if(tag != row[2]):
                        sql = "update s%d set tagline = '%s' where userid = %d;" % (ctx.guild.id, tag, ctx.author.id)
                        cursor.execute(sql)
                        connection.commit()
                    if(code is None):
                        code = random.randint(100000, 999999)
                        sql = "update s%d set code = %d where userid = %d;" % (ctx.guild.id, code, ctx.author.id)
                        cursor.execute(sql)
                        connection.commit()
                    await verificationemails.send_email(receiver, ctx, code)
                exists = True
                break
        if(exists == False):
            code = random.randint(100000, 999999)
            print(code)
            sql = "INSERT INTO s%d(userid, code, tagline, verified) VALUES(%d, %d, '%s', FALSE);" % (ctx.guild.id, ctx.author.id, code, tag)
            cursor.execute(sql)
            connection.commit()
            receiver = f'{tag}{domain}'
            await ctx.send(f'Sending verification code to {receiver}')
            await verificationemails.send_email(receiver, ctx, code)
    else:
        ctx.send('This command is not meant for this channel.')
        try: ctx.send('This command is meant for the channel: %s' % ctx.guild.get_channel(unverifiedchannel).name)
        except: ctx.send('Furthermore, an administrator must specify a dedicated channel for unverified users to use this command with either the "setchannel" command or the "initializechannel" command.')

@bot.command()
async def test(ctx):
    sql = 'UPDATE s%d SET verified = False WHERE userid = %d;' % (ctx.guild.id, ctx.author.id)
    cursor.execute(sql)
    connection.commit()

bot.add_cog(Listeners(bot, connection, cursor))
bot.add_cog(AdminCommands(bot, connection, cursor))
bot.run(os.environ['BOT_TOKEN'])
