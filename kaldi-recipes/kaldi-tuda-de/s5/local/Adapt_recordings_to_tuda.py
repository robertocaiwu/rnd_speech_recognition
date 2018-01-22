
# coding: utf-8

# In[17]:


# -*- coding: utf-8 -*-
import numpy as np
import sys
import argparse
import os
import codecs
import re
import glob
import logging
import shutil
import unittest
import xml.etree.cElementTree as ET
import time
from bs4 import BeautifulSoup
from num2words import num2words
# from nltools import misc
from nltools.speech_transcripts import Transcripts
from shutil import copyfile


# In[18]:


int(round(time.time() * 1000))


# In[28]:


# current_milli_time = lambda: int(round(time.time() * 1000))

def check_directories(directory):
    if not os.path.exists(directory):
        print('Creating directory: ' + directory)
        os.makedirs(directory)
    else:
        print('Directory already existst')

def get_time(n):
#     t = 1514136271.6310985
    t = 1516637965.956
    s, ms = divmod(round(t * 1000)+(1000*n), 1000)  # (1236472051, 807)
    fl = '%s' % (time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime(s)))
    return fl


def make_xml(filename, speaker_id, sentence_id, sentence, cleaned_sentence):

    root = ET.Element("recording")
    ET.SubElement(root, "speaker_id").text = speaker_id
    ET.SubElement(root, "rate").text = rate = '16000'
    ET.SubElement(root, "angle").text = angle = '0'
    ET.SubElement(root, "gender").text = gender = 'Male'
    ET.SubElement(root, "ageclass").text = ageclass = 'NA'
    ET.SubElement(root, "sentence_id").text = sentence_id
    try:
        ET.SubElement(root, "sentence").text = str(sentence)
        ET.SubElement(root, "cleaned_sentence").text = str(cleaned_sentence)
    except:
        ET.SubElement(root, "sentence").text = sentence
        ET.SubElement(root, "cleaned_sentence").text = cleaned_sentence
    ET.SubElement(root, "corpus").text = corpus = 'WIKI'
    ET.SubElement(root, "muttersprachler").text = muttersprachler = 'Ja'
    ET.SubElement(root, "bundesland").text = bundesland = 'NA'
    sourceurls = ET.SubElement(root, "sourceurls")
    ET.SubElement(sourceurls, "url").text = sourceurls = 'NA'

    print(filename)
    document = ET.ElementTree(root)
    document.write(filename + ".xml", encoding='utf-8', xml_declaration=True)

def read_promts(promptsfn):
    prompts = {}
    if os.path.isfile(promptsfn):
        with open(promptsfn, 'rb') as promptsf:
            while True:
                line = promptsf.readline().decode('utf-8', errors='ignore')
                if not line:
                    break
                line = line.rstrip()
                if '\t' in line:
                    afn = line.split('\t')[0]
                    ts = line[len(afn)+1:]
                else:
                    afn = line.split(' ')[0]
                    ts = line[len(afn)+1:]

                prompts[afn] = ts.replace(';',',')
    return prompts

def get_audio_directories(newdir, audiodir):
    global transcripts
    num = 1
    check_directories(newdir)
    for subdir in sorted(os.listdir(audiodir))[:]:

        subdirfn  = '%s/%s'   % (audiodir, subdir)
        wavdirfn  = '%s/wav'  % subdirfn

        # do we have prompts?
        promptsfn = '%s/etc/promts-original' % subdirfn
        print(subdirfn)
        prompts = read_promts(promptsfn)
#         print(prompts)

        for key, promt in prompts.items():
            gettime = get_time(num)
            xml_fn = '%s/%s' % (newdir,gettime)
            speaker_id = subdir
            sentence_id = key
            sentence = promt
            cleaned_sentence = promt
            make_xml(xml_fn, speaker_id, sentence_id, sentence, cleaned_sentence)
            cfn = gettime
            wav_file = '%s/%s.wav' % (wavdirfn,key)
            if os.path.isfile (wav_file):
                shutil.copy(wav_file,'%s/%s.wav' % (newdir,cfn))
            num += 1


if __name__ == '__main__':
    scenarios = ['test_f1m', 'test_f05m', 'test_s1m']
    for s in range(3):
        test = scenarios[s]
        test_dir = 'data/%s' % (test)
        check_directories(test_dir)
        audio_directory = 'data/extracted/%s' % (test)
        audio_directories = get_audio_directories(test_dir, audio_directory)
