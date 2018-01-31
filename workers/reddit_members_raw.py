from lib.data_worker import DataWorker

import time
import requests
import re
from urllib import parse as urllib_parse

req_headers = {
    'Connection':'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'hcmc.io.bot.v1',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
}

REDDIT_REQUEST_TEMPLATE = "https://www.reddit.com/r/%s/about.json"
REDDIT_ID_REGEX = re.compile(r"\/r\/([\d\w\-\_\.]+)/?")


class RedditMembersRawDataWorker(DataWorker):
    update_frequency = 60 * 10

    def __init__(self):
        pass

    def fetch_data(self):
        r = requests.get("http://db.xyz.hcmc.io/data/coins.json")
        data = r.json()

        for row in data:
            if not row:
                continue

            if not ('community' in row and 'reddit' in row['community']):
                # There is not reddit links for current row item
                continue

            links = row['community']['reddit']

            if not links:
                # There is not reddit links for current row item
                continue

            data = dict(
                ts=int(time.time()),
                members=0,
                members_active=0,
            )

            for link in links:
                url = urllib_parse.urlparse(link)
                matches = REDDIT_ID_REGEX.findall(url.path)

                if not matches:
                    continue

                page_id = matches[0]

                # slow down to prevent ip ban
                time.sleep(0.5)
                r = requests.get(REDDIT_REQUEST_TEMPLATE % page_id, headers=req_headers)

                resp = r.json()

                if 'error' in resp:
                    if resp['error'] == 403:
                        # private community
                        continue

                    elif resp['error'] == 404:
                        # doesn't exists or banned
                        continue

                if 'kind' in resp and resp['kind'] == 'Listing':
                    # this is not sub reddit (skipping)
                    continue

                resp = resp['data']

                data['members'] += resp['subscribers']
                data['members_active'] += resp['active_user_count']

            self.save(row['id'], data)

    def save(self, coin_id, data):
        if data is None:
            return

        # In real parser we will get last entry from db and check if current data differs
        # from latest saved and if not we will skip it.

        print(coin_id, data)