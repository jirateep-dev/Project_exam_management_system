#!/bin/bash

chmod +x manage.py migrate
uwsgi --ini uwsgi.ini