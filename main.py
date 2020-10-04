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
        super().__init__(command_prefix='/',self_bot=False,activity=discord.Game(self.activity))
        random.seed()
        self.quit_val = random.randint(100000000000,999999999999)
        self.remove_command('help')
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
        # This creates the quitval and saves it to my server
        print("Logged on")
        print(self.quit_val)
        #with open("char_" + str(self.quit_val),"w") as file:
        #    file.write(str(self.quit_val))

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
                # replies with a generated keysmash
                await channel.send(choice(self.replies))
                return

        if str(channel.name) != 'h-mestuck':
            for w in contents:
                if w in self.x1:
                    wlist = []
                    wlist.append(w)
                    await channel.send(self.gen_reply(wlist, 1))
                    return
            l = 0
            wlist = []
            for w in contents:
                if w in self.x2:
                    print(w + ' ' + str(l))
                    wlist.append(w)
                    l = l + 1
            if l >= 2:
                await channel.send(self.gen_reply(wlist, 2))

        if str(self.quit_val) in contents:
            await channel.send(self.logoff_msg)
            await self.close()

    def gen_reply(self, words, type):
        msg = 'u said'
        for w in words:
            msg = msg + ' `'  + w + '`'
            if w != words[len(words) - 1]:
                msg = msg + ', '
        msg = msg + ' - '
        if type == 1:
            msg = msg + choice(self.hs_replies)
        elif type == 2:
            msg = msg + choice(self.suspicious)
        return msg


if __name__ == '__main__':
    Bot()
