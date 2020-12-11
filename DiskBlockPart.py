import StringParser


class DiskBlockPart:
    """
    所有的磁盘块，无论是不是用于存储目录信息，都被分成了8份，本类的对象则存储其中的一份。
    """

    def __init__(self, part_list):
        self.__name_list = part_list[0:3]
        self.__type_list = part_list[3:5]
        self.__properties = part_list[5]
        self.__begin_block_index = part_list[6]
        self.__length = part_list[7]

    def is_dir(self):
        """
        是否为目录

        :return: True/False
        """

        try:
            properties_dec = StringParser.string_to_int(self.__properties)
        except ValueError:
            return None

        if properties_dec & StringParser.string_to_int("00001000") != 0:
            return True
        return False

    def is_ordinary_file(self):
        """
        是否为普通文件

        :return: True/False
        """

        try:
            properties_dec = StringParser.string_to_int(self.__properties)
        except ValueError:
            return None

        if properties_dec & StringParser.string_to_int("00000100") != 0:
            return True
        return False

    def is_system_file(self):
        """
        是否为系统文件

        :return: True/False
        """

        try:
            properties_dec = StringParser.string_to_int(self.__properties)
        except ValueError:
            return None

        if properties_dec & StringParser.string_to_int("00000010") != 0:
            return True
        return False

    def get_name(self):
        """
        获取文件名或目录名

        :return: 文件或目录名
        """

        name = ""

        for name_ch in self.__name_list:

            # 如果name_ch是空则跳过
            if name_ch is None:
                continue

            # 是空串则跳过
            if name_ch == StringParser.empty_string():
                continue

            # 如果是全0或空字符串则跳过
            if StringParser.string_to_int(name_ch) == 0:
                continue

            try:
                name += chr(int(name_ch, 2))
            except ValueError:
                return None

        return name

    def is_empty(self):
        """
        part是否为空

        :return: True/False
        """

        # 如果全为空串，则为空
        if self.get_part_list() == [StringParser.empty_string()] * 8:
            return True

        # 如果part的第一个字符为$，则表示没有目录项
        # 此处由于coding时没有看清楚需求，现在在这里加上$的判断，事实上没有影响
        # print(self.get_part_list())
        # print([StringParser.int_to_string(ord("$"))] + ([StringParser.empty_string()] * 7))
        if self.get_part_list() == [StringParser.int_to_string(ord("$"))] + \
                ([StringParser.empty_string()] * 7):
            return True

        return False

    def get_part_list(self):
        """
        返回内容为01字符串的列表

        :return: 内容为01字符串的列表
        """

        part_list = []
        part_list += self.__name_list
        part_list += self.__type_list
        part_list.append(self.__properties)
        part_list.append(self.__begin_block_index)
        part_list.append(self.__length)

        return part_list

    def set_part_list(self, part_list):
        """
        设置part的所有内容

        :param part_list: 内容为01字符串的列表
        :return: 无
        """

        self.__name_list = part_list[0:3]
        self.__type_list = part_list[3:5]
        self.__properties = part_list[5]
        self.__begin_block_index = part_list[6]
        self.__length = part_list[7]

    def set_name(self, name):
        """
        设置文件或目录名字

        :param name: 新文件或目录名
        :return: True成功，False失败
        """

        try:
            if not (1 <= len(name) <= 3):
                return False
        except TypeError:
            return False

        name_list = []

        for index in range(3):
            try:
                # 部分情况下输入中文会产生None这种结果
                if StringParser.int_to_string(ord(name[index])) is None:
                    return False

                name_list.append(StringParser.int_to_string(ord(name[index])))
            except IndexError:
                name_list.append(StringParser.int_to_string(0))
            except Exception:
                return False

        self.__name_list = name_list
        return True

    def get_type(self):
        """
        获取类型，目录请勿使用

        :return: 类型的int值
        """

        type_list = self.__type_list

        type_string = ""
        for one_type in type_list:
            type_string += one_type

        return StringParser.string_to_int(type_string)

    def set_type(self, type_number, is_dir=False):
        """
        设置类型，目录请勿使用

        :param type_number: 新类型（int值）
        :param is_dir: 是否为目录
        :return: 无
        """

        if is_dir:
            self.__type_list = [StringParser.empty_string()] * 2
            return

        type_string = StringParser.int_to_string(type_number)

        # 如果不足16位则补足16位
        while len(type_string) < 16:
            type_string = "0" + type_string

        type_list = []
        for index in range(2):
            type_list.append(type_string[0:8])
            type_string = type_string[8:]

        self.__type_list = type_list

    def get_properties(self):
        """
        获取属性

        :return: 属性的int值
        """

        return StringParser.string_to_int(self.__properties)

    def set_properties(self, properties_number):
        """
        设置属性

        :param properties_number: 新属性的int值
        :return: 无
        """

        self.__properties = StringParser.int_to_string(properties_number)

    def init_properties(self, is_dir=False):
        """
        新建文件时用于初始化属性

        :param is_dir: 是否为目录
        :return: 无
        """

        if is_dir:
            # 目录属性

            self.__properties = "00001000"
            return

        self.__properties = "00000100"

    def get_begin_block_index(self):
        """
        获取起始盘块号的int值

        :return: 起始盘块号的int值
        """
        return StringParser.string_to_int(self.__begin_block_index)

    def set_begin_block_index(self, begin_block_index):
        """
        设置起始盘块号的int值

        :param begin_block_index: 起始盘块号的int值
        :return: 无
        """
        self.__begin_block_index = StringParser.int_to_string(begin_block_index)

    def get_length(self):
        """
        获得长度

        :return: 长度
        """
        return StringParser.string_to_int(self.__length)

    def set_length(self, length, is_dir=False):
        """
        设置长度

        :param length: 长度
        :param is_dir: 是否为目录
        :return: 无
        """
        if is_dir:
            self.__length = StringParser.int_to_string(0)
            return True

        self.__length = StringParser.int_to_string(length)
        return True

    def clear(self):
        """
        清空本part

        :return: 无
        """

        self.__name_list = [StringParser.empty_string()] * 3
        self.__type_list = [StringParser.empty_string()] * 2
        self.__properties = StringParser.empty_string()
        self.__begin_block_index = StringParser.empty_string()
        self.__length = StringParser.empty_string()

    def is_readonly(self):
        """
        是否为只读

        :return: True/False
        """

        if StringParser.string_to_int(self.__properties) & int("00000001", 2):
            return True

        return False

    def get_properties_string(self):
        """
        返回属性的中文

        :return: 以下之一（字符串）：文件夹，普通文件，系统文件
        """
        if self.is_dir():
            return "文件夹"
        if self.is_ordinary_file():
            return "普通文件"
        if self.is_system_file():
            return "系统文件"

    def get_permission_string(self):
        """
        获取权限的中文

        :return: 以下之一（字符串）：只读，""
        """
        if self.is_readonly():
            return "只读"

        return ""

    def init_dir_part(self):
        """
        设置每一个part的第一个字符为$，其它为空格字符串

        :return: 无
        """
        self.set_part_list([StringParser.int_to_string(ord("$"))] + ([StringParser.empty_string()] * 7))
