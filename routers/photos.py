# Импорт основной библиотеки FastAPI
from fastapi import APIRouter
# Библиотека для отображения прогресс бара
from tqdm import tqdm
# Библиотека работы с файлами
import os
import shutil
# Библиотеки для сравнения двух картинок
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np
# Библиотека для логирования
from sqlalchemy.testing.plugin.plugin_base import logging
# Импорт класса для логирования данный в GoogleSheet
from functions.logger import class_logging_info_in_GoogleSheet
# Импорт данных для работы с папками
from dates import pathsfiles
# Импорт функций для обработки фотографий
from functions.photos import convertimage, renameanduploadimage
# Импорт валидатора данных (pydantic)
from pydantic import BaseModel

# Объявления роутер сбор статистики
photos = APIRouter()

# Определение Pydantic-схемы
class photosPydantic(BaseModel):
    result: bool
    text: str = None
    sameness: float = None
    error: str = None
    folders: int = None
    countfirstfolder: int = None
    countsecondfolder: int = None

# Ручка для сканирования папки для разбора фотографий
# Без входных аргументов
@photos.get("/scanfolderforparsing",
            summary="Сканирование папки 'фото товара для выгрузки на сайт'",
            response_model=photosPydantic)
def scan_folder_for_parsing():
    # Класс для логирования данных в GoogleSheets
    loggingooglesheets = class_logging_info_in_GoogleSheet()
    # Переменная для обновления данных
    massimages = [0, 0, 0, 0, 0]

    # Проверка наличия фотографий
    # Если папок для разбора нет
    if os.listdir(pathsfiles.mainpathanalysis) == []:
        return photosPydantic(result=False,
                              text="В папке для разбора нету фотографий")
    # Если есть папки для разбора
    else:
        folders = os.listdir(pathsfiles.mainpathanalysis)
        # Пробегаемся по элеметам
        for element in folders:
            # Выясняем путь к этому файлу
            pathfolder = pathsfiles.mainpathanalysis + "/" + element
            # Обыгрывание Thumbs.db
            if element == "Thumbs.db":
                # Пытаемся удалить данный файл
                try:
                    if os.access(pathfolder, os.R_OK and os.X_OK):
                        os.remove(pathfolder)
                except Exception:
                    return photosPydantic(result=False,
                                          text="Возникла ошибка при удаление системного файла Thumbs.db",
                                          error=Exception)
            # Если же это не файл Thumbs.db
            else:
                # Получаем данные о файлах по этому пути
                nextlist = os.listdir(pathfolder)
                # Если папка пуста, то пишем о пустой папке
                if not nextlist:
                    return photosPydantic(result=False,
                                          text=f"Возникла ошибка при работе с папкой {element}. Она пуста",
                                          error=Exception)
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
                                imagecreator = loggingooglesheets.select_dates_from_photo(pathimage)
                                # Функции записи данных в Google Sheets
                                #loggingooglesheets.logging_dates_from_photo(dateimage)
                                #loggingooglesheets.logging_dates_from_photo2(dateimage)
                                #loggingooglesheets.logging_all_dates_from_photo(dateimage)
                                # Переименование и загрузка фотографии
                                renameanduploadimage(pathimage, numberfolder)
                                # Увеличиваем счётчик папки
                                numberfolder = numberfolder + 1
                    #print(f"Количество фотографий в папке: {len(nextlist)}")
                    #print(f"Данные о владельце: {imagecreator}")
                    loggingooglesheets.logging_all_dates_from_photo(imagecreator, len(nextlist))
            # Отчищаем папку
            os.rmdir(pathfolder)
        # Отправляем данные
        return photosPydantic(result=True,
                              text=f"Папка для разбора фотографий полностью разобрана",
                              folders=len(folders))

# Ручка для сравнения двух папок с фотографиями между собой 1С сайт
# Входные аргументы:
#   Путь к первой папке
#   Путь ко второй папке
@photos.get("/scanfolder",
            summary="Сканирование папки на соответствие",
            response_model=photosPydantic)
def scan_folder(pahtmainfolder, pathsitefolder):
    try:
        # Разница между первой папки и второй
        main_site = set(os.listdir(pahtmainfolder))-set(os.listdir(pathsitefolder))
        len_main_site = len(main_site)
        site_main = set(os.listdir(pathsitefolder))-set(os.listdir(pahtmainfolder))
        len_site_main = len(site_main)
        countmainfolder = len(os.listdir(pahtmainfolder))
        countsitefolder = len(os.listdir(pathsitefolder))
        if len_main_site > 0:
            for element in main_site:
                oldpath = pahtmainfolder + "/" + element
                newpath = pathsitefolder + "/" + element
                shutil.copy(oldpath, newpath)

            return photosPydantic(result=True,
                                  text=f"Сравнение папки [{pahtmainfolder}] и папки [{pathsitefolder}] завершилось успешно",
                                  countfirstfolder=countmainfolder,
                                  countsecondfolder=countsitefolder,
                                  folders=len_main_site)
        else:
            return photosPydantic(result=True,
                                  text=f"Сравнение папки [{pahtmainfolder}] и папки [{pathsitefolder}] завершилось успешно",
                                  countfirstfolder=countmainfolder,
                                  countsecondfolder=countsitefolder,
                                  folders=len_site_main)
    except Exception as Ex:
        return photosPydantic(result=True,
                              text=f"Сравнение папки {pahtmainfolder} и папки {pathsitefolder} завершилось ошибкой {Ex}")

