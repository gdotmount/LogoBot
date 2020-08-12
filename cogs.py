import discord
import asyncio
from discord.ext import commands
from discord.utils import get
class Listeners(commands.Cog):
    def __init__(self, bot, connection, cursor):
        self.bot = bot
        self.connection = connection
        self.cursor = cursor

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logobot is logged in and ready to lock and load.')

        # Check if Logobot is still a member of a guild or if the verification channel and/or verification roles have been deleted
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE;'"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for table in results:
            table = table[0]
            sql = "SELECT verifiedrole, unverifiedrole, unverifiedchannel from %s where userid = 0;"
            self.cursor.execute(sql)
            results2 = self.cursor.fetchall()[0]
            verifiedrole = results2[0]
            unverifiedrole = results2[1]
            unverifiedchannel = results[2]
            id = int(table[slice(1, len(table))])
            guild = self.bot.get_guild(id)
            if(guild.get_member(692453391091368017) is None):
                await self.on_guild_remove(guild)
            else:
                if(guild.get_role(verifiedrole) is None):
                    sql = "update s%d set verifiedrole = NULL where userid = 0;" % guild.id
                    self.cursor.execute(sql)
                    self.connection.commit()
                if(guild.get_role(unverifiedrole) is None):
                    sql = "update s%d set unverifiedrole = NULL where userid = 0;" % guild.id
                    self.cursor.execute(sql)
                    self.connection.commit()
                if(guild.get_channel(unverifiedchannel) is None):
                    sql = "update s%d set unverifiedchannel = NULL where userid = 0;" % guild.id
                    self.cursor.execute(sql)
                    self.connection.commit()

    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        sql = "DROP TABLE s%d CASCADE;" % guild.id
        self.cursor.execute(sql)
        self.connection.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        sql = "select unverifiedchannel from s%d where userid = 0;" % message.guild.id
        self.cursor.execute(sql)
        unverifiedchannel = self.cursor.fetchall()[0][0]
        if(message.channel == unverifiedchannel):
            if(self.bot.user == message.author):
                await message.delete(5)
            else: await message.delete()
        else:
            if self.bot.user == message.author:
                return
            if message.content == 'ping':
                await message.channel.send('pong')
        await self.bot.process_commands(message)

    @commands.bot_has_guild_permissions(manage_channels=True)
    async def initchannel(self, guild):
        sql = "select verifiedrole, unverifiedrole from s%d where userid = 0;" % guild.id
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        verifiedrole = results[0][0]
        unverifiedrole = results[0][1]

        overwrites = {
                guild.me: discord.PermissionOverwrite(read_messages=True),
                guild.get_role(verifiedrole): discord.PermissionOverwrite(read_messages=False),
                guild.get_role(unverifiedrole): discord.PermissionOverwrite(read_messages=True)
                }
        channel = guild.create_text_channel("Verification", overwrites=overwrites)

        sql = "update s%d set unverifiedchannel = %d where userid = 0;" % (guild.id, channel.id)
        self.cursor.execute(sql)
    
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def initroles(self, guild):
        guild.create_role()


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        sql = "CREATE TABLE IF NOT EXISTS s%d (domain varchar(100), verifiedrole bigint, unverifiedrole bigint, unverifiedchannel bigint, userid BIGINT PRIMARY KEY, code INT, tagline varchar(100), verified BOOLEAN);" % guild.id
        self.cursor.execute(sql)
        sql = "INSERT INTO s%d (domain, userid) VALUES('@gmail.com', 0);" & guild.id
        self.cursor.execute(sql)
        for member in guild.members:
            sql = 'INSERT INTO s%d (userid, verified) VALUES(%d, TRUE);' % (guild.id, member.id)
            self.cursor.execute(sql)
        try:
            await self.initroles(guild)
            try: await self.initchannel(guild)
            except PermissionError: guild.owner.send("It seems that I don't have permission to create channels, which means you (or an admin) will either need to give me that permission and call the 'initializechannel' command or manually set a channel for verification and call the 'setchannel' command for it.")
        except PermissionError: guild.owner.send("It seems that I don't have permission to manage roles, which means you (or an admin) will either need to give me that permission and call the 'initializeroles' command or manually set the verified and (optionally) unverified roles with the 'setrole' command. You may also need to do the same for the verification channel.")
        finally: self.connection.commit()
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        sql = "select verifiedrole, unverifiedrole from s%d where userid = 0;" % role.guild.id
        self.cursor.execute(sql)
        results = self.cursor.fetchall()[0]
        unverifiedrole = results[1]
        verifiedrole = results[0]
        if(role.id == unverifiedrole):
            sql = "update s%d set unverifiedrole = NULL where userid = 0;" % role.guild.id
            self.cursor.execute(sql)
            self.connection.commit()
        if(role.id == verifiedrole):
            sql = "update s%d set verifiedrole = NULL where userid = 0;" % role.guild.id
            self.cursor.execute(sql)
            self.connection.commit()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        sql = "select unverifiedchannel from s%d where userif = 0;" % channel.guild.id
        self.cursor.execute(sql)
        unverifiedchannel = self.cursor.fetchall()[0][0]
        if(channel.id == unverifiedchannel):
            sql = "update s%d set unverified channel = NULL where userid = 0;"
            self.cursor.execute(sql)
            self.connection.commit()

class AdminCommands(commands.Cog):
    def __init__(self, bot, connection, cursor):
        self.bot = bot
        self.connection = connection
        self.cursor = cursor

    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.command()
    async def initializechannel(self, ctx, name = 'Verification'):
        sql = "select verifiedrole, unverifiedrole from s%d where userid = 0;"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()[0]
        verifiedrole = results[0]
        unverifiedrole = results[1]

        if(not ctx.channel.permissions_for(ctx.author).administrator):
            ctx.send('You are not authorized to use this command as it is restricted to administrators.')
            return
        if(verifiedrole is None):
            ctx.send("A role for verification must be designated with either the 'initializeroles' command or the 'setrole' command. A role for unverified users is optional.")
            return

        if(unverifiedrole is None):
            overwrites = {
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                ctx.guild.get_role(verifiedrole): discord.PermissionOverwrite(read_messages=False)
            }
            channel = ctx.guild.create_text_channel(name, overwrites=overwrites)
        else:
            overwrites = {
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                ctx.guild.get_role(verifiedrole): discord.PermissionOverwrite(read_messages=False),
                ctx.guild.get_role(unverifiedrole): discord.PermissionOverwrite(read_messages=True)
                }
            channel = ctx.guild.create_text_channel(name, overwrites=overwrites)
        sql = "update s%d set unverifiedchannel = %d where userid = 0;" % (ctx.guild.id, channel.id)
        self.cursor.execute(sql)
        self.connection.commit()

    @initializechannel.error
    async def ichannel_error(self, ctx, error):
        if isinstance(error, PermissionError):
            await ctx.send('I do not have permission to do that. I need to be granted the "Manage Channels" permission. Or, you can manually create a channel for verification and user the "setchannel" command.')

    @commands.command()
    async def setdomain(self, ctx, domain):
        if(ctx.channel.permissions_for(ctx.author).administrator):
            sql = "UPDATE s%d SET domain = '%s' where userid = 0;" % (ctx.guild.id, domain)
            self.cursor.execute(sql)
            self.connection.commit()

            sql = 'SELECT domain FROM s%d where userid = 0;' % ctx.guild.id
            self.cursor.execute(sql)
            print(f'New domain for server "{ctx.guild.name}": ' + domain)
        else: ctx.send('You are not authorized to use this command as it is restricted to administrators.')