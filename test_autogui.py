import pyautogui
import time

time.sleep(2)

position=pyautogui.locateOnScreen('src//button.PNG' , confidence=0.9)
pyautogui.click(position)
pyautogui.click(position)