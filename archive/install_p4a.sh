sudo apt install -y git zip unzip default-jdk python3-pip python3-setuptools autoconf libtool pkg-config zlib1g-dev cmake libffi-dev libssl-dev debhelper python3-dev
sudo pip install cython
sudo pip install -r requirements.txt
export PATH=$PATH:~/.local/bin/
sudo buildozer -v android debug