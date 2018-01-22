import os
import sys

if __name__ == '__main__':

    audiodir = ['test_f1m', 'test_f05m', 'test_s1m']
    with open('waveID.txt', 'w') as waveid:
        for s in range(3):
            for file in os.listdir(audiodir[s]):
                if file.endswith(".xml"):
                    waveid.write('data/' + audiodir[s]+'/'+file+'\n')
