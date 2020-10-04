# main for deep space network, a 17776 bot
# author Nicky (@starmaid#6925)
# created 10/3/2020
# edited NA
# version 1.0

import discord
from discord.ext import commands
import random
from random import choice

class Bot(commands.Bot):
    phrases = [
        'DSN'
    ]
    replies = [
        '`STATUS: GOOD`'
    ]

    activity = 'comms monitor'
    logoff_msg = 'logging off'

    def __init__(self):
        # This is the stuff that gets run at startup
        super().__init__(command_prefix='>',self_bot=False,activity=discord.Game(self.activity))
        random.seed()
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
            pass
        try:
            if self.token is None:
                with open('./dsnbot/token.txt','r') as fp:
                    self.token = fp.readlines()[0].strip('\n')
        except:
            print("Token file not found")

    async def on_ready(self):
        print("Logged on")


    async def on_message(self, message):
        # this function is executed when a message is recieved
        if message.author == self.user:
            # ignore yourself
            return
        # turn the whole message lowercase
        contents = message.clean_content.lower().split(' ')
        # finds where the message came from
        channel = message.channel

        # Checks the contents against the predefined phrases
        for phrase in self.phrases:
            if phrase in contents:
                await channel.send(choice(self.replies))
                return

        
    @commands.command(pass_context=True)
    async def help(ctx):
        #this is the help command.
        help_msg = '```<+> DSN BOT <+>\n' + \
            'a discord bot to communicate with space probes ' + \
            'at lightpseed :/' + \
            '\nusage:          >command [params]*' + \
            '\n --- availible commands ---' + \
            '\n>help                               shows this message' + \
            '\n>quit                               shuts down the bot (only works for starmaid)' + \
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
