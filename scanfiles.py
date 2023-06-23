import os


# поиск всех sv файлов в директории и поддиректориях
def scan(dir, svfiles):
    # dirfiles = []  # все файлы и папки директории
    dirpathes = []  # все папки директории

    # сканирование файлов
    with os.scandir(dir) as files:
        for file in files:
            # добавление файла или папки в список
            # dirfiles.append(dir + "\\" + file.name)

            # добавление файла sv в список
            if file.name.endswith(".sv"):
                svfiles.append(dir + "\\" + file.name)
            # добавление подкаталогов(папок) с список
            if file.is_dir():
                dirpathes.append(file.name)
    # идем дальше по всем папкам в текущей дериктории
    for path in dirpathes:
        scan(dir + "\\" + path, svfiles)

# получить список sv файлов
def getsv(dir):
    svfiles = []  # список путей sv файлов
    scan(dir, svfiles)
    return svfiles
