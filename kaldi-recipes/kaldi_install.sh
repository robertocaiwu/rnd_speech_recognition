#!/bin/bash

if [ $# -eq 0 ]; then
    stage=0
    install_kaldi=false
elif [ $# -eq 1 ]; then
    stage=$1
    install_kaldi=false
elif [ $# -eq 2 ]; then
    stage=$1
    install_kaldi=$2
elif [ $# -eq 3 ]; then
    stage=$1
    install_kaldi=false
else
    exit 1
fi

if [ $stage -le 0 ]; then
    # create list of packages to install
    packagelist=(
      automake
      autoconf
      git
      sox
      subversion
      libatlas3-base
      libatlas-base-dev
      python-pip
      cython
      portaudio19-dev
      python3-dev
    )
    ### install debian packages listed in array above
    sudo apt-get update
    sudo apt-get install -y ${packagelist[@]}

fi

if [ $stage -le 1 ]; then
    # Create installation folder for Kaldi
    if [ ! -d ~/speech ];
    then
      mkdir ~/speech
      cd ~/speech
    else
      cd ~/speech
    fi

    # Kaldi installation
    if [ ! -d kaldi ]; then
      git clone git@github.com:kaldi-asr/kaldi.git
      install_kaldi=true
    fi

    if [ "$install_kaldi" == true ]; then
      NPROC=$(nproc)
      make clean
      cd kaldi/tools
      make -j $NPROC
      cd ../src
      ./configure --shared
      make clean
      make depend -j $NPROC
      make -j $NPROC
    fi
fi

if [ $stage -le 2 ]; then
    echo "kaldi_root=$HOME/speech/kaldi
    Name: kaldi-asr
    Description: kaldi-asr speech recognition toolkit
    Version: 5.1
    Libs: -L\${kaldi_root}/tools/openfst/lib -L\${kaldi_root}/src/lib -lkaldi-decoder -lkaldi-lat -lkaldi-fstext -lkaldi-hmm -lkaldi-feat -lkaldi-transform -lkaldi-gmm -lkaldi-tree -lkaldi-util -lkaldi-matrix -lkaldi-base -lkaldi-nnet3 -lkaldi-online2
    Cflags: -I\${kaldi_root}/src  -I\${kaldi_root}/tools/openfst/include -I\${kaldi_root}/tools/ATLAS_headers/include
    " > ~/speech/kaldi-asr.pc

    LD_LIBRARY_PATH=$HOME/speech/kaldi/src/lib:$LD_LIBRARY_PATH
    PKG_CONFIG_PATH=$HOME/speech:$PKG_CONFIG_PATH
    echo $PKG_CONFIG_PATH

    # Installation of python packages used by Kaldi wrapper
    pip install --upgrade pip
    pip install --user numpy Cython pyaudio sounddevice webrtcvad py-kaldi-asr
fi

if [ $stage -le 3 ]; then
    # Installing library for performing speech recognition, with support for several engines and APIs, online and offline.
    git clone --single-branch --branch feature/py-kalid-asr_support git@github.com:robertocaiwu/speech_recognition.git
    cd ~/speech/speech_recognition
    python setup.py install
fi
