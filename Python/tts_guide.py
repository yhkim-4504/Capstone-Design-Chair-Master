import threading
from gtts import gTTS
from playsound import playsound

class TTS(threading.Thread):
    def __init__(self, txt, save_name='tts.mp3', lang='ko', slow=False):
        threading.Thread.__init__(self)
        self.txt = txt
        self.save_name = save_name
        self.lang = lang
        self.slow = slow

    def run(self):
        self.make_tts()
        self.play_tts()

    def make_tts(self):
        self.tts = gTTS(text=self.txt, lang=self.lang, slow=self.slow)
        self.tts.save(self.save_name)

    def play_tts(self):
        playsound(self.save_name)