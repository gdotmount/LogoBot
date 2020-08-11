import discord
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user == message.author:
            return
        if message.content == 'ping':
            await message.channel.send('pong')
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        sql = "CREATE TABLE IF NOT EXISTS s%d (domain varchar(100), userid BIGINT PRIMARY KEY, code INT, tagline varchar(100), verified BOOLEAN);" % guild.id
        self.cursor.execute(sql)
        sql = "INSERT INTO s%d (domain, userid) VALUES('@gmail.com', 0);" & guild.id
        self.cursor.execute(sql)
        for member in guild.members:
            sql = 'INSERT INTO s%d (userid, verified) VALUES(%d, TRUE);' % (guild.id, member.id)
            self.cursor.execute(sql)
        self.connection.commit()
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        sql = "select unverifiedrole from s%d where userid = 0;" % role.guild.id
        self.cursor.execute(sql)
        unverifiedrole = self.cursor.fetchall()[0][0]
        if(role.id == unverifiedrole):
            sql = "update s%d set unverifiedrole = NULL where userid = 0;" % role.guild.id
            self.cursor.execute(sql)
            self.connection.commit()

class AdminCommands(commands.Cog):
    def __init__(self, bot, connection, cursor):
        self.bot = bot
        self.connection = connection
        self.cursor = cursor

    @commands.command()
    async def initializechannel(self, ctx, name = 'Verification', ):
        if(ctx.channel.permissions_for(ctx.author).administrator):
            try:
                overwrites = {
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
                    ctx.guild.get_role(): discord.PermissionOverwrite(read_messages=False),
                    ctx.guild.get_role(): discord.PermissionOverwrite(read_messages=True)
                    }
                ctx.guild.create_text_channel(name, overwrites=overwrites)
            except:
                ctx.send('There was an error; an admin may need to give this bot permission to create channels.')
        else: ctx.send('You are not authorized to use this command as it is restricted to administrators.')

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