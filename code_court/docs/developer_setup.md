## Intro
Currently code\_court only runs on unix systems (linux, macos, etc). If you only have access to windows machines you have a few options (in order of preferability):

1. [Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/install-win10) (Should work for development, however with the current Windows Build(1709), docker is difficult to work with)
2. Run a linux [virtual machine](https://www.virtualbox.org/)
3. Run a linux container with [docker](https://www.docker.com/docker-windows)
4. Use a linux server (I like [Linode](https://www.linode.com/), [AWS](https://aws.amazon.com/) would be a good choice too)

I've also been playing around with running code\_court on loki, and have had mild success. You can see my notes on that in `loki_setup_example.md`.

## General setup

Here's a rough list of what you'll need to install. This command works for the latest ubuntu; you may need to adjust it for other distros.
`sudo apt install python3-dev nodejs bash libffi-dev libxml2-dev libxslt-dev gcc build-essential htop virtualenv docker.io npm python-pip default-jdk lua5.1 guile-2.0 ruby rustc -y`

Next you'll need to clone the repository
`git clone https://github.com/unoacm/code_court.git`


## Setup for courthouse

The courthouse contains the admin interface and acts as the central coordinating
server for the system. All database access goes through the courthouse, mostly by
using its api (in `courthouse/views/api.py`)

```bash
# Create a virtualenv for the courthouse
# We want to use the latest python3, so
# specify that path (python3.6 would be ideal, a lower version of 3 is fine, though)
cd code_court/code_court/courthouse
virtualenv env -p /usr/bin/python3.6

# Source the virtualenv. Note that you will need to do this anytime
# you want to start the server (run `deactivate` to turn it off)
source env/bin/activate

# Install the courthouse python dependencies
# into the virtualenv
pip install -r requirements.txt

# Run the courthouse
./web.py

# You can access the webapp by going to localhost:9191/admin
# in a browser
# (Admin login is admin:pass)
```

## Setup for executor

The executor is the service that actually runs submitted code. Usually
it uses docker to securely run submissions, but it has a non-docker
mode for development. Look at the production setup docs for info on how
to run the executor using docker

```bash
# Create and source executor virtualenv
cd code_court/code_court/executor
virtualenv env -p /usr/local/bin/python3.4
source env/bin/activate

# Install executor python dependencies
pip install -r requirements.txt

# Run the executor in insecure mode
# If you're doing development on the executor, you should
# run it in in both secure and insecure modes, see production_setup.md
# for more info on how to install the requirements for secure mode
./executor.py --insecure
```

## Setup for the defendant frontent

The defendant frontend is the interface that contestants use. It's a pure
frontend app (written using vuejs) that uses an api to communicate with the courthouse.

```bash
# Since the Debian and Ubuntu distros package managers have version that lag behind,
# we need a more recent version of nodejs (this might be WSL specific)
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs
# Install npm dependencies
cd code_court/code_court/defendant-frontend
npm install

# Run build, this will then be served at http://localhost:9191
# when you start the courthouse
npm run build

# Optional: If you're developing the frontend there's a way
# to run it that's a lot more pleasant. It's faster,
# automatically reloads, and shows errors.
# The courthouse still needs to be running, but you can access
# the defendant-frontend at http://localhost:8080
npm run dev

```

## Misc

## Run courthouse tests
```bash
cd code_court/code_court/courthouse
# make sure virtualenv is sourced
nosetests
```

## Commit checklist
### Courthouse
- [ ] make sure tests pass by running `nosetests`
- [ ] make sure code is correctly formatted by running `black` (`pip install black` to install)
