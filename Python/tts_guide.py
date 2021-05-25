import multiprocessing
from gtts import gTTS
from playsound import playsound
from time import sleep


class TTS:
    def __init__(self, save_name='tts.mp3', lang='ko', slow=False):
        self.save_name = save_name
        self.lang = lang
        self.slow = slow

    def run(self, txt):
        self.make_tts(txt)
        self.play_tts()

    def make_tts(self, txt):
        self.tts = gTTS(text=txt, lang=self.lang, slow=self.slow)
        self.tts.save(self.save_name)

    def play_tts(self):
        playsound(self.save_name)

if __name__ == '__main__':
    tts = TTS()
    p = multiprocessing.Process(target=tts.run, args=('반갑습니다', ))
    p.start()
    sleep(5)
    p = multiprocessing.Process(target=tts.run, args=('하이.', ))
    p.start()