#! /bin/bash

# -- Fetch latest books from Airtable (requires AIRTABLE_KEY env var)
python3 fetch_books.py

# -- Build with baseurl, '/ntest'
# bundle exec jekyll build --baseurl '/ntest'

# -- Build with no baseurl
bundle exec jekyll build

# -- Deploy _site contents to gh-pages
cd _site
git init
git add -A
git commit -m "Deploy to gh-pages"
git remote add origin https://github.com/scfiller/scfiller.github.io.git
git push --force origin HEAD:gh-pages
cd ..
rm -rf _site
