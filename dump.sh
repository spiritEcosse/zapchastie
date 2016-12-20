#!/usr/bin/env bash

source /home/h5782c/virtualenv/zapchastie/2.7/bin/activate
./manage.py dumpdata --indent 4 --natural-primary --natural-foreign -e contenttypes -e auth.Permission -e sessions -e admin > data/fixtures/all.json
git add .
git commit -m 'autocommit datetime on `date + "%Y-%m-%d %H:%M:%S"` (dump data database and images)'
git push
