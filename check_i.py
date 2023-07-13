# ������ �������� ������������ ������ ������ �������� ����� ����������
# ��������� ��������������� ������� � ����� ������ (report.txt) � �������
import os
import re
import deobfuscator
import work_with_files
files = work_with_files.get_sv_files(os.curdir)
tables = []


def scan_tables(dir, svfiles):
    # dirfiles = []  # ��� ����� � ����� ����������
    dirpathes = []  # ��� ����� ����������

    # ������������ ������
    with os.scandir(dir) as files:
        for file in files:

            # ���������� ����� ��� ����� � ������
            # dirfiles.append(dir + "\\" + file.name)

            # ���������� ����� sv � ������
            if file.name.endswith("table.txt"):
                svfiles.append(dir + "\\" + file.name)

            # ���������� ������������(�����) � ������
            if file.is_dir():
                dirpathes.append(file.name)

    # ���� ������ �� ���� ������ � ������� ����������
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
