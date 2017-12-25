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

# # Download German VoxForge dataset and extract it
# getdata.sh

# # Adapt VoxForge dataset into TUDA format
# python local/Adapt_tuda.py

# Test/Train data prepare
RAWDATA=data/voxforge_train

# Filter by name
FILTERBYNAME="*.xml"

find $RAWDATA/$FILTERBYNAME -type f > data/waveIDs.txt

RAWDATA_Test=../../kaldi-tuda-de/s5/data/wav/german-speechdata-package-v2
find $RAWDATA_Test/test/$FILTERBYNAME -type f >> data/waveIDs.txt

python local/data_prepare.py -f data/waveIDs.txt
for x in train test ; do
  utils/utt2spk_to_spk2utt.pl data/$x/utt2spk > data/$x/spk2utt
done

# Get freely available phoneme dictionaries, if they are not already downloaded
if [ ! -f data/lexicon/de.txt ]
then
    wget --directory-prefix=data/lexicon/ https://raw.githubusercontent.com/marytts/marytts-lexicon-de/master/modules/de/lexicon/de.txt
    # wget --directory-prefix=data/lexicon/ https://raw.githubusercontent.com/marytts/marytts/master/marytts-languages/marytts-lang-de/lib/modules/de/lexicon/de.txt
    echo "data/lexicon/train.txt">> data/lexicon_ids.txt
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
echo 'build_big_lexicon'
python local/build_big_lexicon.py -f data/lexicon_ids.txt -e data/local/combined.dict
echo 'export_lexicon'
python local/export_lexicon.py -f data/local/combined.dict -o data/local/dict/lexiconp.txt

#Move old lang dir if it exists
mkdir -p data/lang/old
mv data/lang/* data/lang/old

export LC_ALL=C

#Prepare phoneme data for Kaldi
utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang

#Todo: download source sentence archive for LM building

mkdir -p data/local/lm/

if [ ! -f data/local/lm/cleaned.gz ]
then
   wget --directory-prefix=data/local/lm/ http://speech.tools/kaldi_tuda_de/German_sentences_8mil_filtered_maryfied.txt.gz
   mv data/local/lm/German_sentences_8mil_filtered_maryfied.txt.gz data/local/lm/cleaned.gz
fi

# Prepare ARPA LM

# If you wont to build your own:
echo "local/build_lm.sh"
local/build_lm.sh

# Transform LM into Kaldi LM format
echo "local/format_data.sh"
local/format_data.sh
