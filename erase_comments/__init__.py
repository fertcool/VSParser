# ������ ������ � ��������� ������������
# ��������� ������������ �������������� � "erase_comments.json"


from work_with_files import *
from erase_comments.base_funcs import *
# ------------------------------������_��������------------------------------ #
json_struct = get_json_struct(r"jsons/erase_comments.json")

# �-� ����������� �������� ������������ sv ������
def launch():

    # �������� ������������ ���� // � /**/
    if json_struct["tasks"]["BaseErase"]:
        BasePatterns = ["/\*[\s|\S]*?\*/", "//[^\n]*\n"]
        deletecomments(BasePatterns)

    # �������� ������������ ��� �������� ascii ��������
    if json_struct["tasks"]["NotAsciiErase"]:
        asciipatterns = ["/\*[ -~\n]*?\*/", "//[ -~]*\n"]
        deletecomments(asciipatterns, True)

    # �������� ������������ �� minus ������
    if json_struct["tasks"]["MinusErase"]:
        deletecomments(json_struct["minus"])

    # �������� ������������ �� plus ������
    if json_struct["tasks"]["PlusErase"]:
        deletecomments(json_struct["plus"], True)


