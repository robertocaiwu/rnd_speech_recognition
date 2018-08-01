import os
from LiveSpeech import LiveSpeech

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
HMDIR = os.path.join(BASE_PATH, "hmm/en-us/")
LMDIR = os.path.join(BASE_PATH, "lm/en-us/en-us.lm")
DICTD = os.path.join(BASE_PATH, "dict/en-us/cmudict-en-us.dict")

speech = LiveSpeech(
    audio_device='pulse',
    verbose=False,
    sampling_rate=16000,
    buffer_size=2048,
    no_search=False,
    full_utt=False,
    hmm=os.path.join(BASE_PATH, HMDIR),
    lm=os.path.join(BASE_PATH, LMDIR),
    dic=os.path.join(BASE_PATH, DICTD)
)
print('done loading models...')
for phrase in speech:
    print(phrase)
