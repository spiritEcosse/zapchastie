debian:
    # Install postgresql
	sudo apt-get install postgresql postgresql-contrib
	# Drop db: auto_part
	sudo -u postgres bash -c "psql -c \"drop database auto_part;\""
	# Create db: auto_part
	sudo -u postgres createdb auto_part
	# Drop role: auto_part
	# sudo -u postgres bash -c "psql -c \"drop role auto_part;\""
	# Create role: auto_part
	# sudo -u postgres bash -c "psql -c \"CREATE USER auto_part WITH PASSWORD '1111';\""
	# sudo -u postgres bash -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE auto_part TO auto_part;\""
	# Install other libs
	sudo apt-get install libpq-dev
	sudo apt-get install libmagickwand-dev

install_pip:
    # Install pip and virtualenvwrapper
	sudo apt-get install python-pip
	sudo pip install virtualenvwrapper

create_venv:
	./venv.sh auto_part
	# echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bash_login
	# /bin/bash -l -i -c source ~/.bashrc
    # Deactivate virtual env
	#!/bin/bash deactivate virtual env
    # Remove env
	#!/bin/bash rmvirtualenv auto-part
    # Create virtual env
	# source `which virtualenvwrapper.sh`
	# /bin/bash -l -i -c mkvirtualenv auto-part

install:
	pip install -r requirements.txt

build_site:
    # Create settings_local
	cp auto_parts/settings_sample.py auto_parts/settings_local.py
    # Update migrations
	./manage.py makemigrations
	# Apply migrate
	./manage.py migrate auth
	./manage.py migrate contenttypes
	./manage.py migrate sites
	./manage.py migrate catalogue
	./manage.py migrate
	# Import some fixtures.
	./manage.py loaddata data/fixtures*
	./manage.py oscar_populate_countries --initial-only
	./manage.py clear_index --noinput
	./manage.py update_index catalogue

site: debian install_pip create_venv install build_site

sandbox_image:
    docker build -t django-oscar-sandbox:latest .

docs:
	cd docs && make html

coverage:
	py.test --cov=oscar --cov-report=term-missing

lint:
	flake8 src/oscar/
	isort -q --recursive --diff src/

testmigrations:
	pip install -r requirements_migrations.txt
	cd sites/sandbox && ./test_migrations.sh

# This target is run on Travis.ci. We lint, test and build the sandbox
# site as well as testing migrations apply correctly. We don't call 'install'
# first as that is run as a separate part of the Travis build process.
travis: install coverage lint build_sandbox testmigrations

messages:
	# Create the .po files used for i18n
	cd src/oscar; django-admin.py makemessages -a

compiledmessages:
	# Compile the gettext files
	cd src/oscar; django-admin.py compilemessages

css:
	npm install
	npm run build

clean:
	# Remove files not in source control
	find . -type f -name "*.pyc" -delete
	rm -rf nosetests.xml coverage.xml htmlcov *.egg-info *.pdf dist violations.txt

preflight: lint
    # Bare minimum of tests to run before pushing to master
	./runtests.py

todo:
	# Look for areas of the code that need updating when some event has taken place (like
	# Oscar dropping support for a Django version)
	-grep -rnH TODO *.txt
	-grep -rnH TODO src/oscar/apps/
	-grep -rnH "django.VERSION" src/oscar/apps


release: clean
	pip install twine wheel
	rm -rf dist/*
	python setup.py sdist bdist_wheel
	twine upload -s dist/*
