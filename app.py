import os
import random
import psycopg2
import verificationemails
from cogs import Listeners, AdminCommands
from discord.ext import commands

connection = psycopg2.connect(
    user=os.environ['DATABASE_USER'],
    password=os.environ['DATABASE_PASS'],
    host=os.environ['DATABASE_HOST'],
    database=os.environ['DATABASE'],
    port=5432)
cursor = connection.cursor()
bot = commands.Bot(command_prefix='.')


@bot.command()
async def confirm(ctx, tag):
    exists = False
    sql = 'select domain, verifiedrole, unverifiedrole, unverifiedchannel from s%d where userid = 0;' % ctx.guild.id
    cursor.execute(sql)
    results = cursor.fetchall()[0]
    domain = results[0]
    verifiedrole = results[1]
    unverifiedrole = results[2]
    unverifiedchannel = results[3]

    if verifiedrole is None:
        await ctx.send(
            'An administrator must specify a verified role to be given upon verification with either the '
            '"setverifiedrole" command or the "initializeroles" command.')
        return
    elif unverifiedchannel is None:
        await ctx.send(
            'An administrator must specify a dedicated channel for unverified users to use this command with either '
            'the "setchannel" command or the "initializechannel" command.')
        return
    elif ctx.channel.id != unverifiedchannel:
        await ctx.send('This command is meant for unverified users in the channel: %s' % ctx.guild.get_channel(
            unverifiedchannel).name)
        return

    sql = 'SELECT userid, code, tagline, verified FROM s%d;' % ctx.guild.id
    cursor.execute(sql)
    results = cursor.fetchall()

    for row in results:
        if ctx.author.id == row[0]:
            if tag == str(row[1]) and not row[3]:
                role = ctx.guild.get_role(verifiedrole)
                await ctx.author.add_roles(role)
                if unverifiedrole is not None:
                    role = ctx.guild.get_role(unverifiedrole)
                    if role in ctx.author.roles:
                        await ctx.author.remove_roles(role)
                sql = "update s%d set verified = TRUE where userid = %d;" % (ctx.guild.id, ctx.author.id)
                cursor.execute(sql)
                connection.commit()
            elif row[3]:
                role = ctx.guild.get_role(verifiedrole)
                if role in ctx.author.roles:
                    await ctx.send('You are already verified dummy.')
                    await ctx.send('jesus i sound like dr berger')
                else:
                    await ctx.author.add_roles(role)
                    await ctx.send('I verified you again.')
                if unverifiedrole is not None:
                    role = ctx.guild.get_role(unverifiedrole)
                    if role in ctx.author.roles:
                        await ctx.author.remove_roles(role)
            else:
                code = row[1]
                receiver = f'{tag}{domain}'
                await ctx.send(f"Resending verification code to {receiver}")
                if tag != row[2]:
                    sql = "update s%d set tagline = '%s' where userid = %d;" % (ctx.guild.id, tag, ctx.author.id)
                    cursor.execute(sql)
                    connection.commit()
                if code is None:
                    code = random.randint(100000, 999999)
                    sql = "update s%d set code = %d where userid = %d;" % (ctx.guild.id, code, ctx.author.id)
                    cursor.execute(sql)
                    connection.commit()
                await verificationemails.send_email(receiver, ctx, code)
            exists = True
            break
    if not exists:
        code = random.randint(100000, 999999)
        print(code)
        sql = "INSERT INTO s%d(userid, code, tagline, verified) VALUES(%d, %d, '%s', FALSE);" % (
            ctx.guild.id, ctx.author.id, code, tag)
        cursor.execute(sql)
        connection.commit()
        receiver = f'{tag}{domain}'
        await ctx.send(f'Sending verification code to {receiver}')
        await verificationemails.send_email(receiver, ctx, code)


@bot.command()
async def test(ctx):
    sql = 'UPDATE s%d SET verified = False WHERE userid = %d;' % (ctx.guild.id, ctx.author.id)
    cursor.execute(sql)
    connection.commit()


bot.add_cog(Listeners(bot, connection, cursor))
bot.add_cog(AdminCommands(bot, connection, cursor))
bot.run(os.environ['BOT_TOKEN'])
