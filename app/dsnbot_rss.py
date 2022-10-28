# dsnbot bot rss script
# this one chekcs rss feeds and is meant to run like once every 15 min
# put that shit as a cron job
# author Nicky (@starmaid#6925)
# created 10/3/2020
# edited 10/14/2020 added ao3 functionality
# edited 2/21/2021 reformatted for portability
# version 2.0

from datetime import datetime
import json
from feedquery import FeedQuery

# load the file that contains all feeds
rss_path = './rss_conf.json'
try:
    with open(rss_path, 'r') as fp:
        rss_conf = json.load(fp)
except:
    print(str(datetime.now()) + ': RSS file not found')


fq = FeedQuery()
update = False
updated_rss = []
updated_custom = []

# loop through the contents of the file, call functions in the feedquery class
for f in rss_conf['rss'].keys():
    if fq.rss(rss_conf['rss'][f]):
        # updates the main JSON object when passing by reference!
        updated_rss.append(f)
        print(updated_rss)
        update = True

for c in rss_conf['custom'].keys():
    if fq.custom(c, rss_conf['custom'][c]):
        updated_custom.append(c)
        update = True


# send the messages maybe
if update:
    # save changes to JSON
    with open(rss_path, 'w') as fp:
        json.dump(rss_conf, fp)

    # open server config file
    with open('./server_conf.json', 'r') as fp:
        server_conf = json.load(fp)

    fq.send_updates(server_conf, rss_conf, updated_rss, updated_custom)
    