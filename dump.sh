#!/usr/bin/env bash

function dumpdata() {
    echo "Here, the recent actions of the this script."
    source /home/h5782c/virtualenv/zapchastie/2.7/bin/activate 1>>$HOME_DIR.repos_push.log
    ./manage.py dumpdata --indent 4 --natural-primary --natural-foreign -e contenttypes -e auth.Permission -e sessions -e admin > data/fixtures/all.json 1>>$HOME_DIR.repos_push.log
    git add .
    git commit -m "autocommit datetime on `date +'%Y-%m-%d %H:%M:%S'` (dump database and images)";
    git push
}

dumpdata | tee error.log
