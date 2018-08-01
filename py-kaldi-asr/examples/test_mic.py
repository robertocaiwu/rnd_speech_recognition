import os
import sys
import audioop
from ctypes import *
from contextlib import contextmanager
import speech_recognition as sr

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
	pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
	asound = cdll.LoadLibrary('libasound.so')
	asound.snd_lib_error_set_handler(c_error_handler)
	yield
	asound.snd_lib_error_set_handler(None)

class AudioSource(object):
	def __init__(self):
		raise NotImplementedError("this is an abstract class")

	def __enter__(self):
		raise NotImplementedError("this is an abstract class")

	def __exit__(self, exc_type, exc_value, traceback):
		raise NotImplementedError("this is an abstract class")

class Microphone():
	def __init__(self, device_index=None, sample_rate=None, chunk_size=1024):
		assert device_index is None or isinstance(device_index, int), "Device index must be None or an integer"
		assert sample_rate is None or (isinstance(sample_rate, int) and sample_rate > 0), "Sample rate must be None or a positive integer"
		assert isinstance(chunk_size, int) and chunk_size > 0, "Chunk size must be a positive integer"

		# set up PyAudio
		self.pyaudio_module = self.get_pyaudio()
		with noalsaerr():
			audio = self.pyaudio_module.PyAudio()

		try:
			count = audio.get_device_count()  # obtain device count
			# print(count)
			# print(device_index)
			if device_index is not None:  # ensure device index is in range
				assert 0 <= device_index < count, "Device index out of range ({} devices available; device index should be between 0 and {} inclusive)".format(count, count - 1)
				# print('not out of range')
			if sample_rate is None:  # automatically set the sample rate to the hardware's default sample rate if not specified
				device_info = audio.get_device_info_by_index(device_index) if device_index is not None else audio.get_default_input_device_info()
				assert isinstance(device_info.get("defaultSampleRate"), (float, int)) and device_info["defaultSampleRate"] > 0, "Invalid device info returned from PyAudio: {}".format(device_info)
				sample_rate = int(device_info["defaultSampleRate"])
		finally:
			audio.terminate()

		self.device_index = device_index
		self.format = self.pyaudio_module.paInt16  # 16-bit int sampling
		self.SAMPLE_WIDTH = self.pyaudio_module.get_sample_size(self.format)  # size of each sample
		self.SAMPLE_RATE = sample_rate  # sampling rate in Hertz
		self.CHUNK = chunk_size  # number of frames stored in each buffer

		self.audio = None
		self.stream = None

	@staticmethod
	def get_pyaudio():
		"""
		Imports the pyaudio module and checks its version. Throws exceptions if pyaudio can't be found or a wrong version is installed
		"""
		try:
			import pyaudio
		except ImportError:
			raise AttributeError("Could not find PyAudio; check installation")
		from distutils.version import LooseVersion
		if LooseVersion(pyaudio.__version__) < LooseVersion("0.2.11"):
			raise AttributeError("PyAudio 0.2.11 or later is required (found version {})".format(pyaudio.__version__))
		return pyaudio

	@staticmethod
	def list_microphone_names():
		"""
		Returns a list of the names of all available microphones. For microphones where the name can't be retrieved, the list entry contains ``None`` instead.
		The index of each microphone's name in the returned list is the same as its device index when creating a ``Microphone`` instance - if you want to use the microphone at index 3 in the returned list, use ``Microphone(device_index=3)``.
		"""
		audio = Microphone.get_pyaudio().PyAudio()
		try:
			result = []
			for i in range(audio.get_device_count()):
				device_info = audio.get_device_info_by_index(i)
				result.append(device_info.get("name"))
		finally:
			audio.terminate()
		return result

	@staticmethod
	def list_working_microphones():
		"""
		Returns a dictionary mapping device indices to microphone names, for microphones that are currently hearing sounds. When using this function, ensure that your microphone is unmuted and make some noise at it to ensure it will be detected as working.
		Each key in the returned dictionary can be passed to the ``Microphone`` constructor to use that microphone. For example, if the return value is ``{3: "HDA Intel PCH: ALC3232 Analog (hw:1,0)"}``, you can do ``Microphone(device_index=3)`` to use that microphone.
		"""
		pyaudio_module = Microphone.get_pyaudio()
		audio = pyaudio_module.PyAudio()
		try:
			result = {}
			for device_index in range(audio.get_device_count()):
				device_info = audio.get_device_info_by_index(device_index)
				device_name = device_info.get("name")
				assert isinstance(device_info.get("defaultSampleRate"), (float, int)) and device_info["defaultSampleRate"] > 0, "Invalid device info returned from PyAudio: {}".format(device_info)
				try:
					# read audio
					pyaudio_stream = audio.open(
						input_device_index=device_index, channels=1, format=pyaudio_module.paInt16,
						rate=int(device_info["defaultSampleRate"]), input=True
					)
					try:
						buffer = pyaudio_stream.read(1024)
						if not pyaudio_stream.is_stopped(): pyaudio_stream.stop_stream()
					finally:
						pyaudio_stream.close()
				except Exception:
					continue

				# compute RMS of debiased audio
				energy = -audioop.rms(buffer, 2)
				energy_bytes = chr(energy & 0xFF) + chr((energy >> 8) & 0xFF) if bytes is str else bytes([energy & 0xFF, (energy >> 8) & 0xFF])  # Python 2 compatibility
				debiased_energy = audioop.rms(audioop.add(buffer, energy_bytes * (len(buffer) // 2), 2), 2)

				if debiased_energy > 30:  # probably actually audio
					result[device_index] = device_name
		finally:
			audio.terminate()
		return result

if __name__ == "__main__":
	recognizer = sr.Recognizer()
	mic = sr.Microphone(device_index=5)
	# with noalsaerr():
	# 	audio = pyaudio.PyAudio()
	# mic = Microphone(device_index=5)
	# mic.list_microphone_names()
	# result = []
	# for i in range(audio.get_device_count()):
	# 	device_info = audio.get_device_info_by_index(i)
	# 	print('{0}, {1}'.format(device_info.get("name"),i)  )
