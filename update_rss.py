"""Build the static preview from ENKARE_RSS_URL. No third-party dependencies."""
import os
import re
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

SHOW = 'https://open.spotify.com/show/0jukSDatX4ZznOLE8XMoty'
NS = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
      'content': 'http://purl.org/rss/1.0/modules/content/'}

class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, data):
        self.parts.append(data)

def plain(value):
    parser = PlainText(); parser.feed(value or '')
    return ' '.join(' '.join(parser.parts).replace('\u2060', '').replace('\u200b', '').replace('\ufeff', '').split())

def safe_url(value):
    try:
        parts = urlsplit((value or '').strip())
        return value.strip() if parts.scheme == 'https' and parts.hostname and not parts.username else ''
    except ValueError:
        return ''

def parse_feed(data):
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('RSS document type declarations are unsupported')
    root = ET.fromstring(data)
    items, seen = [], set()
    for item in root.findall('./channel/item'):
        title = plain(item.findtext('title'))
        if not title: continue
        key = item.findtext('guid') or item.findtext('link') or title
        if key in seen: continue
        seen.add(key)
        try:
            date = parsedate_to_datetime(item.findtext('pubDate') or '')
            if date.tzinfo is None: date = date.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError, OverflowError):
            date = datetime.min.replace(tzinfo=timezone.utc)
        image = item.find('itunes:image', NS)
        items.append({'title': title, 'description': plain(item.findtext('description') or item.findtext('content:encoded', namespaces=NS)).split('▷▶︎私たちについて')[0][:300],
                      'link': safe_url(item.findtext('link')) or SHOW,
                      'image': safe_url(image.get('href')) if image is not None else '',
                      'number': plain(item.findtext('itunes:episode', namespaces=NS)), 'date': date})
    if not items: raise ValueError('No usable RSS episodes; leaving published site unchanged')
    return sorted(items, key=lambda item: item['date'], reverse=True)

def card(item):
    e = escape
    stamp = item['date'].astimezone(timezone(timedelta(hours=9))).strftime('%Y.%m.%d') if item['date'].year > 1 else 'ENKARE!'
    art = (f'<img src="{e(item["image"], quote=True)}" alt="" loading="lazy" style="width:100%;aspect-ratio:1;object-fit:contain">' if item['image'] else
           f'<span>ENKARE! / EPISODE</span><strong>{e("#"+item["number"] if item["number"] else "♪")}</strong>')
    label = 'Spotifyの番組一覧へ' if item['link'] == SHOW else ('Spotifyで聴く' if urlsplit(item['link']).hostname == 'open.spotify.com' else '配信ページで聴く')
    return f'<article class="episode"><div class="episode-art">{art}</div><div class="episode-copy"><span class="eyebrow">{stamp}</span><h2>{e(item["title"])}</h2><p>{e(item["description"])}</p><a class="text-link" href="{e(item["link"], quote=True)}" target="_blank" rel="noopener noreferrer">{label} ↗</a></div></article>'

def build(source, output, data):
    items = parse_feed(data)
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output or source in output.parents:
        raise ValueError('Output must be separate from the source directory')
    if output.exists(): raise ValueError('Use a fresh output directory')
    pages = {}
    for name in ('episodes.html', 'enkare.html'):
        pages[name] = (source/name).read_text(encoding='utf-8')
    section = '<section class="section episode-list"><p class="list-note">公開中のエピソードを新しい順にご紹介します。</p>'+''.join(card(item) for item in items)+'</section>'
    pages['episodes.html'], count = re.subn(r'<section class="section episode-list">.*?</section>', lambda _: section, pages['episodes.html'], count=1, flags=re.S)
    if count != 1: raise ValueError('Episode section not found')
    latest = '<section class="section"><span class="eyebrow">LATEST EPISODE / 最新の配信</span>'+card(items[0])+'<a class="button blue" href="episodes.html">エピソード一覧へ →</a></section>'
    pages['enkare.html'] = pages['enkare.html'].replace('</section>', '</section>'+latest, 1)
    output.mkdir(parents=True)
    for file in source.iterdir():
        if file.is_file() and file.suffix.lower() in ('.html','.css','.js','.jpg','.png','.mp4','.svg','.ico','.webp'):
            shutil.copy2(file, output/file.name)
    for name, content in pages.items(): (output/name).write_text(content, encoding='utf-8')
    print(f'Built {len(items)} episodes. RSS owner/email fields are not published.')

if __name__ == '__main__':
    url = safe_url(os.environ.get('ENKARE_RSS_URL'))
    if not url: sys.exit('Set ENKARE_RSS_URL to the verified public HTTPS feed URL')
    request = urllib.request.Request(url, headers={'User-Agent':'CueFM-RSS-Website/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(10_000_001)
    if len(data) > 10_000_000: sys.exit('RSS feed exceeds 10MB')
    build(sys.argv[1] if len(sys.argv)>1 else '.', sys.argv[2] if len(sys.argv)>2 else '../site-build', data)


