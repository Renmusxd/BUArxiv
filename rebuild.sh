#!/usr/bin/env bash
set -e

cd "$(dirname "$0")";
\cp test.db test.db.bak
/home/sumnerh/BUArxiv/.virtualenvs/flask/bin/python scrape.py

date >> lastrebuild.txt

