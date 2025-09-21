import time
import feedparser
import json
import base64
import click
import urllib.request
import traceback
from fake_useragent import UserAgent
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone
from staticjinja import Site

UPDATE_FREQ = 3600 # 1hr in seconds

MINUTES = 'm'
HOURS = 'h'
DAYS = 'd'
MONTHS = 'M'
YEARS = 'Y'

def url_to_filename(url):
    return 'db/feeds/'+str(base64.b64encode(url.encode("utf-8")).decode('utf-8'))


def datetime_of_struct_time(st):
    "Convert a struct_time to datetime maintaining timezone information when present"

    # if we have no time info, we just have to assume it's the oldest time
    if st is None:
        return datetime.fromtimestamp(0)
    tz = None
    if st.tm_gmtoff is not None:
        tz = timezone(datetime.timedelta(seconds=st.tm_gmtoff))
        
    # datetime doesn't like leap seconds so just truncate to 59 seconds
    if st.tm_sec in {60, 61}:
        return datetime(*st[:5], 59, tzinfo=tz)
    return datetime(*st[:6], tzinfo=tz)


def calc_ago(now, published):
    "Calculate # of minutes/days/months/years since the last update"
    # TODO: this has tz problems.
    delta = now - published
    if(delta.days == 0):
        minutes = delta.seconds // 60
        if(minutes < 60):
            return (minutes, MINUTES)
        else:
            return (minutes // 60, HOURS)
    elif(delta.days < 31):
        return (delta.days, DAYS)
    elif(delta.days < 365):
        return (delta.days // 30, MONTHS)
    else:
        return (delta.days // 365, YEARS)


def download_feed(url):
    "Download the feed to a local file"
    print('downloading: ',url)
    filename = url_to_filename(url)
    ua = UserAgent()
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', ua.chrome)]
    with opener.open(url) as uh:
        with open(filename, "w") as output:
            output.write(uh.read().decode('utf-8'))


def download_feeds():
    follows_meta = get_follows_meta()
    urls = [x['url'] for x in follows_meta]
    for url in urls:
        download_feed(url)

def is_null_or_empty(l):
    return l is None or len(l) == 0

def get_last_updated(d):
    last_updated = None

    if last_updated is None and not is_null_or_empty(d.entries):
        first = d.entries[0]
        last_updated = first.get('updated_parsed', first.get('published_parsed', None))

    if last_updated is not None:
        return datetime_of_struct_time(last_updated)

    return datetime.fromtimestamp(0)


def get_follow(url):
    """
    Get the 'follow' dictionary which will be passed to the jinja templates for rendering.

    Feeds are locally cached.
    """
    print("processing: ", url);
    now = datetime.utcnow()
    
    # download feed if it hasn't been updated in a while
    filename = url_to_filename(url)
    path = Path(filename)
    if not path.exists() or (time.time() - path.stat().st_mtime > UPDATE_FREQ):
        download_feed(url)

    follow = {}
    d = feedparser.parse(path)

    title = d.feed.get('title')
    follow['title'] = title if (title is not None and title != "") else urlparse(url).netloc
    follow['link'] = d.feed.get('link', url)
    follow['image_href'] = d.feed.image.href if 'image' in d.feed else '';

    feed_last_updated = get_last_updated(d)
    latest_ago_val, latest_ago_interval = calc_ago(now, feed_last_updated)
    follow['latest_ago'] = feed_last_updated
    follow['latest_ago_val'] = latest_ago_val
    follow['latest_ago_interval'] = latest_ago_interval
    follow['posts'] = []

    for e in d.entries[:10]:
        post = {}
        post['title'] = e.title
        post['link'] = e.link
        last_updated = datetime_of_struct_time(
                e.get('updated_parsed', e.get('published_parsed', None)))
        ago_val, ago_interval = calc_ago(now, last_updated)
        post['ago_val'] = ago_val
        post['ago_interval'] = ago_interval
        follow['posts'].append(post)

    return follow


def get_follows_meta():
    "Get subscription data - what feeds are we following"
    with open('db/follows.json', 'r') as file:
        follows_meta = json.load(file)
    #print(json.dumps(follows_meta, indent=4))
    return follows_meta


def get_follows():
    follows_meta = get_follows_meta()

    urls = [x['url'] for x in follows_meta]
    follows = []
    for url in urls:
        try:
            follows.append(get_follow(url))
        except Exception as e:
            print("An exception occurred:", e)
            print(traceback.format_exc())


    follows.sort(key=lambda f: f['latest_ago'], reverse=True)
    return follows


def render(follows):
    context = {'follows': follows}
    site = Site.make_site(
        env_globals=context,
        outpath="build",
    )
    
    site.render(
        use_reloader=False
    )

@click.command()
def main():
    #download_feeds()
    follows = get_follows()
    render(follows)


if __name__ == "__main__":
    main()