# Ручка для переименования файлов в папке в нижний регистр
# Входной аргумент:
#   Путь к папке
@photos.get("/lowwerfilesfromfolder",
            summary="Переименование всех файлов в папке в нижний регистр")
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
@photos.get("/renameallfilesfromfolers",
            summary="Переименование всех файлов(верхний регистр в нижний) во всех папках (1С, сайт)")
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
@photos.get("/comparisonfolders",
            summary="Сопоставление папок между собой")
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
        # Текс корректной операции
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

# Ручка для сопоставления файлом между собой
# Два входных аргумента:
#   Путь к первому файлу
#   Путь к второму файлу
@photos.get("/picturematching",
            summary="Сравнение двух файлов между собой (сопоставление картинок)",
            response_model=photosPydantic)
def picture_matching(firstpath, secondpath):
    #print(f"Работаем с файлами: [{firstpath}] и [{secondpath}]")

    try:
        # Проверка на существование файла
        if os.path.isfile(firstpath) and os.path.isfile(secondpath):

            # Чтение файла в байтовый массив
            img_array1 = np.fromfile(firstpath, dtype=np.uint8)
            img_array2 = np.fromfile(secondpath, dtype=np.uint8)
            # Декодирование массива в изображение OpenCV
            image1 = cv2.imdecode(img_array1, cv2.IMREAD_GRAYSCALE)
            image2 = cv2.imdecode(img_array2, cv2.IMREAD_GRAYSCALE)

            height1, width1 = image1.shape
            #print(f"Размеры файла [{firstpath}]: [{height1}]x[{width1}]")
            height2, width2 = image2.shape
            #print(f"Размеры файла [{secondpath}]: [{height2}]x[{width2}]")

            # Сравниваем казмеры картинок
            if height1 == height2 and width1 == width2:
                # Сравнение картинок
                score, diff = ssim(image1, image2, full=True)

                # Принятие решения
                if score < 0.8:
                    #print(f"Сходство меньше 80%: {score * 100:.2f}")
                    return photosPydantic(result=True,
                                         text="Нужно менять картинку",
                                         sameness=score * 100)
                else:
                    #print(f"Сходство больше 80%: {score * 100:.2f}")
                    return photosPydantic(result=False,
                                         text="Не нужно менять картинку",
                                         sameness=score * 100)
            else:
                return photosPydantic(result=False,
                                      text="Размеры картинок разные")
        else:
            return photosPydantic(result=False,
                                 text="Один из файлов не существует")
    except Exception:
        photosPydantic(result=False,
                       text=f"Ошибка: {Exception}")

# Ручка для замены старых картинок на новых
# Два входных аргумента:
#   Путь к первой папке
#   Путь к второй папке
@photos.get("/replacingimages",
            summary="Замена старых фотографий на новые",
            response_model=photosPydantic)
def replacing_images(firstpath, secondpath):
    # Получение всех папок
    print(f"Получение всех файлов в первой папке {len(os.listdir(firstpath))}")
    print(f"Получение всех файлов в второй папке {len(os.listdir(secondpath))}")

    if len(os.listdir(firstpath)) > len(os.listdir(secondpath)):
        list = zip(os.listdir(firstpath), os.listdir(secondpath))
        print("Разница 1-2:")
    else:
        list = zip(os.listdir(secondpath), os.listdir(firstpath))
        print("Разница 2-1:")

    path1cfolder = pathsfiles.main1cfolder
    pathsitefolder = pathsfiles.sitefolder

    #print(f"Получение всех файлов в первой папке по нужному пути{os.listdir(path1cfolder)[:-2]}")
    #print(f"Получение всех файлов в второй папке по нужному пути{os.listdir(pathsitefolder)}")

    for local, remote in tqdm(list):
        newfirstpath = firstpath + "/" + local
        newsecondpath = secondpath + "/" + remote
        comparison = picture_matching(newfirstpath, newsecondpath)
        if comparison.result == True:
            print(f"Файл [{newfirstpath}] совпадает с [{newsecondpath}] совпадает на: [{comparison.sameness}]")

    return photosPydantic(result=True)

