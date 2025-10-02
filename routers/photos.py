# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Библиотека работы с файлами
import os
import shutil

from sqlalchemy.testing.plugin.plugin_base import logging

# Импорт класса для логирования данный в GoogleSheet
from functions.logger import class_logging_info_in_GoogleSheet
# Импорт данных для работы с папками
from dates import pathsfiles
# Импорт функций для обработки фотографий
from functions.photos import convertimage, renameanduploadimage
# Объявления роутер сбор статистики
photos = APIRouter()

# Ручка для сканирования папки для разбора фотографий
# Без входных аргументов
@photos.get("/scanfolderforparsing", summary="Сканирование папки 'фото товара для выгрузки на сайт'")
def scan_folder_for_parsing():
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
                                # Уменьшение веса и подгонка фотографии
                                convertimage(pathimage)
                                # Функция выяснения данных о фотографии
                                dateimage = loggingooglesheets.select_dates_from_photo(pathimage)
                                # Функции записи данных в Google Sheets
                                loggingooglesheets.logging_dates_from_photo(dateimage)
                                loggingooglesheets.logging_dates_from_photo2(dateimage)
                                # Переименование и загрузка фотографии
                                renameanduploadimage(pathimage, numberfolder)
                                # Увеличиваем счётчик
                                numberfolder = numberfolder + 1
            # Отчищаем папку
            os.rmdir(pathfolder)
        return {
            "result": f"Папка для разбора фотографий полностью разобрана",
            "data": True}

# Ручка для сравнения двух папок с фотографиями между собой 1С сайт
# Входные аргументы:
#   Путь к первой папке
#   Путь ко второй папке
@photos.get("/scanfolder", summary="Сканирование папки на соответствие")
def scan_folder(pahtmainfolder, pathsitefolder):
    try:
        main_site = set(os.listdir(pahtmainfolder))-set(os.listdir(pathsitefolder))
        len_main_site = len(main_site)
        site_main = set(os.listdir(pathsitefolder))-set(os.listdir(pahtmainfolder))
        len_site_main = len(site_main)
        if len_main_site > 0:
            for element in main_site:
                oldpath = pahtmainfolder + "/" + element
                newpath = pathsitefolder + "/" + element
                shutil.copy(oldpath, newpath)
            return {
                "result": f"Копирование файлов из [{pahtmainfolder}] в [{pathsitefolder}] завершилось успешно",
                "firstfolder": f"Количество файлов: [{len(os.listdir(pahtmainfolder))}]",
                "secondfolder": f"Количество файлов: [{len(os.listdir(pathsitefolder))}]",
                "processed_files": len_main_site,
                "data": True}
        else:
            return {
                "result": f"Сравнение папки [{pahtmainfolder}] и папки [{pathsitefolder}] завершилось успешно",
                "firstfolder": f"Количество файлов: [{len(os.listdir(pahtmainfolder))}]",
                "secondfolder": f"Количество файлов: [{len(os.listdir(pathsitefolder))}]",
                "data": True}
    except Exception as Ex:
        return {
            "result": f"Сравнение папки {pahtmainfolder} и папки {pathsitefolder} завершилось ошибкой {Ex}",
            "data": False}

# Ручка для переименования файлов в папке в нижний регистр
# Входной аргумент:
#   Путь к папке
@photos.get("/lowwerfilesfromfolder", summary="Переименование всех файлов в папке в нижний регистр")
def lowwer_files_from_folder(pahtfolder):
    try:
        listdir = os.listdir(pahtfolder)
        lenlistdir = len(listdir)
        count = 0
        for element in listdir:
            if element.islower() == False:
                oldpath = pahtfolder + "/" + element
                newpath = pahtfolder + "/" + element.lower()
                os.rename(oldpath, newpath)
                count += 1
        return {
            "result": f"Переименование файлов в папке {pahtfolder} количеством {lenlistdir} завершилось успешно",
            "counts": count,
            "data": True,}
    except Exception as Ex:
        return {
            "result": f"Переименование файлов в папке {pahtfolder} завершилось c ошибкой.",
            "error": str(Ex),
            "data": False}

# Ручка для переименования всех файлов в папках
# Без входных аргументов
@photos.get("/renameallfilesfromfolers", summary="Переименование всех файлов(верхний регистр в нижний) во всех папках (1С, сайт)")
def rename_all_files_from_folders():
    path1cfolder = pathsfiles.main1cfolder
    pathsitefolder = pathsfiles.sitefolder
    try:
        listdirpath1cfolder = os.listdir(path1cfolder)[:-2]
        listdirpathsitefolder = os.listdir(pathsitefolder)
        counts = 0
        for element in listdirpath1cfolder:
            counts += lowwer_files_from_folder(path1cfolder + element + "/")['counts']
        for element in listdirpathsitefolder:
            counts += lowwer_files_from_folder(pathsitefolder + element + "/")['counts']
        return {
            "result": f"Переименование во всех папках успешно завершено.",
            "change_images": counts,
            "data": True}
    except Exception as Ex:
        return {
            "result": f"Переименование во всех папках завершилось c ошибкой.",
            "error": str(Ex),
            "data": False}

# Ручка для сопоставления всех папок между собой
# Без входных аргументов
@photos.get("/comparisonfolders", summary="Сопоставление папок между собой")
def comparison_folders():
    # Получение всех папок
    path1cfolder = pathsfiles.main1cfolder
    pathsitefolder = pathsfiles.sitefolder
    try:
        # Получение всех папок в главной папке
        listdirpath1cfolder = os.listdir(path1cfolder)[:-2]
        listdirpathsitefolder = os.listdir(pathsitefolder)
        # Флаг корректности операции
        flag = True
        # Текс корретной операции
        text = "Сопоставление папок между собой завершилось успешно."
        for element1c, elementsite in zip(listdirpath1cfolder, listdirpathsitefolder):
            firstpath = path1cfolder + element1c + "/"
            secondpath = pathsitefolder + elementsite + "/"
            # Вызов функции сравнения двух папок между собой
            dates = scan_folder(firstpath, secondpath)
            if dates['data'] == False:
                text = "Сопоставление папок между собой завершилось c ошибкой."
                flag = False
        # Проверка флага корректности работы
        return {
            "result": text,
            "data": flag}
    except Exception as Ex:
        return {
            "result": f"Сопоставление папок между собой завершилось c ошибкой.",
            "error": str(Ex),
            "data": False}