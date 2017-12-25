import os
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get waveIDs')
    parser.add_argument('-d', '--dir', dest='audiodir', help='Source dyrectory', type=str, default='data/voxforge_train')

    args = parser.parse_args()

    with open('data/waveIDs.txt', 'w') as waveid:
        for file in os.listdir(args.audiodir):
            if file.endswith(".xml"):
                waveid.write(args.audiodir+'/'+file+'\n')
