# СКРИПТ РАБОТЫ С УДАЛЕНИЕМ КОММЕНТАРИЕВ
# настройка конфигурации осуществляется в "erase_comments.json"


from work_with_files import *
from erase_comments.base_funcs import *
# ------------------------------ЗАПУСК_УДАЛЕНИЯ------------------------------ #
json_struct = get_json_struct(r"jsons/erase_comments.json")

# ф-я запускающая удаление комментариев sv файлов
def launch():

    # удаление комментариев вида // и /**/
    if json_struct["tasks"]["BaseErase"]:
        BasePatterns = ["/\*[\s|\S]*?\*/", "//[^\n]*\n"]
        deletecomments(BasePatterns)

    # удаление комментариев без основных ascii символов
    if json_struct["tasks"]["NotAsciiErase"]:
        asciipatterns = ["/\*[ -~\n]*?\*/", "//[ -~]*\n"]
        deletecomments(asciipatterns, True)

    # удаление комментариев по minus списку
    if json_struct["tasks"]["MinusErase"]:
        deletecomments(json_struct["minus"])

    # удаление комментариев по plus списку
    if json_struct["tasks"]["PlusErase"]:
        deletecomments(json_struct["plus"], True)


