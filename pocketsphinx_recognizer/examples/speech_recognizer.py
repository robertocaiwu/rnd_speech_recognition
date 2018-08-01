import speech_recognition as sr

def check_internet():
    url='http://www.google.com/'
    timeout = 5
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No internet access.")
    return False

# obtain audio from the microphone
while(True):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    if check_internet():
        # recognize speech using Sphinx
        try:
            print("Google thinks you said " + r.recognize_google(audio))
        except sr.UnknownValueError:
            print("Google could not understand audio")
        except sr.RequestError as e:
            print("Google error; {0}".format(e))
    else:
        # recognize speech using Sphinx
        try:
            print("Sphinx thinks you said " + r.recognize_sphinx(audio))
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))
