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

## Extract recordings to data/extracted directory and run the following:
# python local/Adapt_recordings_to_tuda.py

python local/data_prepare_test.py -f data/waveID.txt
for x in test1 test2 test3; do
  utils/utt2spk_to_spk2utt.pl data/$x/utt2spk > data/$x/spk2utt
done

nnet3_affix=_chain
dir=exp/nnet3${nnet3_affix}/tdnn_sp
train_ivector_dir=exp/nnet3${nnet3_affix}/ivectors_${train_set}_sp_hires_comb

for datadir in test1 test2 test3; do
  utils/copy_data_dir.sh data/$datadir data/${datadir}_hires
done

# do volume-perturbation on the training data prior to extracting hires
# features; this helps make trained nnets more invariant to test data volume.
utils/data/perturb_data_dir_volume.sh data/${train_set}_sp_hires

for datadir in test1 test2 test3; do
  steps/make_mfcc.sh --nj $nj --mfcc-config conf/mfcc_hires.conf \
    --cmd "$train_cmd" data/${datadir}_hires
  steps/compute_cmvn_stats.sh data/${datadir}_hires
  utils/fix_data_dir.sh data/${datadir}_hires
done

for data in test1 test2 test3; do
  steps/online/nnet2/extract_ivectors_online.sh --cmd "$train_cmd" --nj "$nj" \
    data/${data}_hires exp/nnet3${nnet3_affix}/extractor \
    exp/nnet3${nnet3_affix}/ivectors_${data}_hires
done

for data in test1 test2 test3; do
  steps/nnet3/decode.sh --num-threads 1 --nj $nDecodeJobs --cmd "$decode_cmd" \
                        --acwt 1.0 --post-decode-acwt 10.0 \
                        --online-ivector-dir exp/nnet3${nnet3_affix}/ivectors_${data}_hires \
                        --scoring-opts "--min-lmwt 5 " \
                        $dir/graph data/${data}_hires $dir/decode_${data} || exit 1;
done
