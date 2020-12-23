# dsnbot bot rss script
# this one chekcs rss feeds and is meant to run like once every 15 min
# put that shit as a cron job
# author Nicky (@starmaid#6925)
# created 10/3/2020
# edited 10/14/2020
# version 1.1
# added ao3 functionality

import feedparser
import requests
import discord
import json

# look at previous updates
updates_path = './feed_updates.json'
try:
    with open(updates_path, 'r') as fp:
        last_update = json.load(fp)
except:
    last_update = {"story": "1", "jon": "None", "ao3": "none"}

# jon updates
jon_update = False
jon = feedparser.parse('https://www.sbnation.com/authors/jon-bois/rss')
title = jon['entries'][0]['title']
linkj = jon['entries'][0]['link']
if last_update['jon'] != title:
    jon_update = True
    last_update['jon'] = title

# ao3 updates
ao3_update = False
ao3 = feedparser.parse('https://archiveofourown.org/tags/17107986/feed.atom')
sortedlist = sorted(ao3['entries'], key=lambda k: k['updated'], reverse=True)
#updated = sortedlist[0]['updated']
updated = sortedlist[0]['title']
link = sortedlist[0]['link']
if last_update['ao3'] != updated:
    ao3_update = True
    last_update['ao3'] = updated


# send the messages maybe
if jon_update or ao3_update:
    with open(updates_path, 'w') as fp:
        json.dump(last_update, fp)

    client = discord.Client(activity=discord.Game("searching"))

    @client.event
    async def on_ready():
        jon_chan = []
        ao3_chan = []
        for g in client.guilds:
            for c in g.channels:
                if c.name == 'announcements':
                    jon_chan.append(c)
                if c.name == 'clancy':
                    ao3_chan.append(c)
        if jon_update:
            #send a story update to the story channel
            for c in jon_chan:
                await c.send('@everyone `NEW JON ARTICLE:` ' + linkj)
        if ao3_update:
            for c in ao3_chan:
                await c.send('`UPDATED FIC:` ' + linka)
        await client.close()

    def read_token():
        token = None
        try:
            with open('./token.txt','r') as fp:
                token = fp.readlines()[0].strip('\n')
        except:
            print('Token file not found')
        return token

    token = read_token()
    if token is not None:
        client.run(token)
    else:
        pass