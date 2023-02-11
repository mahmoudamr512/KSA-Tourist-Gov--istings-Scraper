import glob
import os
import time
import urllib.request

import requests
import speech_recognition as sr
from undetected_chromedriver import Chrome


class CaptchaSolver:
    """
    Solve Audio Captcha by downloading and getting the numbers out of captcha
    """

    def __init__(self, driver: Chrome) -> None:
        self.driver: Chrome = driver

    def run_solver(self, link):
        self.download_audio(link)
        keys = self.convert_to_text()
        return keys

    def download_audio(self, link) -> None:
        self.driver.execute_script(f"""window.open("{link}");""")
        print(f"""window.open("{link}");""")
        time.sleep(3)
        for file in os.listdir(os.getcwd()):
            if file.endswith(".wav"):
                os.rename(file, "sample.wav")

        self.path_to_wav = os.path.normpath(os.path.join(os.getcwd(), "sample.wav"))
        self.sample_audio = sr.AudioFile(self.path_to_wav)

    # translate audio to text with google voice recognition
    def convert_to_text(self):
        r = sr.Recognizer()
        with self.sample_audio as source:
            audio = r.record(source)
        key = r.recognize_google(audio)
        print(f"[INFO] Recaptcha Passcode: {key}")
        os.remove(self.path_to_wav)
        return key
