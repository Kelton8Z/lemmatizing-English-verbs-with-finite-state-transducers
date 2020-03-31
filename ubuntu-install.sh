#!/usr/bin/env bash

sudo add-apt-repository universe
sudo apt-get update

# Install Python 3.6
apt-get install -y python3.6 python3-pip
apt-get install -y python-dev
apt install python3-setuptools
apt install python3-pip

apt install gcc
apt install g++
apt install make

pwd
# Install openFST
wget http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.7.3.tar.gz

echo "building openfst"
tar -xvf openfst-1.7.3.tar.gz
cd openfst-1.7.3
echo "configuring openfst"
./configure --enable-far --prefix=/usr
echo "building openfst"
make
echo "installing openfst"
make install
echo "done installing openfst"
cd ..

# Install Python package requirements
pip3 install openfst

# Install fststr
git clone https://github.com/dmort27/fststr.git
cd fststr
python3 setup.py build
python3 setup.py install
cd ..

export LD_LIBRARY_PATH=/usr/local/lib
export LD_RUN_PATH=/usr/local/lib
