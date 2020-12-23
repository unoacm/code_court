# Production setup
NOTE: Currently untested for WSL. Docker only runs on Windows 10 Professional or Enterprise or there is this method that has variable mileage: https://blogs.msdn.microsoft.com/commandline/2017/12/08/cross-post-wsl-interoperability-with-docker/
## Courthouse
1. Install dependencies (ubuntu example): `sudo apt install python3-dev nodejs bash libffi-dev libxml2-dev libxslt-dev libpq-dev gcc build-essential htop virtualenv docker.io npm python3-pip -y`
1. Setup docker: `sudo systemctl start docker; sudo systemctl enable docker; sudo gpasswd -a $USER docker` (re-login to activate group)
1. Clone the code\_court repository: `git clone http://github.com/unoacm/code_court`
1. Start postgres (optional) (these instructions run it with docker)
   1. If you don't need postgres to be persistent start with`~/code_court/code_court/start_dev_postgres.sh`
   1. If you need postgres to be persistent, then start with`~/code_court/code_court/start_prod_postgres.sh`
1. Compile defendant-frontend
   1. Run `cd ~/code_court/code_court/defendant-frontend && npm install && npm run build` (this will deploy the defendant files to they will be served by the courthouse)
1. Start courthouse
   1. Setup a virtualenv for the courthouse python dependencies: `virtualenv -p /usr/bin/python3.x ~/courthouse_env`
   1. Install pip dependencies: `. ~/courthouse_env/bin/activate && pip install -r ~/code_court/code_court/courthouse/requirements.txt`
   1. Un-comment the lines for privilege dropping in `uwsgi.ini` and change the `uid` and `gid` to your account name (i.e, ubuntu/piyush/ben)
   1. Login to root with `sudo -s` and re-source the env with `source /home/ben/courthouse_env/bin/activate`
   1. Set the courthouse to production mode by setting the environment variable with `export CODE_COURT_PRODUCTION=1`
   1. Start the courthouse: `cd /home/ben/code_court/code_court/courthouse && ./start_with_postgres.sh`

## Executor
1. This should be done on a seperate server than the courthouse & frontend
1. Install dependencies (ubuntu example): `sudo apt install python3-dev nodejs bash libffi-dev libxml2-dev libxslt-dev libpq-dev gcc build-essential htop virtualenv docker.io npm python3-pip default-jdk lua5.1 guile-2.0 ruby rustc -y`
1. Clone the code\_court repository: `git clone http://github.com/unoacm/code_court`
1. Setup docker: `sudo systemctl start docker; sudo systemctl enable docker; sudo gpasswd -a $USER docker` (re-login to activate group)
1. Build the executor docker image: `cd ~/code_court/code_court/executor/executor/executor_container && ./build.sh`
1. Start the executor: `cd ~/code_court/code_court/executor && ./executor.py --url http://localhost`

# Debugging
## Misc
- There's a script at `~/code_court/code_court/executor/executor_container/temprun.sh` that will start up the executor container and put you into a shell in it
- uwsgitop can be useful for monitoring the status of the courthouse, install it with `sudo pip install uwsgitop` and run it with `uwsgitop localhost:1717`


