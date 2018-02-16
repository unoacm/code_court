# code\_court
Programming Competition Software

# Overview
Code\_court is composed of three separate components.
1. __courthouse__ - The backend api server and admin control panel
1. __defendant-frontend__ - The frontend app for contestants
1. __executor__ - The server that runs user submissions

# Setup
## Courthouse
1. Install dependencies (ubuntu example): `sudo apt install python3-dev nodejs bash libffi-dev libxml2-dev libxslt-dev gcc build-essential htop virtualenv docker.io npm python-pip -y`
1. Setup docker: `sudo systemctl start docker; sudo systemctl enable docker; sudo gpasswd -a $USER docker` (re-login to activate group)
1. Clone the code\_court repository: `git clone http://github.com/unoacm/code_court`
1. Start postgres (optional) (these instructions run it with docker)
   1. Verify that postgres is set to be persisent or not depending on needs in `~/code_court/code_court/start_dev_postgres.sh`
   1. Start postgres with `~/code_court/code_court/start_dev_postgres.sh`
1. Compile defendant-frontend
   1. Run `cd ~/code_court/code_court/defendant-frontend && npm run build` (this will deploy the defendant files to they will be served by the courthouse)
1. Start courthouse
   1. Setup a virtualenv for the courthouse python dependencies: `virtualenv -p /usr/bin/python3 ~/courthoue_env`
   1. Install pip dependencies: `. ~/courthouse_env/bin/activate && pip install -r ~/code_court/code_court/courthouse/requirements.txt`
   1. Start the courthouse
      1. Either with postgres `cd ~/code_court/code_court/courthouse && ./start_with_postgres.sh`
      1. or with sqlite `cd ~/code_court/code_court/courthouse && ./start.sh`

## Executor
1. Install dependencies (ubuntu example): `sudo apt install python3-dev nodejs bash libffi-dev libxml2-dev libxslt-dev gcc build-essential htop virtualenv docker.io npm python-pip -y`
1. Clone the code\_court repository: `git clone http://github.com/unoacm/code_court`
1. Setup docker: `sudo systemctl start docker; sudo systemctl enable docker; sudo gpasswd -a $USER docker` (re-login to activate group)
1. Build the executor docker image: `cd ~/code_court/code_court/executor/executor/executor_container && ./build.sh`

# Debugging
## Misc
- There's a script at `~/code_court/code_court/executor/executor_container/temprun.sh` that will start up the executor container and put you into a shell in it
- uwsgitop can be useful for monitoring the status of the courthouse, install it with `sudo pip install uwsgitop` and run it with `uwsgitop localhost:1717`

# Good background reading
## docker
Redhat has a really good page on docker [here](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux_atomic_host/7/single/getting_started_with_containers/index). It has a little bit of RHEL-specific information, but most of it is general.
