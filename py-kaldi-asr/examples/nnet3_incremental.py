#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2016, 2017 Guenter Bartsch
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
# WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
# MERCHANTABLITY OR NON-INFRINGEMENT.
# See the Apache 2 License for the specific language governing permissions and
# limitations under the License.
#
#
# slightly more advanced demonstration program for kaldiasr online nnet3 
# decoding where we stream audio frames incrementally to the decoder
#

import sys
import os
import wave
import struct
import numpy as np

from time import time

from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

MODELDIR    = 'data/models/kaldi-nnet3-voxforge-de-latest'
MODEL       = 'nnet_tdnn_a'
WAVFILE     = 'data/gsp1.wav'

print '%s loading model...' % MODEL
time_start = time()
kaldi_model = KaldiNNet3OnlineModel (MODELDIR, MODEL)
print '%s loading model... done, took %fs.' % (MODEL, time()-time_start)

decoder = KaldiNNet3OnlineDecoder (kaldi_model)

time_start = time()

wavf = wave.open(WAVFILE, 'rb')

# check format
assert wavf.getnchannels()==1
assert wavf.getsampwidth()==2

# process file in 250ms chunks

chunk_frames = 250 * wavf.getframerate() / 1000
tot_frames   = wavf.getnframes()

num_frames = 0
while num_frames < tot_frames:

    finalize = False
    if (num_frames + chunk_frames) < tot_frames:
        nframes = chunk_frames
    else:
        nframes = tot_frames - num_frames
        finalize = True

    frames = wavf.readframes(nframes)
    num_frames += nframes
    samples = struct.unpack_from('<%dh' % nframes, frames)

    decoder.decode(wavf.getframerate(), np.array(samples, dtype=np.float32), finalize)

    print "%6.3fs: %5d frames (%6.3fs) decoded." % (time()-time_start, num_frames, float(num_frames) / float(wavf.getframerate()) )

wavf.close()

s, l = decoder.get_decoded_string()
print
print "*****************************************************************"
print "**", WAVFILE
print "**", s
print "** %s likelihood:" % MODEL, l
print "*****************************************************************"
print
print "%s decoding took %8.2fs" % (MODEL, time() - time_start )

