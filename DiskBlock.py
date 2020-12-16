from FileExceptions import SameNameException, IllegalNameException, NoSuchPartObjectException
from DiskBlockPart import DiskBlockPart
import StringParser


class DiskBlock:
    """
    此类的对象用于存储一个磁盘块的内容。
    """

    __BLOCK_PART_COUNT = 8
    __BYTE_PER_PART = 8

    def __init__(self, block_list):

        # 该block中的part，有八个对象
        self.__parts = self.__get_part_list(block_list)

    def __getitem__(self, item):
        """
        通过block对象和下标直接得到某一个part的对象

        :param item: 下标item
        :return: 返回parts的第item个对象
        """
        return self.__parts[item]

    @staticmethod
    def __get_part_list(block_list):
        """
        将磁盘块分part存储

        :param block_list: 内容为01字符串的磁盘块内容
        :return: part对象列表
        """

        temp_block_list = block_list[:]
        part_list = []
        for index in range(DiskBlock.__BLOCK_PART_COUNT):
            block_part = temp_block_list[0:DiskBlock.__BLOCK_PART_COUNT]
            temp_block_list = temp_block_list[DiskBlock.__BLOCK_PART_COUNT:]
            part_list.append(DiskBlockPart(block_part))

        return part_list

    def get_content(self):
        """
        获取磁盘块的文本内容

        :return: 磁盘块的文本内容共
        """

        content = ""

        for one_part in self.__parts:
            part_list = one_part.get_part_list()
            content += StringParser.string_list_to_content(part_list)

        return content

    def set_content(self, content):
        """
        写磁盘块文本内容

        :param content: 写入的内容
        :return: 无
        """

        for index in range(self.__BYTE_PER_PART):
            # 对每个part操作

            # 分割成每个part的长度并存入
            part_content = content[0:self.__BYTE_PER_PART]
            content = content[self.__BYTE_PER_PART:]

            new_part_list = []
            while len(part_content) != 0:
                # 获取一个字符
                ch = part_content[0]
                part_content = part_content[1:]

                # 转换为01字符串存到表中
                new_part_list.append(StringParser.int_to_string(ord(ch)))

            while len(new_part_list) < self.__BYTE_PER_PART:
                # 如果列表长度不够，则补空字符串

                new_part_list.append(StringParser.empty_string())

            # 设置part
            self.__parts[index].set_part_list(new_part_list)

    def is_empty(self):
        """
        磁盘块是否为空

        :return: True/False
        """
        is_empty = True

        for block_part in self.__parts:
            if not block_part.is_empty():
                is_empty = False
                break

        return is_empty

    def get_block_list(self):
        """
        获取内容为01字符串的磁盘块列表

        :return: 内容为01字符串的列表
        """

        block_list = []

        for one_part in self.__parts:
            part_list = one_part.get_part_list()
            block_list += part_list

        return block_list

    def set_block_list(self, block_list):
        """
        设置磁盘块内容

        :param block_list: 内容为01字符串的列表
        :return: 无
        """

        # 拆分为八份part列表
        for index in range(DiskBlock.__BLOCK_PART_COUNT):
            # 每八个元素组成一个part列表
            new_part_list = block_list[0:DiskBlock.__BYTE_PER_PART]
            block_list = block_list[DiskBlock.__BYTE_PER_PART:]

            self.__parts[index].set_part_list(new_part_list)

    def find_empty_part(self):
        """
        查看是否有空part可以创建文件夹或者文件

        :return: 空part的下标
        """

        index = 0
        for part in self.__parts:
            if part.is_empty():
                return index

            index += 1

        return -1

    def create_dir(self, name, begin_block_index, empty_part_index):
        """
        在指定的part[index]中创建目录

        :param name: 目录名
        :param begin_block_index: 目录磁盘块起始号
        :param empty_part_index: 空part下标
        :return: 无
        """

        part_object = self.__parts[empty_part_index]

        for part in self.__parts:
            if (not part.is_empty()) and part.get_name() == name:
                raise SameNameException(name)

        if not part_object.set_name(name):
            raise IllegalNameException(name)

        part_object.set_type("0", is_dir=True)
        part_object.init_properties(is_dir=True)
        part_object.set_begin_block_index(begin_block_index)
        part_object.set_length(0, is_dir=True)

    def get_exist_part_list(self):
        """
        获取非空的part列表（存在内容的part）

        :return: 非空的part列表
        """

        part_list = []

        for part in self.__parts:
            if not part.is_empty():
                part_list.append(part)

        return part_list

    def clear(self):
        """
        清空块

        :return: 无
        """

        for part in self.__parts:
            part.clear()

    def create_ordinary_file(self, name, begin_block_index, empty_part_index):
        """
        创建普通文件

        :param name: 文件名
        :param begin_block_index: 文件起始磁盘块号
        :param empty_part_index: 空part下标
        :return: 无
        """

        part_object = self.__parts[empty_part_index]

        # 如果有同名文件则抛出异常
        for part in self.__parts:
            if (not part.is_empty()) and part.get_name() == name:
                raise SameNameException(name)

        # 设置名字失败
        if not part_object.set_name(name):
            raise IllegalNameException(name)

        part_object.set_type(0, is_dir=False)
        part_object.init_properties(is_dir=False)
        part_object.set_begin_block_index(begin_block_index)
        part_object.set_length(1, is_dir=False)

    def init_dir_block(self):
        """
        初始化目录块，即每个目录项第一个字节写$

        :return: 无
        """
        for part in self.__parts:
            part.init_dir_part()

    def get_part_object_by_name(self, name):
        """
        通过名字查找并返回part对象

        :param name: 文件名
        :return: part对象
        """

        for part in self.__parts:
            if name == part.get_name():
                return part

        raise NoSuchPartObjectException()

    def get_part_object_by_begin_block_index(self, begin_block_index):
        """
        通过begin_block_index查找并返回part对象

        :param begin_block_index: 通过开始盘块号找到part对象
        :return: 无
        """
        for part in self.__parts:
            if begin_block_index is not None and \
                    begin_block_index == part.get_begin_block_index():
                return part

        raise NoSuchPartObjectException()
