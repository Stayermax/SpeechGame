import speech_recognition as sr
import os

from pocketsphinx import LiveSpeech, get_model_path

def sphinx_start():
    model_path = get_model_path()

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



def recognizer():
    r = sr.Recognizer()
    words = ' '
    with sr.Microphone() as source:
        print("Say something")
        audio = r.listen(source, 2, 2)
        #audio.get_flac_data()
    try:
        words = r.recognize_google(audio)
        print(words)
    except sr.WaitTimeoutError:
        print('You don\'t saying anything')
    except sr.UnknownValueError:
        print('I don\'t hear what are you saying')
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))
    return words
    #except sr.UnknownValueError:
    #    print("Don't hear")
    #except sr.RequestError as e:
    #    print("Service error; {0}".format(e))

if __name__ == '__main__':
    keywords = [('elephant', 1.0), ('kangaroo', 1.0), ('koala', 1.0), ('lion', 1.0), ('penguin', 1.0), ('rabbit', 1.0),
     ('raccoon', 1.0), ('tiger', 1.0), ('wolf', 1.0)]
    recognizer(keywords)
    #sphinx_start()
