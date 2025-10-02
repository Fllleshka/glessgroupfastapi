# Библиотека для работы с файлами cookie
import pickle

# Функция сохранения сессии
def save_session(driver, path):
    with open(path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

# Функция загрузки сессии
def load_session(driver, path):
    with open(path, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)