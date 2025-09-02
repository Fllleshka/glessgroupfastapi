# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Библиотека работы с файлами
import os

# Импорт класса для логирования данный в GoogleSheet
from functions.logger import class_logging_info_in_GoogleSheet
# Импорт данных для работы с папками
from dates import pathsfiles
# Импорт функций для обработки фотографий
from functions.photos import convertimage
# Объявления роутер сбор статистики
photos = APIRouter()

# Ручка для сканирования папки для разбора фотографий
# Без входных аргументов
@photos.get("/scanfolderforparsing", summary="Сканирование папки 'фото товара для выгрузки на сайт'")
def scan_folder_for_parsing():

    # Переменная для информации об обработанных фотографиях
    infoaboutphotos = []
    # Класс для логгирований данных в GoogleSheets
    loggingooglesheets = class_logging_info_in_GoogleSheet()
    # Проверка наличия фотографий
    # Если папок для разбора нет
    if os.listdir(pathsfiles.mainpathanalysis) == []:
        return {
            "result": f"В папке для разбора нету фотографий",
            "data": False}
    # Если есть папки для разбора
    else:
        # Пробегаемся по элеметам
        for element in os.listdir(pathsfiles.mainpathanalysis):
            # Выясняем путь к этому файлу
            pathfolder = pathsfiles.mainpathanalysis + "/" + element
            # Обыгрывание Thumbs.db
            if element == "Thumbs.db":
                # Пытаемся удалить данный файл
                try:
                    if os.access(pathfolder, os.R_OK and os.X_OK):
                        os.remove(pathfolder)
                except PermissionError:
                    return {
                        "result": f"Возникла ошибка при удаление системного файла Thumbs.db",
                        "typeerror": PermissionError,
                        "data": False}
            # Если же это не файл Thumbs.db
            else:
                # Получаем данные о файлах по этому пути
                nextlist = os.listdir(pathfolder)
                # Если папка пуста, то пишем о пустой папке
                if not nextlist:
                    return {
                        "result": f"Возникла ошибка при работе с папкой {element}. Она пуста",
                        "data": False}
                # Если папка не пуста
                else:
                    numberfolder = 1
                    for elem in nextlist:
                        # Обыгрывание Thumbs.db
                        if elem == "Thumbs.db":
                            continue
                        else:
                            # Условие перебора количества фотографий, так как 6 папки нет
                            if numberfolder >= 6:
                                break
                            else:
                                # Выясняем путь к файлу
                                pathimage = pathfolder + "/" + elem
                                # Функция сбора статистики по загруженным фотографиям
                                loggingooglesheets.logging_folders_with_photos(pathimage)
                                # Уменьшение веса и подгонка фотографии
                                infoaboutphotos.append(convertimage(pathimage))
                                # Переименование и загрузка фотографии
                                #self.renameanduploadimage(pathimage, numberfolder)
                                # Увеличиваем счётчик
                                #numberfolder = numberfolder + 1

    for elemment in infoaboutphotos:
        print(elemment)