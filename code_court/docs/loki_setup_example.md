## Setup for courthouse

The courthouse contains the admin interface and acts as the central coordinating
server for the system. All database access goes through the courthouse, mostly by
using its api (code is in courthouse/views/api.py)

```bash
# Install virtualenv
#
# We need to go through some contortions on loki, since we don't have root access. On
# a system you control you could just install virtualenv to the system (e.g. sudo apt-get install python-virtualenv)
#
# --user installs to the home directory, so you don't need root
# --extra-index-url is needed, because loki seems to be forcing https
pip install --user --extra-index-url https://pypi.python.org/simple/ virtualenv

# Add user's python bin folder to path, so virtualenv can be called
echo "export PATH=$PATH:$HOME/.local/bin" >> ~/.profile

# Clone the code_court repository
git clone https://github.com/unoacm/code_court.git

# Create a virtualenv for the courthouse
# We want to use the latest python3 version, so
# specify that path (python3.6 would be idea, python3.4 is fine, though)
cd code_court/code_court/courthouse
virtualenv env -p /usr/local/bin/python3.4

# Source the virtualenv. Note that you will need to do this anytime
# you want to start the server
# (run `deactivate` to turn it off)
source env/bin/activate

# Run the courthouse
./web.py

# Accessing the webapp
#
# I couldn't figure out how to access the webapp on loki
# directly from a remote computer, so I used ssh port forwarding
# (you could also use a text based browser on loki to access the site
# directly `lynx localhost:9191`)
ssh -L 9191:loki:9191 loki

# Then go to localhost:9191/admin in a browser
# (Admin login is admin@example.org:pass)
```

## Setup for executor

The executor is the service that actually runs submitted code. Usually
it uses docker to securely run submissions, but it has a non-docker
mode for development. Look at the production setup docs for info on how
to run the executor using docker

```bash
# Make sure you've installed virtualenv and cloned the code_court
# repo (look at the courthouse setup instruction for more on that)

# Create and source executor virtualenv
cd code_court/code_court/executor
virtualenv env -p /usr/local/bin/python3.4
source env/bin/activate

# Install executor python dependencies
pip install -r requirements.txt

# Run the executor in insecure mode
./executor.py --insecure
```

## Setup for the defendant frontent

The defendant frontend is the interface that contestants use. It's a pure
frontend app (written using vuejs) that uses an api to communicate with the courthouse.

```
# ERROR, I couldn't get npm working on loki, which is required to build the frontend
```
