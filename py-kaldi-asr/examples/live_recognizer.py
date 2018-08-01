#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback
import logging
import datetime
import sys
import os
import signal

from time                  import time
sys.path.insert(0, '/home/rob/speech/py-kaldi-asr')
from nltools               import misc
from nltools.pulserecorder import PulseRecorder
from nltools.vad           import VAD
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder
from optparse              import OptionParser
from setproctitle import setproctitle

PROC_TITLE                       = 'kaldi_live_demo'

SAMPLE_RATE                      = 16000
BUFFER_DURATION       = 30 # ms
FRAMES_PER_BUFFER                = int(SAMPLE_RATE * BUFFER_DURATION / 1000)

SOURCE                   = 'CM108'
VOLUME                   = 150
AGGRESSIVENESS           = 2

MODEL_DIR                = 'data/models/nnet3_en/'
MODEL                    = 'model'
ACOUSTIC_SCALE           = 1.0
BEAM                     = 7.0
FRAME_SUBSAMPLING_FACTOR = 3

STREAM_ID                        = 'mic'

#
# init
#

misc.init_app(PROC_TITLE)
logging.basicConfig(level=logging.INFO)

print("Kaldi live demo V0.1")

#
# cmdline, logging
#

parser = OptionParser("usage: %prog [options]")

parser.add_option ("-a", "--aggressiveness", dest="aggressiveness", type = "int", default=AGGRESSIVENESS,
                   help="VAD aggressiveness, default: %d" % AGGRESSIVENESS)

parser.add_option ("-m", "--model-dir", dest="model_dir", type = "string", default=MODEL_DIR,
                   help="kaldi model directory, default: %s" % MODEL_DIR)

parser.add_option ("-v", "--verbose", action="store_true", dest="verbose",
                   help="verbose output")

parser.add_option ("-s", "--source", dest="source", type = "string", default=SOURCE,
                   help="pulseaudio source, default: %s" % SOURCE)

parser.add_option ("-V", "--volume", dest="volume", type = "int", default=VOLUME,
                   help="broker port, default: %d" % VOLUME)

(options, args) = parser.parse_args()

if options.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

source         = options.source
volume         = options.volume
aggressiveness = options.aggressiveness
model_dir      = options.model_dir

#
# pulseaudio recorder
#

rec = PulseRecorder (source, SAMPLE_RATE, volume)

#
# VAD
#

vad = VAD(aggressiveness=AGGRESSIVENESS, sample_rate=SAMPLE_RATE)

#
# ASR
#

print ("Loading model from %s ..." % MODEL_DIR)
asr = KaldiNNet3OnlineModel(MODEL_DIR, MODEL)
#, acoustic_scale=ACOUSTIC_SCALE, beam=BEAM, frame_subsampling_factor=FRAME_SUBSAMPLING_FACTOR)
print("Loading model from %s, done ..." % MODEL_DIR)
#
# main
#

print("Start recording")
rec.start_recording(FRAMES_PER_BUFFER)

print ("Please speak.")

while True:

    samples = rec.get_samples()

    logging.debug("%d samples, %5.2f s" % (len(samples), float(len(samples)) / float(SAMPLE_RATE)))

    audio, finalize = vad.process_audio(samples)

    if not audio:
        continue

    logging.debug ('decoding audio len=%d finalize=%s audio=%s' % (len(audio), repr(finalize), audio[0].__class__))
    asr_decoder = KaldiNNet3OnlineDecoder(asr)
    asr_decoder.decode(SAMPLE_RATE, np.array(audio, dtype=np.float32), finalize)

    hstr, confidence = asr_decoder.get_decoded_string()
    hstr = hstr.decode('utf8').strip()

    print ("\r%s                     " % user_utt)

    if finalize:
        print('')
