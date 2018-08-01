#!/usr/bin/env python
# coding: utf-8

import pyaudio
import wave
import audioop
import sys
import os
sys.path.insert(0, '/home/rob/speech/py-kaldi-asr')
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

MODELDIR    = './data/models/nnet3_en/'
MODEL       = 'model'
WAVFILES    = [ 'data/dw961.wav']
DATADIR     = './data/audio/'

# Options
CHUNK = 1024#128 # The size of each audio chunk coming from the input device.
FORMAT = pyaudio.paInt16 # Should not be changed, as this format is best for speech recognition.
CHANNELS = 1
RATE = 48000 #16000 # Speech recognition only works well with this rate.  Don't change unless your microphone demands it.
RECORD_SECONDS = 5 # Number of seconds to record, can be changed.
WAVE_OUTPUT_FILENAME_48 = "output48.wav" # Where to save the recording from the microphone.
WAVE_OUTPUT_FILENAME_16 = "output16.wav"

# Run the thing!
if __name__ == '__main__':
	# text = input("What language do you want to recognize? en/de")

	MODELDIR    = 'data/models/nnet3_en'
	print( '%s loading model...' % MODEL)
	kaldi_model = KaldiNNet3OnlineModel (MODELDIR, MODEL, acoustic_scale=1.0, beam=7.0, frame_subsampling_factor=3)
	print( '%s loading model... done.' % MODEL)
	decoder = KaldiNNet3OnlineDecoder (kaldi_model)
	if decoder.decode_wav_file(WAVFILES[0]):
		s = decoder.get_decoded_string()
		print ("Utterance: ", s[0])
