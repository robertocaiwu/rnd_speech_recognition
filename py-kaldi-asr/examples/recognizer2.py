#!/usr/bin/env python
# coding: utf-8

import pyaudio
import wave
import audioop
import sys
import os
sys.path.insert(0, '/home/rob/speech/py-kaldi-asr')
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

MODELDIR    = 'data/models/nnet3_de/'
MODEL       = 'tdnn_250'
WAVFILES    = [ 'data/2015-01-27-12-32-58_Kinect-Beam.wav', 'data/2015-01-27-12-34-46_Kinect-Beam.wav']
DATADIR     = './data/audio/'

# Options
CHUNK = 1024#128 # The size of each audio chunk coming from the input device.
FORMAT = pyaudio.paInt16 # Should not be changed, as this format is best for speech recognition.
CHANNELS = 1
RATE = 48000 #16000 # Speech recognition only works well with this rate.  Don't change unless your microphone demands it.
RECORD_SECONDS = 5 # Number of seconds to record, can be changed.
WAVE_OUTPUT_FILENAME_48 = "output48.wav" # Where to save the recording from the microphone.
WAVE_OUTPUT_FILENAME_16 = "output16.wav"

def downsampleWav(src, dst, inrate=48000, outrate=16000, inchannels=1, outchannels=1):
	if not os.path.exists(src):
		print( 'Source not found!')
		return False

	if not os.path.exists(os.path.dirname(dst)):
		os.makedirs(os.path.dirname(dst))

	try:
		s_read = wave.open(src, 'r')
		s_write = wave.open(dst, 'w')
	except:
		print('Failed to open files!')
		return False

	n_frames = s_read.getnframes()
	data = s_read.readframes(n_frames)

	try:
		converted = audioop.ratecv(data, 2, inchannels, inrate, outrate, None)
		if outchannels == 1 & inchannels != 1:
			converted[0] = audioop.tomono(converted[0], 2, 1, 0)
	except:
		print ('Failed to downsample wav')
		return False

	try:
		s_write.setparams((outchannels, 2, outrate, 0, 'NONE', 'Uncompressed'))
		s_write.writeframes(converted[0])
	except:
		print ('Failed to write wav')
		return False

	try:
		s_read.close()
		s_write.close()
	except:
		print ('Failed to close wav files')
		return False

	return True


def save_audio(wav_file):
	"""
	Stream audio from an input device and save it.
	"""
	p = pyaudio.PyAudio()

	device = 0
	# p.get_device_info_by_index(0)

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

	# downsampleWav(DATADIR + wav_file, DATADIR + WAVE_OUTPUT_FILENAME_16)

# Run the thing!
if __name__ == '__main__':
	text = input("What language do you want to recognize? en/de")

	if(text=='en'):
		MODELDIR    = 'data/models/nnet3_en'
	elif(text=='de'):
		MODELDIR    = 'data/models/nnet3_de'
	print( '%s loading model...' % MODEL)
	kaldi_model = KaldiNNet3OnlineModel (MODELDIR, MODEL, acoustic_scale=1.0, beam=7.0, frame_subsampling_factor=3)
	print( '%s loading model... done.' % MODEL)

	while(True):
		text = input("Test speech recognition? y/n")
		if(text=='y'):
			save_audio(WAVE_OUTPUT_FILENAME_48)
			decoder = KaldiNNet3OnlineDecoder (kaldi_model)
			WAVFILE = DATADIR + WAVE_OUTPUT_FILENAME_16
			print(WAVFILE)
			if decoder.decode_wav_file(WAVFILE):
				s = decoder.get_decoded_string()
				print ("Utterance: ", unicode(s[0], 'utf-8').encode('utf-8'))
		elif(text=='n'):
			break
		elif(text=='l'):
			for wavfile in os.listdir(DATADIR + 'default'):

				decoder = KaldiNNet3OnlineDecoder (kaldi_model)
				if decoder.decode_wav_file(wavfile):
					s = decoder.get_decoded_string()
					print ("Utterance: ", unicode(s[0], 'utf-8').encode('utf-8'))
