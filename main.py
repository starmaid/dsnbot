# destiny assistant bot for my destiny server
# author Nicky (@starmaid#6925)
# created 05/06/2020
# edited 05/07/2020
# edited 11/27/2020: added aternos functions
# version 1.1

import discord
from datetime import datetime, timezone, timedelta
from dateutil import parser
import asyncio
from discord.ext import commands
import random
from random import choice
from connect_and_launch import get_status, get_number_of_players
from connect_and_launch import connect_account, quitBrowser, get_server_info
from connect_and_launch import start_server, stop_server

class Bot(commands.Bot):
    phrases = [
        'dsn'
    ]
    replies = [
        '`STATUS: GOOD`'
    ]

    activity = 'comms monitor ./help'
    logoff_msg = 'logging off'

    def __init__(self):
        # This is the stuff that gets run at startup
        super().__init__(command_prefix='./',self_bot=False,activity=discord.Game(self.activity))
        self.remove_command('help')
        self.add_command(self.help)
        self.add_command(self.quit)
        self.add_command(self.launch)
        self.add_command(self.players)
        self.add_command(self.status)
        self.add_command(self.stop)
        self.read_token()

        if self.token is not None:
            super().run(self.token)
        else:
            pass

    def read_token(self):
        self.token = None
        try:
            with open('./token.txt','r') as fp:
                self.token = fp.readlines()[0].strip('\n')
        except:
            print('Token file not found')

    async def on_ready(self):
        connect_account()  # logs into aternos
        await asyncio.sleep(2)
        print('Logged on with aternos')


    @commands.command(pass_context=True)
    async def help(ctx):
        #this is the help command.
        help_msg = '```<./> DSN BOT <./>\n' + \
            'a discord bot to communicate with space probes ' + \
            'at lightpseed' + \
            '\nusage:          ./command [params]*' + \
            '\n --- availible commands ---' + \
            '\n./help                shows this message' + \
            '\n./quit                shuts down the bot (only works for starmaid)' + \
            '\n./info                gives server information'
            '\n./launch              starts the aternos minecraft server' + \
            '\n./status              shows status of aternos minecraft server' + \
            '\n./players             shows current players in aternos minecraft server' + \
            '\n./stop                stops aternos minecraft server' + \
            '```'
        await ctx.send(help_msg)
        return


    @commands.command(pass_context=True)
    async def quit(ctx):
        # quits the bot.
        if str(ctx.message.author) == 'starmaid#6925':
            await ctx.send(ctx.bot.logoff_msg)
            await ctx.bot.close()
        else:
            await ctx.send('`you do not have permission to shut me down.`')
        return

    @commands.command(pass_context=True)
    async def launch(ctx):
        # launches aternos
        await ctx.message.channel.send("Launching Server...")
        status = get_status()

        if status == "Offline":
            await start_server()
            author = message.author
            # loops until server has started and pings person who launched
            while True:
                await asyncio.sleep(5)
                if get_status() == "Online":
                    await message.channel.send(f"{author.mention}, the "
                                               f"server has started!")
                    break
        
        elif status == "Online":
            await ctx.message.channel.send("The server is already Online")
        
        elif status == 'Starting ...' or status == 'Loading ...':
            text = "The server is already starting..."
            await message.channel.send(text)

        elif status == 'Stopping ...' or status == 'Saving ...':
            text = "The server is stopping. Please wait."
            await message.channel.send(text)
        
        else:
            text = "An error occurred. Either the status server is not " \
                    "responding or you didn't set the server name " \
                    "correctly.\n\nTrying to launch the server anyways."
            await message.channel.send(text)
            await start_server()


    @commands.command(pass_context=True)
    async def status(ctx):
        # status of aternos
        await ctx.message.channel.send("Getting status...")
        status = get_status()
        await ctx.message.channel.send("The server is {}".format(status))


    @commands.command(pass_context=True)
    async def players(ctx):
        # launches aternos
        await ctx.message.channel.send("Getting players...")
        text = f"There are {get_number_of_players()} players online."
        await message.channel.send(text)

    
    @commands.command(pass_context=True)
    async def info(ctx):
        ip, status, players, software, version = get_server_info()
        text = f"**IP:** {ip} \n**Status:** {status} \n**Players: " \
                f"**{players} \n**Version:** {software} {version}"
        embed = discord.Embed()
        embed.add_field(name="Server Info", value=text, inline=False)
        await message.channel.send(embed=embed)

    
    @commands.command(pass_context=True)
    async def stop(ctx):
        # launches aternos
        await message.channel.send("Stopping the server.")
        status = get_status()

        if status != 'Stopping ...' or status != 'Saving ...':
            await stop_server()

        else:
            await message.channel.send("The server is already Offline.")



if __name__ == '__main__':
    Bot()
