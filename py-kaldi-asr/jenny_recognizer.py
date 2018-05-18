#!/usr/bin/env python
# coding: utf-8

import pyaudio
import wave
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

MODELDIR    = 'data/models/nnet3_de'
MODEL       = 'tdnn_sp'
WAVFILES    = [ 'data/2015-01-27-12-32-58_Kinect-Beam.wav', 'data/2015-01-27-12-34-46_Kinect-Beam.wav']
DATADIR     = './data/'

# Options
CHUNK = 128 # The size of each audio chunk coming from the input device.
FORMAT = pyaudio.paInt16 # Should not be changed, as this format is best for speech recognition.
CHANNELS = 1
RATE = 48000 # Speech recognition only works well with this rate.  Don't change unless your microphone demands it.
RECORD_SECONDS = 10 # Number of seconds to record, can be changed.
WAVE_OUTPUT_FILENAME = "output.wav" # Where to save the recording from the microphone.

def save_audio(wav_file):
        """
        Stream audio from an input device and save it.
        """
        p = pyaudio.PyAudio()

        device = 0

        #find_device(p, ["pulse", "input", "mic", "audio", "default"])
        device_info = p.get_device_info_by_index(device)
        #channels = int(device_info['maxInputChannels'])

        stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=device
        )

        print("recording...")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()

        p.terminate()

        wf = wave.open(DATADIR + wav_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()


# Run the thing!
if __name__ == '__main__':
        text = raw_input("What language do you want to recognize? en/de")

        if(text=='en'):
                MODELDIR    = 'data/models/nnet_en'
                MODEL       = 'nnet_tdnn_a'
        elif(text=='en3'):
                MODELDIR    = 'data/models/nnet_en3'
        elif(text=='de'):
                MODELDIR    = 'data/models/nnet_de'
                MODEL       = 'nnet_tdnn_a'

        print('%s model directory... ' % MODELDIR)
        print('%s loading model...' % MODEL)
        kaldi_model = KaldiNNet3OnlineModel (MODELDIR, MODEL)
        print( '%s loading model... done.' % MODEL              )
        RECORD_SECONDS = int(raw_input("How many seconds to record?"))
        if (RECORD_SECONDS < 1):
                RECORD_SECONDS = 5
        while(True):
                text = raw_input("Test speech recognition? y/n")
                if(text=='y'):
                        save_audio(WAVE_OUTPUT_FILENAME)
                        decoder = KaldiNNet3OnlineDecoder (kaldi_model)
                        WAVFILE = DATADIR + WAVE_OUTPUT_FILENAME
                        if decoder.decode_wav_file(WAVFILE):
                                s = decoder.get_decoded_string()
                                print "Utterance: ", unicode(s[0], 'utf-8').encode('utf-8')
                elif(text=='n'):
                        break
                elif(text=='l'):
                        WAVFILES    = [ 'data/2015-01-27-12-32-58_Kinect-Beam.wav', \
                                        'data/2015-01-27-12-34-36_Kinect-Beam.wav', \
                                        'data/2015-01-27-12-34-46_Kinect-Beam.wav']
                        decoder = KaldiNNet3OnlineDecoder (kaldi_model)
                        if decoder.decode_wav_file(WAVFILES[0]):
                                s = decoder.get_decoded_string()
                                print "Utterance: ", unicode(s[0], 'utf-8').encode('utf-8')
