# destiny assistant bot for my destiny server
# author Nicky (@starmaid#6925)
# created 05/06/2020
# edited 05/07/2020
# version 1.0

import discord
from datetime import datetime, timezone, timedelta
from dateutil import parser
import asyncio
from discord.ext import commands
import random
from random import choice



class Bot(commands.Bot):
    phrases = [
        'dsn'
    ]
    replies = [
        '`STATUS: GOOD`'
    ]

    activity = 'comms monitor'
    logoff_msg = 'logging off'

    def __init__(self):
        # This is the stuff that gets run at startup
        super().__init__(command_prefix='..',self_bot=False,activity=discord.Game(self.activity))
        self.remove_command('help')
        self.add_command(self.help)
        self.add_command(self.quit)
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
        print('Logged on')


    @commands.command(pass_context=True)
    async def help(ctx):
        print("help")
        #this is the help command.
        help_msg = '```<..> DSN BOT <..>\n' + \
            'a discord bot to communicate with space probes ' + \
            'at lightpseed' + \
            '\nusage:          ..command [params]*' + \
            '\n --- availible commands ---' + \
            '\n..help                               shows this message' + \
            '\n..quit                               shuts down the bot (only works for starmaid)' + \
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


if __name__ == '__main__':
    Bot()
