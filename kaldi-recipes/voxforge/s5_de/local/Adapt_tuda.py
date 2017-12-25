
# coding: utf-8

# In[63]:


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


# In[70]:


# current_milli_time = lambda: int(round(time.time() * 1000))

def check_directories(directory):
    if not os.path.exists(directory):
        print('Creating directory: ' + directory)
        os.makedirs(directory)
    else:
        print('Directory already existst: ' + directory)

def get_time(n):
    t = 1514136271.6310985
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

def get_audio_directories(audiodir):
    global transcripts
    num = 1
    newdir = '../data/voxforge_train'
    # check_directories(newdir)
    for subdir in os.listdir(audiodir)[:]:

        if not '-' in subdir:
            logging.warn('skipping %s as it does not match our naming scheme' % subdir)
            continue

        logging.debug ("scanning %s in %s" % (subdir, audiodir))

        subdirfn  = '%s/%s'   % (audiodir, subdir)
        wavdirfn  = '%s/wav'  % subdirfn
        flacdirfn = '%s/flac' % subdirfn

        # do we have prompts?
        promptsfn = '%s/etc/prompts-original' % subdirfn

        prompts = read_promts(promptsfn)

        for key, promt in prompts.items():
#             print(subdir+'-'+key,promt)
#             xml_fn = '%s/%s-%s' % (newdir,subdir,key)
            xml_fn = '%s/%s' % (newdir,get_time(num))
            speaker_id = subdir
            sentence_id = key
            sentence = promt
            cleaned_sentence = promt
            make_xml(xml_fn, speaker_id, sentence_id, sentence, cleaned_sentence)
#             cfn = '%s-%s' % (subdir,key)
            cfn = get_time(num)
            w16filename = audio_convert(cfn, subdir, key, audiodir)
            if w16filename:
                if os.path.isfile (w16filename):
                    shutil.copy(w16filename,'%s/%s.wav' % (newdir,cfn))
            num += 1


def audio_convert (cfn, subdir, fn, audiodir):
    # global mfcc_dir
    wav16_dir = 'wav16_dir_de'
    check_directories(wav16_dir)
    # convert audio if not done yet
    w16filename = "%s/%s/%s/%s.wav" % (audiodir, subdir, wav16_dir, cfn)

    check_directories("%s/%s/%s" % (audiodir, subdir, wav16_dir))
    if not os.path.isfile (w16filename):
        wavfilename  = "%s/%s/wav/%s.wav" % (audiodir, subdir, fn)
        if not os.path.isfile (wavfilename):
            # flac ?
            flacfilename  = "%s/%s/flac/%s.flac" % (audiodir, subdir, fn)
            if not os.path.isfile (flacfilename):
                print ("WAV file '%s' does not exist, neither does FLAC file '%s'                       => skipping submission." % (wavfilename, flacfilename))
                return False
            print ("%-20s: converting %s => %s (16kHz mono)" % (cfn, flacfilename, w16filename))
            os.system ("sox '%s' -r 16000 -b 16 -c 1 %s" % (flacfilename, w16filename))
        else:
            print ("%-20s: converting %s => %s (16kHz mono)" % (cfn, wavfilename, w16filename))
            os.system ("sox '%s' -r 16000 -b 16 -c 1 %s" % (wavfilename, w16filename))

    return w16filename
if __name__ == '__main__':
    train_dir = './data/voxforge_train'
    check_directories(train_dir)
    audio_directory = './data/extracted'
    audio_directories = get_audio_directories(audio_directory)
