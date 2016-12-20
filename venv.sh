#!/usr/bin/env bash

source `which virtualenvwrapper.sh`
rmvirtualenv $1
mkvirtualenv $1

# Install libs in virtual environment
pip install -r requirements.txt

# Update migrations
./manage.py makemigrations

# Apply migrate
./manage.py migrate

# Collectstatic
./manage.py collectstatic --noinput

# Load all data from fixtures
# tar - data/fixtures/all.json.tar.gz data/fixtures/all.json # Unzip all.json
# ./manage.py loaddata data/fixtures/all.json


# Load initial data from fixtures.
#./manage.py loaddata data/fixtures/sites.json
#./manage.py loaddata data/fixtures/auth.json
#./manage.py loaddata data/fixtures/category.json
#./manage.py loaddata data/fixtures/product_class.json
#./manage.py loaddata data/fixtures/product.json
#./manage.py loaddata data/fixtures/partner.json
#./manage.py loaddata data/fixtures/redirects.json
#./manage.py loaddata data/fixtures/promotions.json
#./manage.py oscar_populate_countries --initial-only
./manage.py clear_index --noinput
./manage.py update_index catalogue

./manage.py update_rates
