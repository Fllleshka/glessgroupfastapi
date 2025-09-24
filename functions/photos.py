# Библиотека для работы с изображениями
from PIL import Image
# Библиотека для работы с файлами
import os
# Библиотека для работы с файлами 2
import shutil

# Функция получения размера изображения
def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

# Функция конвертации изображения (уменьшения веса и подгонка под заданные параметры)
def convertimage(path):
    # Размеры изображения на выходе
    width = 1920
    height = 1440
    # Загружаем фотографию в память
    img = Image.open(path)
    # Первоначальный размер картинки
    olddimensions = img.size
    # Получаем размер изображения до компрессии
    image_size = os.path.getsize(path)
    oldsize = get_size_format(image_size)
    # Преобразуем изображение приводя его к нужным высоте и ширине и уменьшая размер
    img.thumbnail(size=(width, height))
    if img.height > 1080:
        difference_height = (height - 1080) / 2
        img = img.crop((0, 0 + difference_height, 1920, height - difference_height))
    # Сохраняем изображение
    img.save(path, optimize=True, quality=95)
    # Получаем новые размеры картинки
    newdimesions = img.size
    # Получаем размер изображение после компрессии
    image_size = os.path.getsize(path)
    newsize = get_size_format(image_size)
    # Возвращаем данные
    return f"{path} с шириной, высотой: {olddimensions} и размером: {oldsize} была преобразована в: {newdimesions} и {newsize}"

# Функция загрузки фотографий по папкам
def renameanduploadimage(pathimage, folder):
    lenmailfolder = 62
    # Начинаем с переименования картинки
    numberfolderfirst = str(pathimage)[lenmailfolder:]
    # Если папка четырёхзначная
    if numberfolderfirst[4] == "/":
        numberfoldersecond = str(numberfolderfirst)[:4]
    elif numberfolderfirst[3] == "/":
        numberfoldersecond = str(numberfolderfirst)[:3]
    else:
        numberfoldersecond = str(numberfolderfirst)[:5]
    # Название картинки
    namepic = numberfoldersecond + str(pathimage)[-4:]
    # Новый путь к картинке
    convertname = str(pathimage)[
                  :lenmailfolder] + numberfoldersecond + "/" + namepic
    # Переименование картинки
    os.rename(pathimage, convertname.lower())
    # Начинаем загрузку фотографии по необходимому местоположению
    newpathfile = str(pathimage)[:29] + str(folder) + "/" + namepic.lower()
    shutil.move(convertname, newpathfile)