#!/bin/bash

SCRIPT_DIR=$(dirname "$0")

# misc packages
sudo apt-get upgrade -y
sudo apt-get install -y virtualenv \
                        tmux \
                        build-essential \
                        python3-dev \
                        libffi-dev \
                        libxml2-dev \
                        libxslt1-dev \
                        zlib1g-dev \
                        node \
                        nodejs-legacy \
                        npm \
                        htop

# install docker
sudo apt-get install \
     apt-transport-https \
     ca-certificates \
     curl \
     software-properties-common -y

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"

sudo apt-get update

sudo apt-get install docker-ce -y

sudo systemctl enable docker

sudo usermod -aG docker $USER

# setup courthouse
mkdir ~/envs
virtualenv -p /usr/bin/python3 ~/envs/courthouse
source ~/envs/courthouse/bin/activate

## add some swap for compiling lxml on a small machine
sudo dd if=/dev/zero of=/swapfile bs=1024 count=524288
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

cd $SCRIPT_DIR/../courthouse
pip install -r requirements.txt

# setup executor
mkdir ~/envs
virtualenv -p /usr/bin/python3 ~/envs/executor
source ~/envs/executor/bin/activate

cd $SCRIPT_DIR/../executor
pip install -r requirements.txt


# setup defendant-frontend
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
cd $SCRIPT_DIR/../defendant-frontend
npm install
