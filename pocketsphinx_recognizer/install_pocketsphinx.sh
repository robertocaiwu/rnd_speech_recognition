#!/bin/bash

# Clone sphinxbase and pocketsphinx repositories

# - git:
#     local-name: sphinxbase
#     uri: git@github.com:cmusphinx/sphinxbase.git
#     version: master
#
# - git:
#     local-name: pocketsphinx
#     uri: git@github.com:cmusphinx/pocketsphinx.git
#     version: master

# create list of packages to install
packagelist=(
  libtool
  automake
  bison
  swig
  python-pyaudio
  python3-pyaudio
)

### install debian packages listed in array above
sudo apt-get update
sudo apt-get install -y ${packagelist[@]}


if [ ! -d sphinxbase ]
then
  git clone git@github.com:cmusphinx/sphinxbase.git
fi
cd sphinxbase
./autogen.sh
./configure
make check
sudo make install
cd ..

if [ ! -d pocketsphinx ]
then
  git clone git@github.com:cmusphinx/pocketsphinx.git
fi

cd pocketsphinx
./autogen.sh
./configure
make check
sudo make install

echo 'export PKG_CONFIG_PATH=~/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=~/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

source ~/.bashrc
