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

if [ -f cmd.sh ]; then
      . cmd.sh; else
         echo "missing cmd.sh"; exit 1;
fi

if [ -f path.sh ]; then
      . path.sh; else
         echo "missing path.sh"; exit 1;
fi

export LC_ALL=C

echo "training jobs: $nJobs"
echo "decode jobs: $nDecodeJobs"

#Prepare phoneme data for Kaldi
utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang

# Now make MFCC features.
time=$(date +"%Y-%m-%d %H:%M:%S")
echo "Now start making MFCC features. $time" | tee -a stage_1.log
for x in train dev test ; do
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs data/$x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
    steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
    utils/fix_data_dir.sh data/$x
done
time=$(date +"%Y-%m-%d %H:%M:%S")
echo "Done making MFCC features and computing CMVN Stats. $time" | tee -a stage_1.log
#change this to test, if you want results on the test set
testDir=test

# Here we start the AM
for x in 1000; do # 2000 3000 5000 10000 12425; do

  # Train monophone models on a subset of the data
  time utils/subset_data_dir.sh data/train $x data/s1/train.$x  ;


  time=$(date +"%Y-%m-%d %H:%M:%S")
  echo "Train monophone models with subset of $x. $time" | tee -a stage_1.log
  # Train monophone models (right now makes no sense to do it only on a subset)
  # Note: the --boost-silence option should probably be omitted by default
  time steps/train_mono.sh --nj $nJobs --cmd "$train_cmd" \
    data/s1/train.$x data/lang exp/mono || exit 1;
  time=$(date +"%Y-%m-%d %H:%M:%S")
  echo "Train monophone models with subset of $x. $time" | tee -a stage_1.log

  # Monophone decoding
  time utils/mkgraph.sh data/lang_test exp/s1/mono.$x exp/s1/mono.$x/graph || exit 1
  # note: local/decode.sh calls the command line once for each
  # test, and afterwards averages the WERs into (in this case
  # exp/mono/decode/
  time steps/decode.sh --config conf/decode.config --nj $njobs --cmd "$decode_cmd" \
    exp/s1/mono.$x/graph data/test exp/s1/mono.$x/decode
done

time=$(date +"%Y-%m-%d %H:%M:%S")
echo "Done training monophone models. $time" | tee -a stage_1.log
# # to make sure you keep the results timed and owned
# for x in exp/s1/*/decode*; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; \
# done | sort -n -r -k2 > exp/s1/RESULTS.mono.$USER.$time
#
# # Get alignments from monophone system.
# steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
#   data/train.12425 data/lang exp/s1/mono.12425 exp/s1/mono.12425_ali || exit 1;
#
# for x in 1000 1500 2000 2500; do
#   for x in 1000 2000 3000 5000 10000 12425; do
#     # train tri1 [first triphone pass]
#     steps/train_deltas.sh --cmd "$train_cmd" \
#       2500 30000 data/train data/lang exp/mono_ali exp/tri1 || exit 1;
#
#     # First triphone decoding
#     time utils/mkgraph.sh data/lang_test exp/tri1 exp/tri1/graph || exit 1;
#     time steps/decode.sh  --nj $nDecodeJobs --cmd "$decode_cmd" \
#       exp/tri1/graph data/$testDir exp/tri1/decode
#   done
# done
