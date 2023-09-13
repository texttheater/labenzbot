#!/usr/bin/env python3


import re
import sys
import urllib.parse


from bs4 import BeautifulSoup
from mastodon import Mastodon
import mysql.connector


import config


def html2txt(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = ''.join(soup.findAll(text=True))
    text = re.sub(r'\s+', ' ', text)
    return text


def strip_wikilinks(text):
    pattern = re.compile(r'\[\[(?:[^]|]+\|)?([^]]+)\]\]')
    return pattern.sub((lambda m: '→ %s' % m.group(1)), text)


if __name__ == '__main__':
    # Get random tweet from DB
    db = mysql.connector.connect(host=config.host, user=config.user,
            password=config.passwd, database=config.db)
    cursor = db.cursor()
    cursor.execute("""SELECT id, stw, stw_sanitus,
            UPPER(LEFT(stw_sortoren, 1)) AS bst, gra, ekl
            FROM labenz
            WHERE aufgenommen IS NOT NULL
            AND veroeffentlicht IS NOT NULL
            AND original = 0
            ORDER BY RAND()
            LIMIT 0,1""")
    results = cursor.fetchall()
    (id, stw, stw_sanitus, bst, gra, ekl) = results[0]
    db.close()
    # How many characters do we have for the definition?
    stw_url = urllib.parse.quote(stw.encode('UTF-8'))
    url = f'https://labenz.neutsch.org/{stw_url}'
    ekllen = 500 - len(stw) - len(gra) - len(url) - 3
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
        api_base_url = 'https://botsin.space/',
    )
    # Post
    mastodon.toot(text)
    # Log
    print(text, file=sys.stderr)
