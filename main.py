# deep space network assistant bot for 17776 server
# author Nicky (@starmaid#6925)
# created 05/06/2020
# edited 05/07/2020
# edited 11/27/2020: added aternos functions
# edited 2/20/2021: reformatted server permissions, added rss feeding
# version 2.0

import discord
from discord.ext import commands
import asyncio
import logging

logging.basicConfig(level=logging.ERROR)

from datetime import datetime
from dateutil import parser
import random
from random import choice
import json
import feedparser

from connect_and_launch import get_status, get_number_of_players
from connect_and_launch import connect_account, quitBrowser, get_server_info
from connect_and_launch import start_server, stop_server

from dsnquery import DSNQuery

server_conf = None
rss_conf = None

class Bot(commands.Bot):
    activity = 'comms monitor ./help'
    logoff_msg = '`logging off`'

    def __init__(self):
        # This is the stuff that gets run at startup
        super().__init__(command_prefix='./',self_bot=False,activity=discord.Game(self.activity))
        self.remove_command('help')
        self.add_command(self.help)
        self.add_command(self.dsn)
        self.add_command(self.add)
        self.add_command(self.ls)
        self.add_command(self.rm)
        self.add_command(self.about)
        self.add_command(self.quit)
        self.add_command(self.launch)
        self.add_command(self.players)
        self.add_command(self.status)
        self.add_command(self.stop)
        self.add_command(self.info)
        
        self.read_token()
        self.load_config()

        if self.token is None or server_conf is None or rss_conf is None:
            print(str(datetime.now()) + ': Could not start server due to missing files')
            pass
        else:
            super().run(self.token)


    def read_token(self):
        self.token = None
        try:
            with open('./token.txt','r') as fp:
                self.token = fp.readlines()[0].strip('\n')
        except:
            print(str(datetime.now()) + ': Token file not found')


    def load_config(self):
        global server_conf
        global rss_conf

        try:
            with open('./server_conf.json', 'r') as fp:
                server_conf = json.load(fp)
        except:
            print(str(datetime.now()) + ': Server conf file not found')

        try:
            with open('./rss_conf.json', 'r') as fp:
                rss_conf = json.load(fp)
        except:
            print(str(datetime.now()) + ': RSS conf file not found')


    async def on_ready(self):
        connect_account()  # logs into aternos
        await asyncio.sleep(2)
        print(str(datetime.now()) + ': Logged on with aternos')


    @commands.command(pass_context=True)
    async def help(ctx):
        #this is the help command.
        cmd = ctx.message.content.lower().split()
        l = len(cmd)

        if l == 1:
            # no params, just plain help
            help_msg = '```<./> DSN BOT <./>\n' + \
                'a discord bot to communicate with space probes ' + \
                'at lightpseed' + \
                '\nusage:          ./command [params]*' + \
                '\n --- availible commands ---' + \
                '\n./help                shows this message' + \
                '\n./dsn                 queries the Deep Space Network' + \
                '\n./ls [all, active]    lists all feeds, or active feeds in this server' + \
                '\n./add [params]*       adds a feed. See ./help add' + \
                '\n./rm [channel] [name] removes a feed from the server. use ./ls to find names' + \
                '\n./about               shows an about message for the bot' + \
                '\n./quit                shuts down the bot (only works for starmaid)'


            if str(ctx.guild.id) in server_conf.keys() and 'minecraft' in server_conf[str(ctx.guild.id)]['permissions']:
                help_msg += \
                    '\n./info                gives mc server information' + \
                    '\n./launch              starts the aternos minecraft server' + \
                    '\n./status              shows status of aternos minecraft server' + \
                    '\n./players             shows current players in aternos minecraft server' + \
                    '\n./stop                stops aternos minecraft server'

        elif l == 2:
            # we had a second param
            if cmd[1] == 'add':
                help_msg = '```<./> DSN BOT <./>' + \
                    '\nAdd a notification feed to a channel. Omit hard brackets when invoking.' + \
                    '\nIf you already know the name of the feed, via "./ls all", you can add ' + \
                    'it directly by name.' + \
                    '\n    ./add [#channel] [name]' + \
                    '\nIf you want to create a new custom feed using default settings, add ' + \
                    'it directly with the link. STILL BEING DEVELOPED - IT MIGHT NOT WORK' + \
                    '\n    ./add [#channel] rss [link to rss feed]'
        else:
            help_msg = '```help parameters not recognized.'

        help_msg += '```'
        await ctx.send(help_msg)
        return


    @commands.command(pass_context=True)
    async def about(ctx):
        """send an about message"""
        global server_conf
        global rss_conf

        msg = '```<./> DSN BOT <./>' + \
            '\nInspired by the Deep Space Network, run by JPL in Pasadena, CA.' + \
            '\nMade by @starmaid#6925. Contact me with questions.' + \
            '\nGithub: https://github.com/starmaid/dsnbot' + \
            '\nCurrently in ' + str(len(server_conf.keys())) + ' servers' + \
            '\nWatching ' + str(len(rss_conf['rss'].keys())) + ' rss feeds and ' + \
            str(len(rss_conf['custom'].keys())) + ' custom feeds' + \
            '```'

        await ctx.send(msg)
        return

    # async def on_guild_join(guild):
        # would love to say hi hehe


    ### ========== UPDATE COMMANDS ========== ###

    @commands.command(pass_context=True)
    async def add(ctx):
        """add an update to a channel"""

        global server_conf
        global rss_conf
        
        # read the message
        cmd = ctx.message.content.lower().split()
        l = len(cmd)
        guild_name = ctx.guild.name
        guild_id = ctx.guild.id
        chan_name = ctx.channel.name
        chan_id = ctx.channel.id

        new_chan = None

        err = False
        newrss = False

        # check arguments
        if l < 2:
            msg = '`too few arguments provided. See ./help add`'
            err = True;
            # parse arguments
            # send error message
        elif l == 3:
            # its just adding an already created one
            new_name = cmd[2]
            new_chan = cmd[1].replace('<','').replace('>','').replace('#','')

            all_ids = []
            for ch in ctx.guild.channels:
                all_ids.append(str(ch.id))

            if new_chan not in all_ids:
                err = True
                msg = '`Channel not valid. Make sure that the link is blue.`'
            elif new_name not in rss_conf['rss'].keys() and new_name not in rss_conf['custom'].keys():
                msg = '`premade feed not found`'
                err = True
            else:
                if str(guild_id) in server_conf.keys():
                    if new_chan in server_conf[str(guild_id)].keys():
                        server_conf[str(guild_id)][new_chan].append(new_name)
                    else: 
                        server_conf[str(guild_id)][new_chan] = [new_name]
                else:
                    server_conf[str(guild_id)] = {'permissions': ['rss'], chan_id: [new_name]}

        elif l == 4:
            new_chan = cmd[1].replace('<','').replace('>','').replace('#','')
            all_ids = []
            for ch in ctx.guild.channels:
                all_ids.append(str(ch.id))

            if str(new_chan) not in all_ids:
                err = True
                msg = '`Channel not valid. Make sure that the #channel link is blue.`'
            elif cmd[2] != "rss":
                msg = '`Improperly formed command. see ./help add`'
                err = True
            else:
                try:
                    feed = feedparser.parse(cmd[3])
                    title = feed['feed']['title'].replace(' ','').lower()
                    shortname = ''.join([c for c in title if c.isalnum()])
                    new_name = shortname[0:20]
                    
                    rss_conf['rss'][new_name] = {'url': cmd[3], 
                                                      'field':'title', 
                                                      'last_url':'', 
                                                      'last_val':'', 
                                                      'last_time':'', 
                                                      'msg_template': '`Update for ' + new_name + ':` '}
                    newrss = True
                    if str(guild_id) in server_conf.keys():
                        if chan_id in server_conf[guild_id].keys():
                            server_conf[str(guild_id)][chan_id].append(new_name)
                        else: 
                            server_conf[str(guild_id)][chan_id] = [new_name]
                    else:
                        server_conf[str(guild_id)] = {'permissions': ['rss'], chan_id: [new_name]}
                except:
                    msg = '`feed failed to be imported. make sure the link is correct, or contact an administrator`'
                    err = True

        if not err:
            # open and write to files to save changes
            with open('./server_conf.json', 'w') as fp:
                json.dump(server_conf, fp)
            
            if newrss:
                with open('./rss_conf.json', 'w') as fp:
                    json.dump(rss_conf, fp)
            
            # the most recent update will be sent to the server at [time]
            msg = '`update feed for "' + guild_name + '"` <#' + new_chan + '> `"' + new_name + '" added successfully`'
        

        # send confirmation message
        print(str(datetime.now()) + ': ' + msg)
        await ctx.send(msg)
        return

    @commands.command(pass_context=True)
    async def ls(ctx):
        """list updates"""
        # read the message

        global server_conf
        global rss_conf
        
        cmd = ctx.message.content.lower().split()
        l = len(cmd)
        guild_name = ctx.guild.name
        guild_id = ctx.guild.id
        chan_name = ctx.channel.name
        chan_id = ctx.channel.id

        err = False
        
        if l > 2:
            err = True
            msg = '`Too many arguments for ls. see ./help`'
        else:
            if l == 1 or cmd[1] == 'active':
                # list active feeds for this server
                if str(guild_id) not in server_conf.keys():
                    msg = '`Server not registered, no active feeds. see ./ls all`'
                    err = True
                else:
                    msg = '`List of active feeds and their channels:`'

                    for c in ctx.guild.channels:
                        loop_chan_id = str(c.id)
                        if loop_chan_id in server_conf[str(guild_id)].keys():
                            msg += '\n<#' + loop_chan_id + '>'
                            for feed in server_conf[str(guild_id)][loop_chan_id]:
                                msg += '\n    `' + feed + '`'

            elif cmd[1] == 'all':
                # list all feeds known by the rss thing
                msg = '```'
                msg += '\nList of all feeds updated via DSNbot:'
                msg += '\nRSS'
                for feed in rss_conf['rss'].keys():
                    msg += '\n    ' + feed + ' ' + rss_conf['rss'][feed]['url']

                msg += '\nCUSTOM'
                for feed in rss_conf['custom'].keys():
                    msg += '\n    ' + feed + ' ' + rss_conf['custom'][feed]['desc']

                msg += '```'

            else:
                err = True
                msg = '`invalid args. see ./help`'
        
        # send to channel
        print(str(datetime.now()) + ': ' + msg)
        await ctx.send(msg)
        return


    @commands.command(pass_context=True)
    async def rm(ctx):
        """remove an enabled update"""

        global server_conf
        global rss_conf
        
        # read the message
        cmd = ctx.message.content.lower().split()
        l = len(cmd)
        guild_name = ctx.guild.name
        guild_id = ctx.guild.id
        chan_name = ctx.channel.name
        chan_id = ctx.channel.id

        err = False

        # check arguments
            # parse arguments
            # send error message
        if l > 3:
            err = True
            msg = '`Too many arguments for rm. see ./help`'
        elif l < 3:
            err = True
            msg = '`Too few arguments for rm. see ./help`'
        else:
            del_feed = cmd[2]
            del_chan = cmd[1].replace('<','').replace('>','').replace('#','')

            all_ids = []
            for ch in ctx.guild.channels:
                all_ids.append(str(ch.id))

            if del_chan not in all_ids:
                # make sure channel exists
                err = True
                msg = '`Channel not valid. Make sure that the link is blue.`'
            
            else:
                if str(guild_id) in server_conf.keys():
                    if del_chan in server_conf[str(guild_id)].keys():
                        try:
                            server_conf[str(guild_id)][del_chan].remove(del_feed)
                            msg = '`update feed for "' + guild_name + '"` <#' + del_chan + '> `"' + del_feed + '" deleted successfully`'
                        except:
                            msg = '`premade feed not recognized. make sure you are using the exact spelling given in ./ls active`'
                            err = True
                    else: 
                        msg = '`selected channel not registered. good news is, theres nothing to delete!`'
                        err = True
                else:
                    msg = '`server not registered. good news is, theres nothing to delete!`'
                    err = True

        # open and save file
        if not err:
            # open and write to files to save changes
            with open('./server_conf.json', 'w') as fp:
                json.dump(server_conf, fp)
            
            
        # send confirmation message
        print(str(datetime.now()) + ': ' + msg)
        await ctx.send(msg)
        return


    @commands.command(pass_context=True)
    async def dsn(ctx):
        """dsn current communication poll"""
        msg = DSNQuery().poll()
        await ctx.send(msg)



    async def on_command_error(self, ctx, error):
        """Handle commands that are not recognized so it stops printing to console"""
        if type(error) is commands.CommandNotFound:
            msg = "`command not recognized.`"
            await ctx.send(msg)
    

    @commands.command(pass_context=True)
    async def quit(ctx):
        # quits the bot.
        if str(ctx.message.author) == 'starmaid#6925':
            await ctx.send(ctx.bot.logoff_msg)
            await ctx.bot.close()
            quitBrowser()
        else:
            await ctx.send('`you do not have permission to shut me down.`')
        
        print(str(datetime.now()) + ': Shutting down')
        return

    ### ========== MINECRAFT COMMANDS ========== ###

    @commands.command(pass_context=True)
    async def launch(ctx):
        # launches aternos

        if not (ctx.guild.id in server_conf.keys() and 'minecraft' in server_conf[ctx.guild.id]['permissions']):
            msg = '`sorry, your server does not have minecraft permissions`'
            return

        await ctx.send("`Launching Server...`")
        status = get_status()

        if status == "Offline":
            await start_server()
            author = ctx.author
            # loops until server has started and pings person who launched
            while True:
                await asyncio.sleep(5)
                if get_status() == "Online":
                    await ctx.send(f"{author.mention}, `the "
                                               f"server has started!`")
                    break
        
        elif status == "Online":
            await ctx.send("`The server is already Online`")
        
        elif status == 'Starting ...' or status == 'Loading ...':
            text = "`The server is already starting...`"
            await ctx.send(text)

        elif status == 'Stopping ...' or status == 'Saving ...':
            text = "`The server is stopping. Please wait.`"
            await ctx.send(text)
        
        else:
            text = "`An error occurred.\nTrying to launch the server anyways.`"
            await ctx.send(text)
            await start_server()


    @commands.command(pass_context=True)
    async def status(ctx):
        """status of aternos"""
        if not (ctx.guild.id in server_conf.keys() and 'minecraft' in server_conf[ctx.guild.id]['permissions']):
            msg = '`sorry, your server does not have minecraft permissions`'
            return

        await ctx.send("`Getting status...`")
        status = get_status()
        await ctx.send("`The server is {}`".format(status))


    @commands.command(pass_context=True)
    async def players(ctx):
        # launches aternos
        if not (ctx.guild.id in server_conf.keys() and 'minecraft' in server_conf[ctx.guild.id]['permissions']):
            msg = '`sorry, your server does not have minecraft permissions`'
            return

        await ctx.send("`Getting players...`")
        text = f"`There are {get_number_of_players()} players online.`"
        await ctx.send(text)

    
    @commands.command(pass_context=True)
    async def info(ctx):
        if not (ctx.guild.id in server_conf.keys() and 'minecraft' in server_conf[ctx.guild.id]['permissions']):
            msg = '`sorry, your server does not have minecraft permissions`'
            return

        ip, status, players, software, version = get_server_info()
        text = f"**IP:** {ip} \n**Status:** {status} \n**Players: " \
                f"**{players} \n**Version:** {software} {version}"
        embed = discord.Embed()
        embed.add_field(name="Server Info", value=text, inline=False)
        await ctx.send(embed=embed)

    
    @commands.command(pass_context=True)
    async def stop(ctx):
        # stops aternos
        if not (ctx.guild.id in server_conf.keys() and 'minecraft' in server_conf[ctx.guild.id]['permissions']):
            msg = '`sorry, your server does not have minecraft permissions`'
            return
        
        await ctx.send("`Stopping the server.`")
        status = get_status()

        if status != 'Stopping ...' or status != 'Saving ...':
            await stop_server()

        else:
            await ctx.send("`The server is already Offline.`")



if __name__ == '__main__':
    Bot()
