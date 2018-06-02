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
  automake
  bison
  swig
  python-pyaudio
  python3-pyaudio
)

### install debian packages listed in array above
sudo apt-get update
sudo apt-get install -y ${packagelist[@]}

git clone git@github.com:cmusphinx/sphinxbase.git

cd sphinxbase
./autogen.sh
./configure
make check
sudo make install

cd ..
git clone git@github.com:cmusphinx/pocketsphinx.git

cd pocketsphinx
./autogen.sh
./configure
make check
sudo make install

echo 'export PKG_CONFIG_PATH=~/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=~/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

source ~/.bashrc
