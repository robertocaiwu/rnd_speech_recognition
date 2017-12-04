[ ! -L "steps" ] && ln -s ../../wsj/s5/steps

[ ! -L "utils" ] && ln -s ../../wsj/s5/utils

# mfccdir should be some place with a largish disk where you
# want to store MFCC features.
mfccdir=mfcc

stage=stage_1

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

# #Prepare phoneme data for Kaldi
# utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang

# Now make MFCC features.
# time=$(date +"%Y-%m-%d %H:%M:%S")
# echo "Now start making MFCC features. $time" | tee -a $stage.log
# for x in train test dev ; do
#     utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
#     steps/make_mfcc.sh --cmd "$train_cmd" --nj $nJobs data/$x exp/make_mfcc/$x $mfccdir
#     utils/fix_data_dir.sh data/$x # some files fail to get mfcc for many reasons
#     steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir
#     utils/fix_data_dir.sh data/$x
# done
# time=$(date +"%Y-%m-%d %H:%M:%S")
# echo "Done making MFCC features and computing CMVN Stats. $time" | tee -a $stage.log
# #change this to test, if you want results on the test set

testDir=test
# Here we start the AM

for x in 1000 2000 3000 5000 10000 12425; do

  # Train monophone models on a subset of the data
  time utils/subset_data_dir.sh data/train $x data/s1/train.$x  ;

  for it in 1 2 3 4; do

    time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "Train iteration $it for monophone models with subset of $x. $time" | tee -a exp/s1/$stage.log
    # Train monophone models (right now makes no sense to do it only on a subset)
    # Note: the --boost-silence option should probably be omitted by default
    time steps/train_mono.sh --nj $nJobs --cmd "$train_cmd" \
      data/s1/train.$x data/lang exp/s1/mono.$it.$x || exit 1;
    time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "Trained iteration $it for monophone models with subset of $x. $time" | tee -a exp/s1/$stage.log

    echo "mkgraph iteration $it for monophone models with subset of $x. $time" | tee -a exp/s1/$stage.log
    # Monophone decoding
    time utils/mkgraph.sh data/lang_test exp/s1/mono.$it.$x exp/s1/mono.$it.$x/graph || exit 1
    time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "mkgraph iteration $it for monophone models with subset of $x. $time" | tee -a exp/s1/$stage.log

    echo "decode iteration $it for monophone models with subset of $x. $time" | tee -a exp/s1/$stage.log
    # note: local/decode.sh calls the command line once for each
    # test, and afterwards averages the WERs into (in this case
    # exp/mono/decode/
    time steps/decode.sh --config conf/decode.config --nj $nDecodeJobs --cmd "$decode_cmd" \
      exp/s1/mono.$it.$x/graph data/test exp/s1/mono.$it.$x/decode

    time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "decode iteration $it for monophone models with subset of $x. $time" | tee -a exp/s1/$stage.log
  done
done


time=$(date +"%Y-%m-%d %H:%M:%S")
echo "Done training monophone models. $time" | tee -a exp/s1/$stage.log
# to make sure you keep the results timed and owned
for x in exp/s1/*/decode*; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; \
done | sort -n -r -k2 > exp/s1/RESULTS.mono.$USER.$time


echo "Starting aligning of monophone model. $time" | tee -a exp/s1/$stage.log
# Get alignments from monophone system.
steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
  data/s1/train.12425 data/lang exp/s1/mono.1.12425 exp/s1/mono.1.12425_ali || exit 1;


for it in 1; do
  for s in 1500 ; do #  2000 2500; do
    for g in 20000; do

      time=$(date +"%Y-%m-%d %H:%M:%S")
      echo "Start standard triphone models training: it:$it, s:$s, g:$g. $time" | tee -a exp/s1/$stage.log
      # train tri1 [first triphone pass]
      steps/train_deltas.sh --cmd "$train_cmd" \
        $s $g data/train data/lang exp/s1/mono.1.12425_ali exp/s1/tri1.$it.$s.$g || exit 1;

      time=$(date +"%Y-%m-%d %H:%M:%S")
      echo "Start standard triphone models graph: it:$it, s:$s, g:$g. $time" | tee -a exp/s1/$stage.log
      # First triphone decoding
      time utils/mkgraph.sh data/lang_test exp/s1/tri1.$it.$s.$g exp/s1/tri1.$it.$s.$g/graph || exit 1;

      time=$(date +"%Y-%m-%d %H:%M:%S")
      echo "Start standard triphone models decoding: it:$it, s:$s, g:$g. $time" | tee -a exp/s1/$stage.log
      time steps/decode.sh  --nj $nDecodeJobs --cmd "$decode_cmd" \
        exp/s1/tri1.$it.$s.$g/graph data/$testDir exp/s1/tri1.$it.$s.$g/decode
    done
  done

  # for s in 2000; do
  #   for g in 10000 30000 40000; do
  #     time=$(date +"%Y-%m-%d %H:%M:%S")
  #     echo "Start standard triphone models training: it:$it, s:$s, g:$g. $time" | tee -a exp/s1/$stage.log
  #     # train tri1 [first triphone pass]
  #     steps/train_deltas.sh --cmd "$train_cmd" \
  #       $s $g data/train data/lang exp/s1/mono.1.12425_ali exp/s1/tri1.$it.$s.$g || exit 1;
  #
  #     time=$(date +"%Y-%m-%d %H:%M:%S")
  #     echo "Start standard triphone models graph: it:$it, s:$s, g:$g. $time" | tee -a exp/s1/$stage.log
  #     # First triphone decoding
  #     time utils/mkgraph.sh data/lang_test exp/s1/tri1.$it.$s.$g exp/s1/tri1.$it.$s.$g/graph || exit 1;
  #
  #     time=$(date +"%Y-%m-%d %H:%M:%S")
  #     echo "Start standard triphone models decoding: it:$it, s:$s, g:$g. $time" | tee -a exp/s1/$stage.log
  #     time steps/decode.sh  --nj $nDecodeJobs --cmd "$decode_cmd" \
  #       exp/s1/tri1.$it.$s.$g/graph data/$testDir exp/s1/tri1.$it.$s.$g/decode
  #   done
  # done
done
