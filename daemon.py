import time
from workers.reddit_members_raw import RedditMembersRawDataWorker

workers = [
    RedditMembersRawDataWorker(),
]

for p in workers:
    p.run()

while True:
    for p in workers:
        p.ping()

    time.sleep(10)