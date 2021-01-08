
import StringParser
from FileExceptions import NoEmptyPartException, NoEmptyBlockException, EmptyBlockException, \
    DirectoryNotFoundException, NotADirectoryException, FileNotFoundException, NotAOrdinaryFileException, \
    SystemFileModifiedException, NotEnoughBlockToWriteException, HasNotASCIICharException
from DiskBlock import DiskBlock


class DiskBlocks:
    """
    使用此类直接创建整一块磁盘的对象，通过该对象执行所有操作。
    """

    # FAT磁盘块数
    __FAT_BLOCK_COUNT = 2

    # 总共的块数
    __TOTAL_BLOCK_COUNT = 128

    # 每个磁盘块的字节数
    __BYTE_PER_BLOCK = 64

    # 磁盘真实的文件名
    __DISK_FILE_NAME = "disk"

    def __init__(self):

        # 从文件中获取01字符串列表
        disk_list = self.__get_disk()

        # 获取磁盘块对象
        self.__blocks = self.__get_blocks(disk_list)

    def __getitem__(self, item):
        """
        使用下标直接获取block对象

        :param item: 磁盘块号
        :return: 返回对应磁盘块对象
        """

        return self.__blocks[item]

    def __get_disk(self):
        """
        加载file文件

        :return: 全盘的01字符串列表
        """

        try:

            # 尝试打开磁盘文件
            open(self.__DISK_FILE_NAME, "r")
        except FileNotFoundError:

            # 如果不存在则创建磁盘
            self.__new_disk()

        file_object = open(self.__DISK_FILE_NAME, "r")

        # 读取真实磁盘文件存为01字符串列表
        disk_list = file_object.readlines()

        # 去除\n
        disk_list = [one_byte[:-1] for one_byte in disk_list]

        file_object.close()

        return disk_list

    def __new_disk(self):
        """
        如果没有该磁盘文件，则创建一个磁盘文件

        :return: 无
        """

        disk_list = []

        # 初始化真实磁盘文件
        for index in range(DiskBlocks.__BYTE_PER_BLOCK * DiskBlocks.__TOTAL_BLOCK_COUNT):
            if index in range(DiskBlocks.__FAT_BLOCK_COUNT + 1):
                # 开始的两块磁盘块用于存储索引，再加一块用于根目录，这三块磁盘的FAT表内容都应该是-1，此处使用255代替
                # 真实磁盘文件1~3行

                disk_list.append(StringParser.int_to_string(255) + "\n")
                continue
            if index in range(
                    DiskBlocks.__FAT_BLOCK_COUNT + 1,
                    DiskBlocks.__BYTE_PER_BLOCK * DiskBlocks.__FAT_BLOCK_COUNT):
                # 剩下的全填0字符串，表示FAT表内容中的0
                # 真实磁盘文件4~128行

                disk_list.append(StringParser.int_to_string(0) + "\n")
                continue
            # print((index - DiskBlocks.__BYTE_PER_BLOCK * DiskBlocks.__FAT_BLOCK_COUNT) / 8)
            if (index - DiskBlocks.__BYTE_PER_BLOCK * DiskBlocks.__FAT_BLOCK_COUNT) / 8 in range(8):
                # 填$（需求要求）
                # 真实磁盘文件中的第129 137 145 153 161 169 177 185

                disk_list.append(StringParser.int_to_string(ord("$")) + "\n")
                continue
            disk_list.append(StringParser.empty_string() + "\n")

        with open(self.__DISK_FILE_NAME, "w") as file_object:
            file_object.writelines(disk_list)

    def write_disk(self):
        """
        当磁盘块被操作后需要手动调用此方法才能将新磁盘块内容保存到实际的文件disk中

        :return: 无
        """

        disk_list = []
        for block in self.__blocks:
            for part in block:
                disk_list += part.get_part_list()

        # print(len(disk_list))

        with open(self.__DISK_FILE_NAME, "w") as file_object:
            # 加'\n'在每个01字符串最后，并保存至文件
            file_object.writelines([(one_byte + "\n" if one_byte is not None else StringParser.empty_string())
                                    for one_byte in disk_list])

    @staticmethod
    def __get_blocks(disk_list):
        """
        将文件读取出来的disk_list列表转化为多个对象并保存

        :param disk_list: 全盘01字符串列表
        :return: 磁盘块对象列表
        """

        blocks = []

        # 复制一份disk_list用于切片
        temp_disk_list = disk_list[:]
        for index in range(DiskBlocks.__TOTAL_BLOCK_COUNT):
            block = DiskBlock(temp_disk_list[0:DiskBlocks.__BYTE_PER_BLOCK])
            temp_disk_list = temp_disk_list[DiskBlocks.__BYTE_PER_BLOCK:]

            blocks.append(block)

        return blocks

    def __get_fat_list(self):
        """
        获取FAT list（两个列表直接相接，通过索引找）

        :return: FAT list（01字符串列表）
        """
        fat_list = []

        for index in range(DiskBlocks.__FAT_BLOCK_COUNT):
            fat_list += self.__blocks[index].get_block_list()

        return fat_list

    def __set_fat_list(self, index, content):
        """
        设置fat

        :param index: FAT索引号
        :param content: FAT索引号对应内容（01字符串）
        :return: 无
        """

        # 先获取FAT表
        fat_list = self.__get_fat_list()

        # 修改FAT表
        fat_list[index] = content

        # 存回到block对象中
        for block_index in range(DiskBlocks.__FAT_BLOCK_COUNT):
            new_fat_list = fat_list[0:DiskBlocks.__BYTE_PER_BLOCK]
            fat_list = fat_list[DiskBlocks.__BYTE_PER_BLOCK:]

            self.__blocks[block_index].set_block_list(new_fat_list)

    def get_fat(self, index):
        """
        获取FAT中第index个元素的内容

        :param index: FAT索引号
        :return: FAT索引号对应的内容索引（int）
        """

        fat_list = self.__get_fat_list()

        return StringParser.string_to_int(fat_list[index])

    def __set_fat(self, index, next_index):
        """
        设置FAT中第index个元素的内容

        :param index: FAT索引号
        :param next_index: FAT索引号对应的新内容
        :return: 无
        """

        self.__set_fat_list(index, StringParser.int_to_string(next_index))

    def __find_empty_block(self):
        """
        寻找未被使用的磁盘块并返回索引号

        :return: 未被使用的磁盘块索引号
        """

        fat_list = self.__get_fat_list()

        index = 0
        for content in fat_list:
            if StringParser.string_to_int(content) == 0:
                return index

            index += 1

        return -1

    def create_dir(self, block_index, name):
        """
        在指定磁盘块下创建目录（不判断给定的磁盘块是否为目录）

        :param block_index: 在该磁盘块下创建目录
        :param name: 新目录名
        :exception NoEmptyPartException: 在该磁盘块下没有找到空的part
        :exception NoEmptyBlockException: 已经没有磁盘块用于分配给新的目录
        :exception SameNameException: 创建的目录与已有的目录或文件同名
        :exception IllegalNameException: 传入的新目录名不合法
        """

        # 获取空part的index
        empty_part_index = self.__blocks[block_index].find_empty_part()

        # 如果没有空part
        if empty_part_index == -1:
            raise NoEmptyPartException(block_index)

        # 找空块，如果没有则返回错误
        empty_block_index = self.__find_empty_block()
        if empty_block_index == -1:
            raise NoEmptyBlockException()

        # 交给part内的方法创建
        self.__blocks[block_index].create_dir(name, empty_block_index, empty_part_index)

        # 新块目录项写$
        self.__blocks[empty_block_index].init_dir_block()

        # 修改FAT
        self.__set_fat(empty_block_index, 255)

    def __recurse_delete_ordinary_file(self, begin_block_index):
        """
        递归删除普通文件

        :param begin_block_index: 文件开头的磁盘块索引号
        :return: 无
        """

        # 清空块
        self.__blocks[begin_block_index].clear()

        # 找下一个索引
        next_block_index = self.get_fat(begin_block_index)

        if next_block_index != 255:
            # 非-1即继续删除

            self.__recurse_delete_ordinary_file(next_block_index)

        # 重置为未使用状态
        self.__set_fat(begin_block_index, 0)

    def __recurse_delete_dir(self, begin_block_index):
        """
        递归删除文件

        :param begin_block_index: 目录的磁盘块索引号
        :return: 无
        """

        # 获取这个block
        block = self.__blocks[begin_block_index]

        for part in block:

            if part.is_empty():
                continue

            del_block_index = part.get_begin_block_index()

            if part.is_ordinary_file():
                # 如果是文件

                # 如果是系统文件
                if part.is_system_file():
                    raise SystemFileModifiedException(part.get_name())

                # 删除这个block的所有内容
                self.__recurse_delete_ordinary_file(del_block_index)

            if part.is_dir():
                # 如果是目录则递归该方法

                self.__recurse_delete_dir(del_block_index)

            # 清除part
            part.clear()

        # 删除自身
        self.__blocks[begin_block_index].clear()

        # 删除FAT
        self.__set_fat(begin_block_index, 0)

    def delete_dir(self, block_index, name):
        """
        在指定磁盘块下删除目录（不判断给定的磁盘块是否为目录）

        :param block_index: 删除该磁盘块下的目录
        :param name: 即将被删除的目录名
        :returns: 无返回值
        :exception EmptyBlockException: 指定磁盘块为空块
        :exception DirectoryNotFoundException: 未找到指定目录
        :exception NotADirectoryException: 指定的名字不是一个目录
        """

        if self.__blocks[block_index].is_empty():
            # 如果该块没有东西
            raise EmptyBlockException(block_index)

        # 取出这一个block
        block = self.__blocks[block_index]

        # 找出指定的name的目录是否存在
        has_dir = False
        part = None
        for one_part in block:
            if one_part.get_name() == name:
                has_dir = True
                part = one_part
                break

        if not has_dir:
            # 如果没有指定名字的目录

            raise DirectoryNotFoundException(name)

        if not part.is_dir():
            # 指定的名字不是一个目录

            raise NotADirectoryException(name)

        # 递归删除
        self.__recurse_delete_dir(part.get_begin_block_index())

        part.clear()

        # 目录项写$
        part.init_dir_part()

    def create_ordinary_file(self, block_index, name):
        """
        在指定磁盘块下新建文件（不判断给定的磁盘块是否为文件）

        :param block_index: 在该磁盘块下创建
        :param name: 新建文件名
        :return: 无返回值
        :exception NoEmptyPartException: 在该磁盘块下没有找到空的part
        :exception NoEmptyBlockException: 已经没有磁盘块用于分配给新的文件
        :exception SameNameException: 创建的文件名与已有的目录或文件同名
        :exception IllegalNameException: 传入的新文件名不合法
        """

        # 寻找这个磁盘块下面的空part
        empty_part_index = self.__blocks[block_index].find_empty_part()
        if empty_part_index == -1:
            raise NoEmptyPartException(block_index)

        # 寻找空块
        empty_block_index = self.__find_empty_block()
        if empty_block_index == -1:
            raise NoEmptyBlockException()

        # 创建普通文件
        self.__blocks[block_index].create_ordinary_file(name, empty_block_index, empty_part_index)

        # 设置FAT
        self.__set_fat(empty_block_index, 255)

    def delete_ordinary_file(self, block_index, name):
        """
        在指定磁盘块下删除文件（不判断给定的磁盘块是否为文件）

        :param block_index: 删除该磁盘块下的文件
        :param name: 即将被删除的文件名
        :returns: 无返回值
        :exception EmptyBlockException: 指定磁盘块为空块
        :exception FileNotFoundException: 未找到指定文件
        :exception NotADirectoryException: 指定的名字不是一个文件
        """

        if self.__blocks[block_index].is_empty():
            # 如果该块没有东西

            raise EmptyBlockException(block_index)

        # 取出这一个block
        block = self.__blocks[block_index]

        # 找出指定的name的目录是否存在
        has_ordinary_file = False
        part = None
        for one_part in block:
            if one_part.get_name() == name:
                has_ordinary_file = True
                part = one_part
                break

        if not has_ordinary_file:
            # 如果没有指定名字的文件

            raise FileNotFoundException(name)

        if not part.is_ordinary_file():
            # 指定的名字不是一个文件

            raise NotAOrdinaryFileException(name)

        # 递归删除
        self.__recurse_delete_ordinary_file(part.get_begin_block_index())

        # 清除自身的记录
        part.clear()

        # 目录项写$
        part.init_dir_part()

    def get_full_content(self, block_index):
        """
        获取文件完整内容（没有判断传入的磁盘块是文件还是目录）

        :param block_index: 文件开始磁盘号
        :return: 文件完整内容
        """

        content = ""

        # 通过FAT表查找文件内容
        temp_block_index = block_index
        while True:

            # 获取一个磁盘块的内容并追加到content字符串后面
            content += self.__blocks[temp_block_index].get_content()

            temp_block_index = self.get_fat(temp_block_index)

            # 已经是最后一个磁盘块索引
            if temp_block_index == 255:
                break

        return content

    def set_full_content(self, block_index, content):
        """
        设置文件完整内容（没有判断传入的磁盘块是文件还是目录）

        :param block_index: 文件开始磁盘号
        :param content: 文件完整内容
        :return: 文件占用磁盘块数
        """

        # 检查是否有中文字符
        for ch in content:
            if StringParser.int_to_string(ord(ch)) is None:
                raise HasNotASCIICharException()

        need_block_count = len(content) // self.__BYTE_PER_BLOCK \
            if len(content) % self.__BYTE_PER_BLOCK == 0 \
            else len(content) // self.__BYTE_PER_BLOCK + 1

        # 防止出现内容长度为0的情况
        if need_block_count == 0:
            need_block_count = 1

        # 计算出当前文件已经使用了的块
        used_block_count = 1
        temp_block_index = block_index
        while True:
            temp_block_index = self.get_fat(temp_block_index)

            if temp_block_index == 255:
                # 如果索引为-1则退出计算

                break

            used_block_count += 1
        # 计算出未被使用的块
        unused_block_count = 0
        for index in range(self.__TOTAL_BLOCK_COUNT):
            if self.get_fat(index) == 0:
                # 如果块为空，则统计

                unused_block_count += 1

        # 计算总可用空间
        available_block_count = used_block_count + unused_block_count

        # 如果实际需要的块数大于可用的块数
        if need_block_count > available_block_count:
            raise NotEnoughBlockToWriteException(need_block_count, unused_block_count)

        # 删除块内容
        self.__recurse_delete_ordinary_file(block_index)

        temp_content = content
        temp_block_index = block_index
        while True:

            # 获取前64字符
            one_block_content = temp_content[0:self.__BYTE_PER_BLOCK]
            temp_content = temp_content[self.__BYTE_PER_BLOCK:]

            # 设置这一个块的内容
            self.__blocks[temp_block_index].set_content(one_block_content)

            # 不管一个块是否足够存储，都先设置为-1防止找空块时找到这一块
            self.__set_fat(temp_block_index, 255)

            if len(temp_content) == 0:
                # 如果内容存储完毕

                break

            # 找空块，返回索引号
            new_block_index = self.__find_empty_block()

            # 存下一个块的索引
            self.__set_fat(temp_block_index, new_block_index)

            # 进行下一轮的存储
            temp_block_index = new_block_index

        return need_block_count
