#!/usr/bin/env python
from __future__ import print_function
import requests

def check_internet():
    url='http://www.google.com/'
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet access.")
    return False

# Run the thing!
if __name__ == '__main__':
    print(check_internet())
