# -*- coding: utf-8 -*-

# Copyright 2015 Language Technology, Technische Universitaet Darmstadt (author: Benjamin Milde)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import argparse
import common_utils
import codecs
# import traceback
# import datetime
# import maryclient
# import StringIO
# import os
# import errno

# from bs4 import BeautifulSoup
#
from common_utils import make_sure_path_exists
# import collections
# import itertools

if __name__ == '__main__':

    wavscp =  codecs.open('../data/local/train_trans.txt','r','utf-8')
    datadir = '../data/train/'
    make_sure_path_exists(datadir)
    with codecs.open(datadir +'text', 'w', 'utf-8') as train_text:
        for wav in wavscp:
            try:
                train_text.write(wav)
            except Exception as err:
                print 'Error in file, omitting', wav
                print err
