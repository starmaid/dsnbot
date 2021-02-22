# dsnbot bot 20020 update script
# this one chekcs when a new chapter is posted
# put that shit as a cron job for mon/wed/fri at 3pm est
# WARNING this LOOPS UNTIL UPDATE so like
# author Nicky (@starmaid#6925)
# created 10/3/2020
# edited 2/21/2021 modular and portable now
# version 2.0

import time
import json
from feedquery import FeedQuery


# load the file that contains all feeds
rss_path = './rss_conf.json'
try:
    with open(rss_path, 'r') as fp:
        rss_conf = json.load(fp)
except:
    print(str(datetime.now()) + ': RSS file not found')


rss_conf['custom']['update_20020']['active'] = True
fq = FeedQuery()

update = fq.update_20020(rss_conf['custom']['update_20020'])

# send the messages maybe
if update:
    # save changes to JSON
    with open(rss_path, 'w') as fp:
        json.dump(rss_conf, fp)

    # open server config file
    with open('./server_conf.json', 'r') as fp:
        server_conf = json.load(fp)

    fq.send_updates(server_conf, rss_conf, [], ['update_20020'])
