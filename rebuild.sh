#!/usr/bin/env bash
set -e

cd "$(dirname "$0")";
/home/sumnerh/BUArxiv/.virtualenvs/flask/bin/python scrape.py

date >> lastrebuild.txt

