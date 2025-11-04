#!/usr/bin/env python3


import random
import re
import sys
import urllib.parse


from bs4 import BeautifulSoup
from mastodon import Mastodon
import requests


def html2txt(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = ''.join(soup.findAll(string=True))
    text = re.sub(r'\s+', ' ', text)
    return text


def strip_wikilinks(text):
    pattern = re.compile(r'\[\[(?:[^]|]+\|)?([^]]+)\]\]')
    return pattern.sub((lambda m: '→ %s' % m.group(1)), text)


if __name__ == '__main__':
    # Get random liff from API
    r = requests.get('https://labenz.neutsch.org/api.php')
    r.raise_for_status()
    liffs = r.json()
    liff = random.choice(liffs)
    # Populate fields
    id = liff['id']
    stw = liff['stw']
    stw_sanitus = liff['stw_sanitus']
    bst = liff['bst']
    gra = liff['gra']
    ekl = liff['ekl']
    # How many characters do we have for the definition?
    stw_url = urllib.parse.quote(stw_sanitus.encode('UTF-8'))
    url = f'https://labenz.neutsch.org/{stw_url}'
    ekllen = 500 - len(stw) - len(gra) - 23 - 3
    if ekllen < 1:
        print(
            'ERROR: no characters left for definition of {stw}',
            file=sys.stderr,
        )
        sys.exit(1)
    # Format
    ekl = strip_wikilinks(html2txt(ekl))
    if len(ekl) > ekllen:
        ekllen -= 1 # for … character
        ekl = ekl[:ekllen] + '…'
    text = f'{stw}{gra}: {ekl} {url}'
    # Create Mastodon client
    mastodon = Mastodon(
        access_token='token.secret',
        api_base_url = 'https://mastodon.social/',
    )
    # Post
    mastodon.toot(text)
    # Log
    print(text, file=sys.stderr)
