---
layout: post
title:  "how i built this website"
date:   2024-04-29
last_modified_at: 2024-04-29
categories: [all]
---
I build this website using Jekyll and the Jekyll Ghost theme as a base.
I utilized the Liquid tags written for this Edward Tufte website to add in
margin notes and images.

I host this website for free on Github pages, which unfortunately doesn't
play nicely with many Jekyll plugins. I use this shell script (which I found on Reddit but haven't been able to relocate since) to build
the website locally and then push to GH pages to avoid plugin incompatibility.

```
#! /bin/bash

# -- Build with baseurl, '/ntest'
# bundle exec jekyll build --baseurl '/ntest'

# -- Build with no baseurl
bundle exec jekyll build

# -- Get rid of any existing local gh-pages
git branch -D gh-pages

# -- Create a new gh-pages branch not based on any existing branch
git checkout --orphan gh-pages

# -- Delete the junk that git puts into this new branch
# -- ( see git-checkout --orphan documentation for details. )
git rm -rf .

# -- add, commit, and push contents from _site to gh-pages branch.
git --work-tree _site/ add .
git --work-tree _site/ commit -m 'gh-pages commit' .
git --work-tree _site/ push -f origin gh-pages

## -- go back to working on master branch and clean up.
git checkout -f master
git branch -D gh-pages
rm -rf _site
```
