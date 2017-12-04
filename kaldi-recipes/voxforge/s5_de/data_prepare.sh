#!/bin/bash

# Copyright 2017 Roberto Cai
# Apache 2.0

#Now start preprocessing with KALDI scripts

if [ -f cmd.sh ]; then
      . cmd.sh; else
         echo "missing cmd.sh"; exit 1;
fi

#Path also sets LC_ALL=C for Kaldi, otherwise you will experience strange (and hard to debug!) bugs. It should be set here, after the python scripts and not at the beginning of this script
if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;

fi

[ ! -L "steps" ] && ln -s ../../wsj/s5/steps

[ ! -L "utils" ] && ln -s ../../wsj/s5/utils

# mfccdir should be some place with a largish disk where you
# want to store MFCC features.
mfccdir=mfcc

utf8()
{
    iconv -f ISO-8859-1 -t UTF-8 $1 > $1.tmp
    mv $1.tmp $1
}

# Prepares KALDI dir structure and asks you where to store mfcc vectors and the final models (both can take up significant space)
python local/prepare_dir_structure.py

# The number of parallel jobs to be started for some parts of the recipe
# Make sure you have enough resources(CPUs and RAM) to accomodate this number of jobs
njobs=8

# This recipe can select subsets of VoxForge's data based on the "Pronunciation dialect"
# field in VF's etc/README files.
# dialects="()"

# The number of randomly selected speakers to be put in the test set
nspk_test=1

# Test-time language model order
lm_order=2

# Word position dependent phones?
pos_dep_phones=true

# The directory below will be used to link to a subset of the user directories
# based on various criteria(currently just speaker's accent)
selected=${DATA_ROOT}/selected

# The user of this script could change some of the above parameters. Example:
# /bin/bash run.sh --pos-dep-phones false
. utils/parse_options.sh || exit 1

[[ $# -ge 1 ]] && { echo "Unexpected arguments"; exit 1; }

# Select a subset of the data to use
# WARNING: the destination directory will be deleted if it already exists!

# echo "selecting dialect"
local/voxforge_select.sh --dialect $dialects \
  ${DATA_ROOT}/extracted ${selected} || exit 1
#
# # Mapping the anonymous speakers to unique IDs
echo "Mapping anonymus speakers to unique IDs"
local/voxforge_map_anonymous.sh ${selected} || exit 1

# Initial normalization of the data
echo "Initial normalization of the data"
local/voxforge_data_prep.sh --nspk_test ${nspk_test} ${selected} || exit 1

mkdir -p /data/train/
if [ ! -f data/train/text ]
then
  cp data/local/train_trans.txt data/train/text
fi

if [ ! -f data/train/wav.scp ]
then
  cp data/local/train_wav.scp data/train/wav.scp
fi
if [ ! -f data/train/utt2spk ]
then
  cp data/local/train.utt2spk data/train/utt2spk
fi
if [ ! -f data/train/spk2utt ]
then
  cp data/local/train.spk2utt data/train/spk2utt
fi

## Preparing the test dataset from kaldi-tuda-de
RAWDATA=../../kaldi-tuda-de/s5/data/wav/german-speechdata-package-v2
FILTERBYNAME="*.xml"
find $RAWDATA/test/$FILTERBYNAME -type f > data/waveIDs.txt
python local/data_prepare.py -f data/waveIDs.txt
utils/utt2spk_to_spk2utt.pl data/test/utt2spk > data/test/spk2utt

# Get freely available phoneme dictionaries, if they are not already downloaded
if [ ! -f data/lexicon/de.txt ]
then
    wget --directory-prefix=data/lexicon/ https://raw.githubusercontent.com/marytts/marytts-lexicon-de/master/modules/de/lexicon/de.txt
    #data/lexicon/train.txt only exists after kaldi-tuda-de has been run
    # echo "../../kaldi-tuda-de/s5/data/lexicon/train.txt">> data/lexicon_ids.txt
    echo "data/lexicon/de.txt">> data/lexicon_ids.txt
fi

if [ ! -f data/lexicon/VM.German.Wordforms ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/VM/VM.German.Wordforms
    echo "data/lexicon/VM.German.Wordforms">> data/lexicon_ids.txt
fi

if [ ! -f data/lexicon/RVG1_read.lex ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_read.lex
    echo "data/lexicon/RVG1_read.lex">> data/lexicon_ids.txt
fi

if [ ! -f data/lexicon/RVG1_trl.lex ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG1/RVG1_trl.lex
    echo "data/lexicon/RVG1_trl.lex">> data/lexicon_ids.txt
fi

if [ ! -f data/lexicon/LEXICON.TBL ]
then
    wget --directory-prefix=data/lexicon/ ftp://ftp.bas.uni-muenchen.de/pub/BAS/RVG-J/LEXICON.TBL
    utf8 data/lexicon/LEXICON.TBL
    echo "data/lexicon/LEXICON.TBL">> data/lexicon_ids.txt
fi


#Transform freely available dictionaries into lexiconp.txt file + extra files
mkdir -p data/local/dict/
python local/build_big_lexicon.py -f data/lexicon_ids.txt -e data/local/combined.dict
python local/export_lexicon.py -f data/local/combined.dict -o data/local/dict/lexiconp.txt
#
# #Move old lang dir if it exists
mkdir -p data/lang/old
mv data/lang/* data/lang/old

#Prepare phoneme data for Kaldi
utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang

# Now make MFCC features.
for x in train ; do
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs data/$x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data/$x
done
