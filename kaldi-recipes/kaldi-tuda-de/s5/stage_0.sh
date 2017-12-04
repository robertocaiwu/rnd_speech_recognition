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

if [ -f cmd.sh ]; then
      . cmd.sh; else
         echo "missing cmd.sh"; exit 1;
fi

if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;
fi


python local/prepare_dir_structure.py

if [ ! -d data/wav/german-speechdata-package-v2 ]
then
    wget --directory-prefix=data/wav/ http://speech.tools/kaldi_tuda_de/german-speechdata-package-v2.tar.gz
    cd data/wav/
    tar xvfz german-speechdata-package-v2.tar.gz
    cd ../../
fi

#adapt this to the Sprachdatenaufnahmen2014 folder on your disk
RAWDATA=data/wav/german-speechdata-package-v2

# Filter by name
FILTERBYNAME="*.xml"

find $RAWDATA/*/$FILTERBYNAME -type f > data/waveIDs.txt
python local/data_prepare.py -f data/waveIDs.txt



# Get freely available phoneme dictionaries, if they are not already downloaded
if [ ! -f data/lexicon/de.txt ]
then
    wget --directory-prefix=data/lexicon/ https://raw.githubusercontent.com/marytts/marytts/master/marytts-languages/marytts-lang-de/lib/modules/de/lexicon/de.txt
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
python local/build_big_lexicon.py -f data/lexicon_ids.txt -e data/local/combined.dict
python local/export_lexicon.py -f data/local/combined.dict -o data/local/dict/lexiconp.txt

#Move old lang dir if it exists
mkdir -p data/lang/old
mv data/lang/* data/lang/old
