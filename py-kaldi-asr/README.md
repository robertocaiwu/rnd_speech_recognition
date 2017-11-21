# py-kaldi-asr

Some simple wrappers around kaldi-asr intended to make using kaldi's (online, nnet3)
decoders as convenient as possible. 

Target audience are developers who would like to use kaldi-asr as-is for speech
recognition in their application on GNU/Linux operating systems.

Constructive comments, patches and pull-requests are very welcome.

Example
=======

Simple wav file decoding:

```python
from kaldiasr.nnet3 import KaldiNNet3OnlineModel, KaldiNNet3OnlineDecoder

MODELDIR    = 'data/models/kaldi-nnet3-voxforge-de-r20161117'
MODEL       = 'nnet_tdnn_a'
WAVFILE     = 'data/single.wav'

model   = KaldiNNet3OnlineModel   (MODELDIR, MODEL)
decoder = KaldiNNet3OnlineDecoder (model)

if decoder.decode_wav_file(WAVFILE):

    print '%s decoding worked!' % model

    s, l = decoder.get_decoded_string()
    print
    print "*****************************************************************"
    print "**", s
    print "** %s likelihood:" % model, l
    print "*****************************************************************"
    print

else:
    print '%s decoding did not work :(' % model

```

Please check the examples directory for more example code.

Links
=====

* [Data / Models](http://goofy.zamia.org/voxforge/ "models")

* [Code](https://github.com/gooofy/py-kaldi-asr "github")

Requirements
============

* Python 2.7
* NumPy
* Cython
* [kaldi-asr 5.1](http://kaldi-asr.org/ "kaldi-asr.org")

Setup Notes
===========

At the time of this writing kaldi-asr does not seem to have an official way to
install it on a system. 

So, for now we will rely on pkg-config to provide LIBS and CFLAGS for compilation:
Create a file called `kaldi-asr.pc` somewhere in your `PKG_CONFIG_PATH` that provides
this information:

```bash
kaldi_root=/apps/kaldi

Name: kaldi-asr
Description: kaldi-asr speech recognition toolkit
Version: 5.1
Requires: atlas
Libs: -L${kaldi_root}/tools/openfst/lib -L${kaldi_root}/src/lib -lkaldi-decoder -lkaldi-lat -lkaldi-fstext -lkaldi-hmm -lkaldi-feat -lkaldi-transform -lkaldi-gmm -lkaldi-tree -lkaldi-util -lkaldi-matrix -lkaldi-base -lkaldi-nnet3 -lkaldi-online2
Cflags: -I${kaldi_root}/src  -I${kaldi_root}/tools/openfst/include
```

make sure `kaldi_root` points to wherever your kaldi checkout lives in your filesystem.

License
=======

My own code is Apache licensed unless otherwise noted in the script's copyright
headers.

Some scripts and files are based on works of others, in those cases it is my
intention to keep the original license intact. Please make sure to check the
copyright headers inside for more information.

Author
======

Guenter Bartsch <guenter@zamia.org>
Kaldi 5.1 adaptation contributed by mariasmo https://github.com/mariasmo

