def string_to_int(string):
    # 把类似于00101000这样的字符串转换为int类型
    number = int(string, 2)

    return number


def int_to_string(number: int):
    if not (0 <= number <= 255):
        return None

    # 转换成二进制
    string = bin(number)

    # 去掉二进制前面的0b
    string = string[2:]

    # 补够8位
    while len(string) < 8:
        string = "0" + string

    return string


def string_list_to_content(string_list):
    # 将一个全为类似于00101010的字符串列表转换为字符串
    # 如果某个元素是全空格，则跳过

    content = ""
    for string in string_list:
        try:
            ch = chr(int(string, 2))
            content += ch
        except:
            continue

    return content


def empty_string():
    return "        "
