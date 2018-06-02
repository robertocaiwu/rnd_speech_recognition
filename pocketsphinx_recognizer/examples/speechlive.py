import os
from pocketsphinx import LiveSpeech, get_model_path

model_path = get_model_path()
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
HMDIR = os.path.join(BASE_PATH, "hmm/en-us/cmusphinx-en-us.tar.gz")
LMDIR = os.path.join(BASE_PATH, "lm/en-us/en-us.lm.bin")
DICTD = os.path.join(BASE_PATH, "dict/en-us/cmudict-en-us.dict")
print(LMDIR)
print(os.path.join(model_path, 'en-us/en-us.lm.bin'))
speech = LiveSpeech(
    verbose=False,
    sampling_rate=16000,
    buffer_size=2048,
    no_search=False,
    full_utt=False,
    hmm=os.path.join(model_path, 'en-us'),
    lm=os.path.join(model_path, 'en-us.lm.bin'),
    dic=os.path.join(model_path, 'cmudict-en-us.dict')
)

for phrase in speech:
    print(phrase)
