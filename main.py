import datetime
import random
import threading
import time
from threading import Thread
import LinkedIn.main
import pyautogui


def apply_linkedin():
    print(f"Apply threadStarting at{datetime.datetime.now()}")
    LinkedIn.main.LINKEDIN().apply()
    print(f"Apply threadFinished at{datetime.datetime.now()}")


def move_mouse():
    while True:
        x, _ = pyautogui.position()
        pyautogui.moveTo(x + 200, pyautogui.position().y, duration=1.0)
        pyautogui.moveTo(x, pyautogui.position().y, duration=0.5)
        time.sleep(random.randint(0, 10))


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    l_thread = threading.Thread(target=apply_linkedin)
    l_thread.start()
    m_thread = threading.Thread(target=move_mouse)
    m_thread.start()
    l_thread.join()
    m_thread.join()
