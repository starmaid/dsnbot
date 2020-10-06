# dsnbot bot 20020 update script
# this one chekcs when a new chapter is posted
# put that shit as a cron job for mon/wed/fri at 3pm est
# WARNING this LOOPS UNTIL UPDATE so like
# author Nicky (@starmaid#6925)
# created 10/3/2020
# edited NA
# version 1.0

import requests
import time
import discord
import json


# look at previous updates
updates_path = './feed_updates.json'
try:
    with open(updates_path, 'r') as fp:
        last_update = json.load(fp)
except:
    last_update = {"story": "1", "jon": "None"}


baselink = 'https://www.sbnation.com/secret-base/21410129/20020/chapter-'

story_update = False
next = int(last_update['story']) + 1
while not story_update:
    # try to get the chapter
    link = baselink+str(next)
    webpage = requests.get(link)
    
    if webpage.status_code != 404:
        # if we actually get a chapter back, increase the counter
        last_update['story'] = str(next)
        story_update = True
    else:
        time.sleep(10)


# send the messages maybe
if story_update:
    with open(updates_path, 'w') as fp:
        json.dump(last_update, fp)

    client = discord.Client(activity=discord.Game("searching"))

    @client.event
    async def on_ready():
        story_chan = []
        for g in client.guilds:
            for c in g.channels:
                if c.name == 'announcements':
                    story_chan.append(c)
        if story_update:
            #send a story update to the story channel
            for c in story_chan:
                await c.send('@everyone `WHAT COLLEGE FOOTBALL WILL LOOK LIKE IN THE FUTURE #' + str(next) + ':` ' + link)
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