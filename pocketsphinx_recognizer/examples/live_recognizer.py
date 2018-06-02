import pyaudio
import wave
from sphinxbase.sphinxbase import *
from pocketsphinx.pocketsphinx import *
from os import environ, path
import os

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
config = Decoder.default_config()
config.set_string('-hmm', path.join(BASE_PATH, 'hmm/en-us/cmusphinx-en-us.tar.gz'))
config.set_string('-lm', path.join(BASE_PATH, 'lm/en-us/en-us.lm.bin'))
config.set_string('-dict', path.join(BASE_PATH, 'dict/en-us/cmudict-en-us.dict'))
# config.set_string('-logfn', '/dev/null')
decoder = Decoder(config)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
stream.start_stream()

in_speech_bf = False
decoder.start_utt()
while True:
    buf = stream.read(1024)
    if buf:
        decoder.process_raw(buf, False, False)
        if decoder.get_in_speech() != in_speech_bf:
            in_speech_bf = decoder.get_in_speech()
            if not in_speech_bf:
                decoder.end_utt()
                print('Result:', decoder.hyp().hypstr)
                decoder.start_utt()
    else:
        break
decoder.end_utt()
