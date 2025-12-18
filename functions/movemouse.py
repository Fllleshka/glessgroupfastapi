import pyautogui
import datetime

# Включение паузы 1.5 секунды между действиями
pyautogui.PAUSE = 1

# Функция перемещения мышки и кликов
def movemouse(massx, massy, numberbutton):
    for elem in range(0, len(massx)):
        #print(f'{elem + 1}\t\t[{massx[elem]}]\t[{massy[elem]}]')
        pyautogui.moveTo(massx[elem], massy[elem], duration=0.25)
        # Тип скриншота кнопка
        if elem == numberbutton:
            pyautogui.leftClick()
            reg = (0, 0, 1920, 1080)
            takeascreenshot("Button", "screenshots/proofofwork/", reg)
        else:
            pyautogui.leftClick()

# Функция скриншота
def takeascreenshot(name, path, reg):
    # Время сейчас
    today = datetime.datetime.today()
    todaytime = today.strftime("%d.%m.%Y.%H.%M.%S")
    path = path + name + " " + todaytime + ".png"
    screen = pyautogui.screenshot(path, region = reg)