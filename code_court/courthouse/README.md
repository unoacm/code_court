# dev setup
## Mac
- Install brew from http://brew.sh
- `brew install python3`
- Create virtualenv `virtualenv env -p /usr/local/bin/python3`
- Activate virtualenv `source env/bin/activate`
- Install dependencies `pip install -r requirements.txt`
- Start web server and event loop `gunicorn web:app -c gunicorn_config.py`

## Linux
- Create virtualenv `virtualenv env -p /usr/bin/python3`
- Activate virtualenv `source env/bin/activate`
- Install dependencies `pip install -r requirements.txt`
- Start web server and event loop `gunicorn web:app -c gunicorn_config.py`

# misc
- Run tests with `nosetests`
