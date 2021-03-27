import feedparser
import requests
import discord
from dateutil import parser
from datetime import datetime

class FeedQuery:
    def __init__(self):
        # whatever
        self.methods = []
        for func in dir(self):
            if callable(getattr(self, func)) and '__' not in func:
                self.methods.append(func)


    def rss(self, feed_dict):
        """update the feed dict, and return true if changed"""
        update = False

        # get the file from Online
        rssfile = feedparser.parse(feed_dict['url'])
        
        # sort by the updated time parsed
        try:
            sortedlist = sorted(rssfile['entries'], key=lambda k: parser.parse(k['updated'], fuzzy=True), reverse=True)
            entry = sortedlist[0]
            # check the updated time
            time = entry['updated']
        except:
            print(str(datetime.now()) + ': error for sorting ' + feed_dict['url'])
            entry = rssfile['entries'][0]
            time = ''

        try:
            # Check the field and read the value
            updated = entry[feed_dict['field']]
            # get the link too
            link = entry['link']

            # compare to previous values 
            if updated != feed_dict['last_val']:
                update = True
                feed_dict['last_val'] = updated
                feed_dict['last_url'] = link
                feed_dict['last_time'] = time
        except:
            print(str(datetime.now()) + ': other error for ' + feed_dict['url'])
        
        return(update)


    def custom(self, feed_name, feed_dict):
        """figures out where to send the custom thing to"""
        update = False

        # check if feed_name is in the list of methods in this class
        if feed_name in self.methods:
            # call that method
            update = getattr(self,feed_name)(feed_dict)
        
        # return results as a dict and a t/f value
        return(update)


    def custom_template(self, feed_dict):
        """example tempalte for a custom updater"""

        new_msg = "`wahtever`"
        feed_dict['msg'] = new_msg
        return(True)


    def update_20020(self, feed_dict):
        """
        updater for 20020, inactive for now
        would be run at 3:00 pm EST on MWF
        """

        baselink = 'https://www.sbnation.com/secret-base/21410129/20020/chapter-'

        update = False
        total_sleep = 0
        interval = 10

        if feed_dict['active'] == 'True':
            next = int(feed_dict['story']) + 1
            while not update:
                # try to get the chapter
                link = baselink+str(next)
                webpage = requests.get(link)
                
                if webpage.status_code != 404:
                    # if we actually get a chapter back, increase the counter
                    feed_dict['story'] = str(next)
                    update = True
                else:
                    # check again in {interval} seconds
                    if not total_sleep > 60*60:
                        # if we have been doing this for an hour then fuckin stop it
                        time.sleep(interval)
                        total_sleep += interval
                    else:
                        break
            if update:
                new_msg = '@everyone `WHAT COLLEGE FOOTBALL WILL LOOK LIKE IN THE FUTURE #' + str(next) + ':` ' + link
                feed_dict['msg'] = new_msg
            
            feed_dict['active'] = 'False'

        return(update)


    def send_updates(self, server_conf, rss_conf, updated_rss=[], updated_custom=[]):
        client = discord.Client(activity=discord.Game("downlink active ./help"))

        @client.event
        async def on_ready():
            for g in client.guilds:
                if str(g.id) in server_conf.keys():
                    for c in g.channels:
                        if str(c.id) in server_conf[str(g.id)].keys():
                            for feed in server_conf[str(g.id)][str(c.id)]:
                                if feed in updated_rss:
                                    # then the data changed
                                    msg = rss_conf['rss'][feed]['msg_template']
                                    msg += rss_conf['rss'][feed]['last_url']
                                    await c.send(msg)

                                if feed in updated_custom:
                                    # then the custom data changed
                                    await c.send(rss_conf['custom'][feed]['msg'])

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