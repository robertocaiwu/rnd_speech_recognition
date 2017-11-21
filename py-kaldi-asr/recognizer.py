
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

MODELDIR    = 'data/models/kaldi-nnet3-voxforge-en-r20171030'
MODEL       = 'nnet_tdnn_a'
WAVFILES    = [ 'data/a0405.wav', 'data/a0406.wav', 'data/a0407.wav']

print '%s loading model...' % MODEL
kaldi_model = KaldiNNet3OnlineModel (MODELDIR, MODEL)
print '%s loading model... done.' % MODEL

decoder = KaldiNNet3OnlineDecoder (kaldi_model)
for WAVFILE in WAVFILES:
	if decoder.decode_wav_file(WAVFILE):
	    s = decoder.get_decoded_string()
	    print "Utterance: ", s
