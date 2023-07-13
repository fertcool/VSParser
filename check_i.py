# скрипт проверки правильности работы чтения иерархии после обфускации
# переводит обфксцированные обьекты в файле отчета (report.txt) в обычные
import os
import re
import deobfuscator
import work_with_files
files = work_with_files.get_sv_files(os.curdir)
tables = []


def scan_tables(dir, svfiles):
    # dirfiles = []  # все файлы и папки директории
    dirpathes = []  # все папки директории

    # сканирование файлов
    with os.scandir(dir) as files:
        for file in files:

            # добавление файла или папки в список
            # dirfiles.append(dir + "\\" + file.name)

            # добавление файла sv в список
            if file.name.endswith("table.txt"):
                svfiles.append(dir + "\\" + file.name)

            # добавление подкаталогов(папок) с список
            if file.is_dir():
                dirpathes.append(file.name)

    # идем дальше по всем папкам в текущей дериктории
    for path in dirpathes:
        scan_tables(dir + "\\" + path, svfiles)


def launch():
    scan_tables(os.curdir, tables)
    for file in files:
        fileopen = open("report.txt", "r")
        filetext = fileopen.read()
        fileopen.close()

        if re.search(r"\$root", filetext):
            print(file)
    fileopen = open("report.txt", "r")
    filetext = fileopen.read()
    fileopen.close()


    for table in tables:
        table_struct = deobfuscator.get_decrt_in_file(table.replace("_decrypt_table.txt", ".sv"))

        for id in table_struct:

            filetext = re.sub(id, table_struct[id], filetext)

    fileopennew = open("new_report", "w")
    fileopennew.write(filetext)
