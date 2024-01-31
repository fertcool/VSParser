import os

# ------------------------------�������_������_������_SV------------------------------ #

# �-� ������ ���� sv ������ (����� � ���) � ���������� � ��������������
def scan_svfiles(dir, svfiles):
    # dirfiles = []  # ��� ����� � ����� ����������
    dirpathes = []  # ��� ����� ����������

    # ������������ ������
    with os.scandir(dir) as files:
        for file in files:

            # ���������� ����� sv � ������
            if file.name.endswith(".sv"):
                svfiles.append(os.path.join(dir, file.name))

            # ���������� ������������(�����) � ������
            if file.is_dir():
                dirpathes.append(file.name)

    # ���� ������ �� ���� ������ � ������� ����������
    for path in dirpathes:
        scan_svfiles(os.path.join(dir, path), svfiles)


# �-� �������� ������ sv ������
def get_sv_files(dir):
    svfiles = []  # ������ ����� sv ������
    scan_svfiles(dir, svfiles)
    return svfiles
