class SameNameException(Exception):
    """
    创建文件时同名异常
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "文件或目录名" + self.name + "已存在"


class NoEmptyPartException(Exception):
    """
    无空part异常
    """

    def __init__(self, block_index):
        self.block_index = block_index

    def __str__(self):
        return "第" + str(self.block_index) + "块磁盘块没有空白part"


class NoEmptyBlockException(Exception):
    """
    没有空块异常
    """

    def __str__(self):
        return "磁盘块已经全部被占用"


class EmptyBlockException(Exception):
    """
    指定块没有文件异常
    """

    def __init__(self, block_index):
        self.block_index = block_index

    def __str__(self):
        return "第" + str(self.block_index) + "块磁盘块没有文件或目录"


class DirectoryNotFoundException(Exception):
    """
    目录未找到异常
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "名字为" + self.name + "的目录未找到"


class NotADirectoryException(Exception):
    """
    指定的名字不是目录异常
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name + "不是一个目录"


class IllegalNameException(Exception):
    """
    命名非法
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "名字" + self.name + "非法"


class FileNotFoundException(Exception):
    """
    指定的名字文件不存在异常
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "文件" + self.name + "不存在"


class NotAOrdinaryFileException(Exception):
    """
    指定名字不是文件异常
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "名字" + self.name + "不是文件"


class ReadonlyFileModifiedException(Exception):
    """
    修改只读文件异常
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "文件" + self.name + "是只读文件"


class SystemFileModifiedException(Exception):
    """
    只读文件被删除异常
    """

    def __int__(self, name):
        self.name = name

    def __str__(self):
        return "文件" + self.name + "是系统文件"


class NotEnoughBlockToWriteException(Exception):
    """
    文件内容大于可存储空间异常
    """

    def __init__(self, need_block_count, unused_block_count):
        self.need_block_count = need_block_count
        self.unused_block_count = unused_block_count

    def __str__(self):
        return "文件占用的磁盘块数" + str(self.need_block_count) + "大于实际可用的磁盘块数" + str(self.unused_block_count)


class NoSuchPartObjectException(Exception):
    """
    没有该part对象
    """
    def __str__(self):
        return "没有该part对象"


class HasNotASCIICharException(Exception):
    """
    内容可能具有非ASCII字符
    """

    def __str__(self):
        return "内容可能具有非ASCII字符，拒绝保存"
