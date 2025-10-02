# Импорт основной библиотеки FastAPI
import time

from fastapi import APIRouter
# Библиотека для логирования
import logging
# Импорт библиотеки для работы с файлами
import os
# Библиотека для работы с браузером
from selenium import webdriver
from selenium.webdriver.common.by import By

# Импорт класса для работы с Дром
from dates import datesfordrom
# Импорт класса для оповещения отвественных
from functions.logger import send_message_telegram_bot
# Импорт функций для работы с cookies
from functions.selenium_drom import *
# Объявления роутер для работы с AvitoAPI
drom = APIRouter()

# Ручка для вычисления баланса Дром
# Без входных аргументов
@drom.get("/getinfobalance", summary="Получение Баланса Дром")
def get_info_balance():
    # Инициализация класса с данными
    datafromfrom = datesfordrom()
    try:
        # Запускаем браузер GoogleChrome
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=chrome_options)
        # Открываем веб сайт
        driver.get(datafromfrom.mainurl)
        # Проверяем есть ли сохранённый файл cookie
        if os.path.exists(datafromfrom.cookiespath) != True:
            # Заполняем данные для входа
            logininput = datesfordrom.login
            passwordinput = datesfordrom.password
            input_field = driver.find_element(By.ID, "sign")
            input_field.clear()
            input_field.send_keys(logininput)
            input_field = driver.find_element(By.ID, "password")
            input_field.clear()
            input_field.send_keys(passwordinput)
            # Нажимаем на кнопку входа
            driver.find_element(By.ID, "signbutton").click()
            # Сохраняем cookie для дальнейшего использования
            save_session(driver, datafromfrom.cookiespath)

        # Загружаем данные файлов cookie
        load_session(driver, datafromfrom.cookiespath)
        # Перезагружаем страницу браузера
        driver.refresh()
        # Ищем данные о балансе
        balance = driver.find_element(By.CLASS_NAME,"personal-balance-info__balance").text
        time.sleep(3)
        # Закрываем браузер
        driver.quit()
        return {
            "result": f"Получение Баланса успешно завершено",
            "status": True,
            "data": balance}
    except Exception as e:
        return {
            "result": f"Сбой запроса токена авторизации",
            "data": e}