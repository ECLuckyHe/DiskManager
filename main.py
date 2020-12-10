import StringParser
from DiskWindow import DiskWindow
from FileExceptions import SameNameException
from DiskBlocks import DiskBlocks

disk_window = DiskWindow()


# def print_block():
#     index = 0
#     for block in disk:
#         print(str(index) + "." + str(block.get_block_list()))
#         index += 1

#
#
# disk.create_dir(2, "tst") #3
# disk.create_ordinary_file(3, "txt") #4
# disk.set_full_content(4, """
# There are moments in life when you miss someone so much that you just want to pick them from your dreams and hug them for real! Dream what you want to dream;go where you want to go;be what you want to be,because you have only one life and one chance to do all the things you want to do.
#
# May you have enough happiness to make you sweet,enough trials to make you strong,enough sorrow to keep you human,enough hope to make you happy? Always put yourself in others'shoes.If you feel that it hurts you,it probably hurts the other person, too.""")
#
# disk.create_dir(2, "ety")
# print_block()
# disk.write_disk()
#
# disk.create_dir(5, "def")
# disk.create_ordinary_file(5, "g")
# print(disk[5].get_exist_part_list()[0].get_begin_block_index())
#
# print(disk.get_full_content(4))
#
# disk.delete_ordinary_file(3, "txt")
# for part in disk[5].get_exist_part_list():
#     print(part.get_name())
#
# index = disk[2].get_exist_part_list()[0].get_begin_block_index()