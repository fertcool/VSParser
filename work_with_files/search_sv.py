import os

# ------------------------------ФУНКЦИИ_ПОИСКА_ФАЙЛОВ_SV------------------------------ #

# ф-я поиска всех sv файлов (путей у них) в директории и поддиректориях
def scan_svfiles(dir, svfiles):
    # dirfiles = []  # все файлы и папки директории
    dirpathes = []  # все папки директории

    # сканирование файлов
    with os.scandir(dir) as files:
        for file in files:

            # добавление файла sv в список
            if file.name.endswith(".sv"):
                svfiles.append(dir + "\\" + file.name)

            # добавление подкаталогов(папок) с список
            if file.is_dir():
                dirpathes.append(file.name)

    # идем дальше по всем папкам в текущей дериктории
    for path in dirpathes:
        scan_svfiles(dir + "\\" + path, svfiles)


# ф-я получить список sv файлов
def get_sv_files(dir):
    svfiles = []  # список путей sv файлов
    scan_svfiles(dir, svfiles)
    return svfiles
