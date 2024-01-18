
from work_with_files import *

# ------------------------------��������_�������------------------------------ #
# �-� ����������� �������� ���� �� ���� ������� ���� � 1 �����
def deletecomments(patterns, plus = False):
    from erase_comments import json_struct
    # �������� ������������ �� ����� �������
    if json_struct["conf"]["allfiles"]:

        # ��������� ������ ����� � ������ sv
        svfiles = get_sv_files(os.curdir)

        # ���� �� ���� ������
        for sv in svfiles:

            # �������� ������������ �� �������� sv �����
            delete(sv, patterns, plus)

    # ���� ���������� ���������� ������ 1 ����
    else:

        # �������� ������������ �� ������� sv �����
        delete(json_struct["conf"]["filename"], patterns, plus)


# �������� ������������ �� ��������� ������ ��������
def delete(svfile, patterns, plus):

    svtext = get_file_text(svfile)  # ����� ���� sv

    # ���� �������� � plus �������
    if plus:
        comments = []  # ������ ���� ������������
        BasePatterns = ["/\*[\s|\S]*?\*/", "//[^\n]*\n"]

        # ����� ���� ������������
        for pattern in BasePatterns:
            comments.extend(re.findall(pattern, svtext))

        # ���� �� ������� �����������
        for com in comments:
            match = False  # ���� ���������� � ������������� ��������

            # ����� ����������
            for pluspattern in patterns:
                if(re.match(pluspattern, com)):
                    match = True

            # ���� ���������� ��� �� ������� �����������
            if not match:
               svtext = svtext.replace(com, '\n')

    # ���� �������� � minus �������
    else:
        # ���� ��������� �����������
        for pattern in patterns:
            if re.findall(pattern, svtext):

                # ������� �����������, ��������� � ��������
                svtext = re.sub(pattern, '\n', svtext)

    # ������� ������ �������
    svtext = delete_indents(svtext)

    # ������ � ���� ������ ���� ��� ������������
    write_text_to_file(svfile, svtext)




