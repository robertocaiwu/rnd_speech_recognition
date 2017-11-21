
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

MODELDIR    = 'data/models/kaldi-nnet3-voxforge-en-r20171030'
MODEL       = 'nnet_tdnn_a'
WAVFILE     = 'data/a0405.wav'

decoder = KaldiNNet3OnlineDecoder (MODELDIR, MODEL)

if decoder.decode_wav_file(WAVFILE):

    print '%s decoding worked!' % MODEL

    s = decoder.get_decoded_string()
    print
    print "*****************************************************************"
    print "**", s
    print "** %s likelihood:" % MODEL, decoder.get_likelihood()
    print "*****************************************************************"
    print

else:
    print '%s decoding did not work :(' % MODEL