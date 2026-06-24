#!/usr/bin/env python3
"""
Fetch bookshelf data from Airtable, download cover images to bookshelf/covers/,
and write _data/books.json for Jekyll to consume at build time.

Requires AIRTABLE_KEY env var. Exits cleanly if the key is not set, so
`bundle exec jekyll serve` still works using whatever data is already on disk.

Usage:
    AIRTABLE_KEY=patXXX python3 fetch_books.py
"""
import json
import os
import sys
import requests

AIRTABLE_BASE = 'https://api.airtable.com/v0/appW5NdqoJg8HcuXN/tblUaaH11n2XruFCh'
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
COVERS_DIR = os.path.join(REPO_ROOT, 'bookshelf', 'covers')
DATA_FILE = os.path.join(REPO_ROOT, '_data', 'books.json')
FIELDS = ['Title', 'Author', 'Genre', 'Favorite', 'Attachments']


def fetch_all(key):
    records, offset = [], None
    headers = {'Authorization': f'Bearer {key}'}
    while True:
        params = {'filterByFormula': 'AND({Read}="read", {Show on Website}="True")', 'fields[]': FIELDS}
        if offset:
            params['offset'] = offset
        resp = requests.get(AIRTABLE_BASE, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        records.extend(data['records'])
        offset = data.get('offset')
        if not offset:
            break
    return records


def cover_info(record):
    """Return (download_url, original_filename) or (None, None) if no cover."""
    att = record['fields'].get('Attachments')
    if not att:
        return None, None
    first = att[0]
    thumbs = first.get('thumbnails', {})
    url = (thumbs.get('large') or {}).get('url') or first.get('url')
    return url, first.get('filename', 'cover.jpg')


def download_cover(record_id, url, original_filename):
    os.makedirs(COVERS_DIR, exist_ok=True)
    ext = os.path.splitext(original_filename)[-1].lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
        ext = '.jpg'
    dest_name = f'{record_id}{ext}'
    resp = requests.get(url)
    resp.raise_for_status()
    with open(os.path.join(COVERS_DIR, dest_name), 'wb') as fh:
        fh.write(resp.content)
    return f'/bookshelf/covers/{dest_name}'


def main():
    key = os.environ.get('AIRTABLE_KEY')
    if not key:
        print('AIRTABLE_KEY not set — skipping Airtable fetch', file=sys.stderr)
        sys.exit(0)

    print('Fetching books from Airtable...')
    records = fetch_all(key)
    print(f'  {len(records)} records found')

    books = []
    for r in records:
        fields = r['fields']
        url, filename = cover_info(r)
        img_path = download_cover(r['id'], url, filename) if url else None
        if img_path:
            print(f"  cover: {fields.get('Title', r['id'])}")
        books.append({
            'title': (fields.get('Title') or '').strip(),
            'author': (fields.get('Author') or '').strip(),
            'genre': (fields.get('Genre') or '').lower().strip(),
            'favorite': fields.get('Favorite') == 'True',
            'img': img_path,
        })

    with open(DATA_FILE, 'w', encoding='utf-8') as fh:
        json.dump(books, fh, indent=2, ensure_ascii=False)
    print(f'  Wrote {len(books)} books to _data/books.json')
    print(f'  Cover images in bookshelf/covers/')


if __name__ == '__main__':
    main()
