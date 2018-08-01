import pyaudio
from ctypes import *
from contextlib import contextmanager

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

def find_device(p, tags):
	"""
	Find an audio device to read input from.
	"""
	device_index = None
	for i in range(p.get_device_count()):
		devinfo = p.get_device_info_by_index(i)
		print("Device %d: %s" % (i, devinfo["name"]))

		for keyword in tags:
			if keyword in devinfo["name"].lower():
				print("Found an input: device %d - %s"%(i, devinfo["name"]))
				device_index = i
				return device_index

	if device_index is None:
		print("No preferred input found; using default input device.")

	return device_index

if __name__ == "__main__":
	print('Mic test!')
	with noalsaerr():
			audio = pyaudio.PyAudio()
	result = []
	device = find_device(audio, ["pulse","input", "mic", "audio", "default"]) #
	device_count = audio.get_device_count()
	if device_count > 0:
		for i in range(device_count):
				device_info = audio.get_device_info_by_index(i)
				print('{0}, {1}'.format(device_info.get("name"),i)  )
	else:
		print('No devices detected')
