from distutils.core import setup
from distutils.extension import Extension
import numpy

try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
else:
    use_cython = True
cmdclass = { }
ext_modules = [ ]

if use_cython:
    ext_modules += [
        Extension("kaldiasr.nnet3", 
                  sources  = [ "kaldiasr/nnet3.pyx", "kaldiasr/nnet3_wrappers.cpp" ],
                  language = "c++",
                  extra_compile_args=['-std=gnu++11']),
    ]
    cmdclass.update({ 'build_ext': build_ext })
else:
    ext_modules += [
        Extension("kaldiasr.nnet3", 
                  sources  = [ "kaldiasr/nnet3.cpp", "kaldiasr/nnet3_wrappers.cpp" ],
                  language = "c++",),
    ]

setup(
    name                 = 'py-kaldi-asr',
    version              = '0.1.0',
    description          = 'Simple Python/Cython interface to kaldi-asr decoders',
    long_description     = open('README.md').read(),
    author               = 'Guenter Bartsch',
    author_email         = 'guenter@zamia.org',
    maintainer           = 'Guenter Bartsch',
    maintainer_email     = 'guenter@zamia.org',
    url                  = 'https://github.com/gooofy/py-kaldi-simple',
    # download_url         = 'https://pypi.python.org/pypi/kaldisimple',
    packages             = ['kaldiasr'],
    cmdclass             = cmdclass,
    ext_modules          = ext_modules,
    # include_dirs         = [numpy.get_include(), '/home/rob/speech_toolkit/kaldi/src', '/home/rob/speech_toolkit/kaldi/tools/openfst/include', '/home/rob/speech_toolkit/kaldi/src/ATLAS/include'],
    include_dirs         = [numpy.get_include()],
    classifiers          = [
                               'Development Status :: 2 - Pre-Alpha',
                               'Operating System :: POSIX :: Linux',
                               'License :: OSI Approved :: Apache Software License',
                               'Programming Language :: Python :: 2',
                               'Programming Language :: Python :: 2.7',
                               'Programming Language :: Cython',
                               'Programming Language :: C++',
                               'Intended Audience :: Developers',
                               'Topic :: Software Development :: Libraries :: Python Modules',
                               'Topic :: Multimedia :: Sound/Audio :: Speech'
                           ],
    license              = 'Apache',
    keywords             = 'kaldi-asr',
    # test_suite           = 'tests', 
    # include_package_data = True,
    # zip_safe             = False
    )

# FIXME: remove old code
# from distutils.core import setup
# from Cython.Build import cythonize
# import numpy
# 
# setup(ext_modules = cythonize(
#            "kaldisimple/kaldi_simple.pyx",               
#            sources  = ["kaldisimple/KaldiSimple.cpp"],  
#            language = "c++",
#       ),
#       include_dirs = [numpy.get_include()]
#      )
#
