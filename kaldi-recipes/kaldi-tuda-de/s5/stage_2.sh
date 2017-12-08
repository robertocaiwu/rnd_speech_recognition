[ ! -L "steps" ] && ln -s ../../wsj/s5/steps

[ ! -L "utils" ] && ln -s ../../wsj/s5/utils

# mfccdir should be some place with a largish disk where you
# want to store MFCC features.
mfccdir=mfcc

stage=stage_2

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


time=$(date +"%Y-%m-%d %H:%M:%S")
echo "Starting aligning of tri1 model. $time" | tee -a exp/s2/$stage.log
steps/align_si.sh --nj $nJobs --cmd "$train_cmd" \
  data/train data/lang exp/s1/tri1.1.2000.30000 exp/s2/tri1_ali || exit 1;

testDir=test
# Here we start the AM
for it in 1; do
  for s in 2000 2500 3000; do #  2000 3000; do
    for g in 30000; do

      time=$(date +"%Y-%m-%d %H:%M:%S")
      echo "Start deltas+delta-deltas triphone model training: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
      # Train tri2a, which is deltas+delta+deltas
      time steps/train_deltas.sh --cmd "$train_cmd" \
        $s $g data/train data/lang exp/s2/tri1_ali exp/s2/tri2a.$it.$s.$g || exit 1;

      time=$(date +"%Y-%m-%d %H:%M:%S")
      echo "Start deltas+delta-deltas triphone model graph: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
      # First triphone decoding
      time utils/mkgraph.sh data/lang_test exp/s2/tri2a.$it.$s.$g exp/s2/tri2a.$it.$s.$g/graph || exit 1;

      time=$(date +"%Y-%m-%d %H:%M:%S")
      echo "Start deltas+delta-deltas triphone model decoding: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
      time steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" \
        exp/s2/tri2a.$it.$s.$g/graph data/$testDir exp/s2/tri2a.$it.$s.$g/decode

    done
  done

  for s in 3000; do #  2000 3000; do
    for g in 20000 40000; do

      time=$(date +"%Y-%m-%d %H:%M:%S")
      echo "Start deltas+delta-deltas triphone model training: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
      # Train tri2a, which is deltas+delta+deltas
      time steps/train_deltas.sh --cmd "$train_cmd" \
        $s $g data/train data/lang exp/s2/tri1_ali exp/s2/tri2a.$it.$s.$g || exit 1;

      time=$(date +"%Y-%m-%d %H:%M:%S")
      echo "Start deltas+delta-deltas triphone model graph: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
      # First triphone decoding
      time utils/mkgraph.sh data/lang_test exp/s2/tri2a.$it.$s.$g exp/s2/tri2a.$it.$s.$g/graph || exit 1;

      time=$(date +"%Y-%m-%d %H:%M:%S")
      echo "Start deltas+delta-deltas triphone model decoding: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
      time steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" \
        exp/s2/tri2a.$it.$s.$g/graph data/$testDir exp/s2/tri2a.$it.$s.$g/decode

    done
  done
done

# for it in 1; do
#   for s in 2000 2500 3000; do #  2000 3000; do
#     for g in 30000; do
#
#       time=$(date +"%Y-%m-%d %H:%M:%S")
#       echo "Start LDA+MLLT triphone model training: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
#       # train and decode tri2b [LDA+MLLT]
#       time steps/train_deltas.sh --cmd "$train_cmd" \
#         $s $g data/train data/lang exp/s2/tri1_ali exp/s2/tri2b.$it.$s.$g || exit 1;
#       # 4000 50000
#
#       time=$(date +"%Y-%m-%d %H:%M:%S")
#       echo "Start LDA+MLLT triphone model graph: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
#       # First triphone decoding
#       time utils/mkgraph.sh data/lang_test exp/s2/tri2b.$it.$s.$g exp/s2/tri2b.$it.$s.$g/graph || exit 1;
#
#       time=$(date +"%Y-%m-%d %H:%M:%S")
#       echo "Start LDA+MLLT triphone model decoding: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
#       time steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" \
#         exp/s2/tri2b.$it.$s.$g/graph data/$testDir exp/s2/tri2b.$it.$s.$g/decode
#
#     done
#   done
#
#   for s in 3000; do #  2000 3000; do
#     for g in 20000 40000; do
#
#       time=$(date +"%Y-%m-%d %H:%M:%S")
#       echo "Start LDA+MLLT triphone model training: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
#       # train and decode tri2b [LDA+MLLT]
#       time steps/train_deltas.sh --cmd "$train_cmd" \
#         $s $g data/train data/lang exp/s2/tri1_ali exp/s2/tri2b.$it.$s.$g || exit 1;
#       # 4000 50000
#
#       time=$(date +"%Y-%m-%d %H:%M:%S")
#       echo "Start LDA+MLLT triphone model graph: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
#       # First triphone decoding
#       time utils/mkgraph.sh data/lang_test exp/s2/tri2b.$it.$s.$g exp/s2/tri2b.$it.$s.$g/graph || exit 1;
#
#       time=$(date +"%Y-%m-%d %H:%M:%S")
#       echo "Start LDA+MLLT triphone model decoding: it:$it, s:$s, g:$g. $time" | tee -a exp/s2/$stage.log
#       time steps/decode.sh --nj $nDecodeJobs --cmd "$decode_cmd" \
#         exp/s2/tri2b.$it.$s.$g/graph data/$testDir exp/s2/tri2b.$it.$s.$g/decode
#
#     done
#   done
# done
