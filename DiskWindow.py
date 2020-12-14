from tkinter import *
from tkinter.ttk import *

import FileExceptions
import StringParser
from DiskBlocks import DiskBlocks


class DiskWindow:
    # 最大可打开编辑窗口数
    __MAX_EDITOR_WINDOW_COUNT = 5

    def __init__(self):

        # 磁盘对象
        self.disk = DiskBlocks()

        # 当前编辑窗口数
        self.current_editor_window_count = 0

        # 当前盘块号
        self.current_disk_block = 2

        # 磁盘栈，用于存储跳转前后的磁盘盘块号
        self.block_stack = []

        # root结点
        self.root = Tk()
        self.root.title("磁盘调度管理系统")

        # 居中显示root结点
        self.root.geometry("{}x{}+{}+{}".format(
            800,
            600,
            int(self.root.winfo_screenwidth() / 2 - 800 / 2),
            int(self.root.winfo_screenheight() / 2 - 600 / 2)
        ))
        self.root.minsize(800, 600)

        # 导航栏和文件操作窗口
        self.frame_manager = Frame(self.root)
        self.frame_manager.pack(side=TOP, fill=BOTH, expand=True)

        # 导航栏frame
        self.frame_guide = Frame(self.frame_manager)
        self.frame_guide.pack(side=TOP, fill='x', anchor="n")

        # 后退按钮
        self.btn_back = Button(self.frame_guide, text="后退", command=self.__back)
        self.btn_back.pack(side=LEFT, fill="y", padx=5, pady=5)

        # 路径栏
        self.entry_path = Entry(self.frame_guide)
        self.entry_path.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.entry_path.bind("<Return>", lambda event: self.__go(self.entry_path.get()))

        # 前往按钮
        self.btn_go = Button(self.frame_guide, text="前往", command=lambda: self.__go(self.entry_path.get()))
        self.btn_go.pack(side=LEFT, fill="y", padx=5, pady=5)

        # 文件操作部分分为了左边的文件树，中间的文件列表和右边的FAT，所以需要一个容易装这两个
        self.frame_op = Frame(self.frame_manager)
        self.frame_op.pack(side=TOP, fill=BOTH, expand=True)

        # 文件树frame
        self.frame_tree = Frame(self.frame_op)
        self.frame_tree.pack(side=LEFT, fill='y')

        # 文件树
        self.treeview_tree = Treeview(
            self.frame_tree,
            columns=["BlockIndex"],
            show="tree",
            selectmode=BROWSE
        )
        self.treeview_tree.column("BlockIndex", width=30)
        self.treeview_tree.pack(side=LEFT, fill=BOTH)
        self.treeview_tree.bind("<Double-Button-1>", lambda event: self.__tree_go())

        # 文件树滚动条
        self.scrollbar_tree = Scrollbar(self.frame_tree)
        self.scrollbar_tree.pack(fill='y', expand=True)
        self.treeview_tree.config(yscrollcommand=self.scrollbar_tree.set)
        self.scrollbar_tree.config(command=self.treeview_tree.yview)

        # 文件列表
        self.treeview_file_list = Treeview(
            self.frame_op,
            columns=["Name", "Properties", "Permission", "Length", "BeginBlockIndex"],
            show="headings",
            selectmode=BROWSE
        )
        self.treeview_file_list.pack()
        self.treeview_file_list.pack(side=LEFT, fill=BOTH, expand=True)
        self.treeview_file_list.column("Name", width=50)
        self.treeview_file_list.column("Properties", width=50)
        self.treeview_file_list.column("Permission", width=50)
        self.treeview_file_list.column("Length", width=30)
        self.treeview_file_list.column("BeginBlockIndex", width=0)
        self.treeview_file_list.heading("Name", text="名称")
        self.treeview_file_list.heading("Properties", text="属性")
        self.treeview_file_list.heading("Permission", text="权限")
        self.treeview_file_list.heading("Length", text="文件长度")
        self.treeview_file_list.heading("BeginBlockIndex", text="起始盘")

        # 创建frame fat
        self.frame_fat = Frame(self.frame_op)
        self.frame_fat.pack(side=LEFT, fill='y')

        # 显示索引表
        self.treeview_fat = Treeview(
            self.frame_fat,
            columns=["BlockIndex", "Content"],
            show="headings",
            selectmode=BROWSE
        )
        self.treeview_fat.pack(side=LEFT, fill=BOTH)
        self.treeview_fat.column("BlockIndex", width=30)
        self.treeview_fat.column("Content", width=60)
        self.treeview_fat.heading("BlockIndex", text="盘")
        self.treeview_fat.heading("Content", text="FAT内容")
        self.treeview_fat.bind("<Double-Button-1>", lambda event: self.__open_fat())

        # 设置fat滚动条
        self.scrollbar_fat = Scrollbar(self.frame_fat)
        self.scrollbar_fat.pack(fill="y", expand=True)
        self.treeview_fat.config(yscrollcommand=self.scrollbar_fat.set)
        self.scrollbar_fat.config(command=self.treeview_fat.yview)

        # 右键菜单
        self.treeview_file_list.bind("<Button-3>", self.__show_pop_up_menu)

        # 删除键
        self.treeview_file_list.bind("<Delete>", lambda event: self.__delete())

        # 退格键回到上一级目录
        self.treeview_file_list.bind("<BackSpace>", lambda event: self.__back())

        # 回车进入目录
        self.treeview_file_list.bind("<Return>", lambda event: self.__open())

        # 左键双击菜单
        self.treeview_file_list.bind("<Double-Button-1>", lambda event: self.__open())

        # 用于显示磁盘中的内容
        self.block_hex_list = []

        # 刷新
        self.__refresh_all()

        # 显示窗口
        self.root.mainloop()

    def __show_pop_up_menu(self, event):
        """
        在文件列表显示右键菜单

        :param event: 事件
        :return: 无
        """

        # 右键菜单
        menu_pop_up = Menu(self.treeview_file_list, tearoff=False)
        menu_pop_up.add_command(label="新建文件夹", command=self.__create_dir)
        menu_pop_up.add_command(label="新建文件", command=self.__create_file)

        # 获取part对象
        part_object = self.__get_file_list_selected_part_object()

        # 选定了文件或目录后的菜单
        if part_object is not None:
            if not part_object.is_dir():
                # 如果是文件，可以修改属性
                menu_pop_up.add_command(label="修改属性", command=self.__modify_properties)
            menu_pop_up.add_command(label="重命名", command=self.__rename)
            menu_pop_up.add_command(label="删除", command=self.__delete)

        menu_pop_up.post(event.x_root, event.y_root)

    def __refresh_all(self):
        """
        刷新文件列表

        :return: 无
        """

        def recursive_get_tree(tree_str, block_index):
            # 递归获取目录树

            # 如果是2则指向根目录，因为下面的代码中不会选择根目录
            if block_index == 2:
                self.treeview_tree.selection_set(tree_str)

            # 模拟用户打开文件夹遍历
            for part in self.disk[block_index].get_exist_part_list():
                if part.is_dir():

                    # 先插入该目录
                    new_tree_str = self.treeview_tree.insert(
                        tree_str,
                        END,
                        text=part.get_name(),
                        open=True,
                        values=(part.get_begin_block_index())
                    )

                    # 如果当前目录就是这个目录，选择它
                    if part.get_begin_block_index() == self.current_disk_block:
                        self.treeview_tree.selection_set(new_tree_str)

                    # 目录下面如果有目录，则插入为子结点
                    if self.disk[part.get_begin_block_index()].get_exist_part_list():
                        recursive_get_tree(new_tree_str, part.get_begin_block_index())

        def refresh_fat():
            # 刷新FAT

            self.treeview_fat.delete(*self.treeview_fat.get_children())

            # 插入FAT
            for index in range(0, 128):
                new_fat = self.treeview_fat.insert("", END, values=[index, self.disk.get_fat(index)])

                # 如果是当前盘块号，则选定fat中的这一项
                if index == self.current_disk_block:
                    self.treeview_fat.selection_set(new_fat)

        def refresh_file_list():
            # 刷新file list

            # 删除文件显示列表中的所有内容
            self.treeview_file_list.delete(*self.treeview_file_list.get_children())

            # 获取存在的part，并添加到显示列表中
            part_list = self.disk[self.current_disk_block].get_exist_part_list()
            for part_object in part_list:
                self.treeview_file_list.insert("", index=END, values=(
                    part_object.get_name(),
                    part_object.get_properties_string(),
                    part_object.get_permission_string(),
                    part_object.get_length() if not part_object.is_dir() else "",
                    part_object.get_begin_block_index()
                ))

        def refresh_path():
            # 刷新路径显示

            # 获取路径

            path = self.__get_current_path()

            # 删除文本框内容
            self.entry_path.delete(0, END)

            # 将路径插入到文本框
            self.entry_path.insert(END, path)

        def refresh_tree():
            # 刷新目录树

            # 清空目录树
            self.treeview_tree.delete(*self.treeview_tree.get_children())

            # 递归获取目录树
            tree_root = self.treeview_tree.insert("", END, text="ROOT", open=True, values=(2))
            recursive_get_tree(tree_root, 2)

        def refresh_block_hex_list():
            # 刷新label block list
            # 以16进制显示盘中内容

            self.block_hex_list.clear()

            # 行号计数器
            line_counter = 1

            for index in range(128):

                # 获取block list
                block_list = self.disk[index].get_block_list()

                output_string = "FBLN  B0 C0  B1 C1  B2 C2  B3 C3  B4 C4  B5 C5  B6 C6  B7 C7\n"
                output_string += "------------------------------------------------------------\n"

                for _index in range(64):

                    if line_counter % 8 == 1:
                        output_string += str(line_counter).zfill(4) + "  "

                    if block_list[_index] == StringParser.empty_string():
                        # 空字符串直接显示空

                        output_string += "       "
                    else:
                        # 转换为十六进制
                        hex_str = str(hex(StringParser.string_to_int(block_list[_index])))[2:]

                        # 不足两位补足两位
                        if len(hex_str) == 1:
                            hex_str = "0" + hex_str

                        # 十六进制大写
                        hex_str = hex_str.upper()

                        # ASCII对应字符
                        ch = chr(StringParser.string_to_int(block_list[_index]))

                        # 处理一些特殊字符
                        if ch == "\0":
                            ch = "\\0"
                        elif ch == "\n":
                            ch = "\\n"
                        elif ch == "\t":
                            ch = "\\t"
                        else:
                            ch = " " + ch

                        output_string += hex_str + " " + ch + "  "

                    # 每8个换一行
                    if _index % 8 == 7:
                        output_string = output_string[:-2]
                        output_string += "\n"

                    line_counter += 1

                # 添加介绍信息
                output_string += "\nFBLN: First Byte Line Number in disk file"
                output_string += "\nB*: *th Hex Byte"
                output_string += "\nC*: *th Char by ASCII"

                # 添加到内容中
                self.block_hex_list.append(output_string)

        refresh_file_list()

        refresh_path()

        refresh_tree()

        refresh_fat()

        refresh_block_hex_list()

    def __get_current_path(self):
        """
        获取当前路径字符串

        :return: 路径字符串
        """

        # 用户所在目录使用的是stack表示，每当进入一个文件夹时，就push当前盘块号到stack中，并修改当前盘块号
        # 获取path的思路是从栈底开始（盘块号为2开始）寻找直到找到当前目录
        # 为了方便，下面反转了栈方便使用pop()

        path = "/"

        # 复制栈
        stack = self.block_stack[:]
        # 反转栈，方便出栈
        stack.reverse()

        while stack:
            block_index = stack.pop()

            # 获取该part对象

            # 如果栈中还有内容，则取栈顶
            # 否则传入当前盘块号
            try:
                part_object = self.disk[block_index].get_part_object_by_begin_block_index(stack[-1])
            except IndexError:
                part_object = self.disk[block_index].get_part_object_by_begin_block_index(self.current_disk_block)

            dir_name = part_object.get_name()

            path += dir_name + "/"

        return path

    def __create_dir(self):
        """
        新建文件夹

        :return: 无
        """

        self.__toplevel_create_window("新建文件夹", "dir")

    def __create_file(self):
        """
        新建文件

        :return: 无
        """

        self.__toplevel_create_window("新建文件", "file")

    def __toplevel_create_window(self, title, file_type):
        """
        新建窗口处理

        :param title: 窗口标题
        :return: 新建文件名
        """

        def on_btn_ok():
            # 按钮确认事件

            # 获取新建文件名称
            file_name = entry_file_name.get()

            print(file_name)

            # 有禁止字符的禁止保存
            for ch in file_name:
                if ch in ["$", ".", "/"]:
                    self.__message_box("错误", "不能包含非法字符：$ . /")
                    return

            try:
                if file_type == "file":
                    # 如果创建的是文件

                    self.disk.create_ordinary_file(self.current_disk_block, file_name)
                if file_type == "dir":
                    # 如果创建的是目录

                    self.disk.create_dir(self.current_disk_block, file_name)
            except Exception as e:

                # NoEmptyPartException的异常信息是给开发者看的，但此处是需要显示给用户
                # 所以需要转换为用户可以理解的句子
                if isinstance(e, FileExceptions.NoEmptyPartException):
                    error_str = "该目录下已不可再创建更多文件"
                else:
                    # 异常信息本身
                    error_str = str(e)

                # 弹出错误
                self.__message_box("错误", error_str)

                # 跳出事件
                return

            # 此处排除中文，由于中文问题目前无法解决
            try:
                self.__refresh_all()
            except TypeError:
                self.__message_box("错误", "类型错误，可能存在非ASCII字符")
                return
            toplevel_window.destroy()

            # 写盘
            self.disk.write_disk()

        toplevel_window, entry_file_name = \
            self.__show_name_input_box(title, "输入新建名称：", on_btn_ok, lambda: toplevel_window.destroy())

    def __show_name_input_box(self, title, message, on_btn_ok, on_btn_cancel):
        """
        显示命名框

        :param title: 标题
        :param on_btn_ok: 点击确定事件
        :param on_btn_cancel: 点击取消事件
        :return: 无
        """

        # 对话框
        toplevel_window = Toplevel()

        # 设置对话框不可调整大小
        toplevel_window.resizable(False, False)
        toplevel_window.geometry("{}x{}+{}+{}".format(
            300,
            100,
            int(self.root.winfo_x() + (self.root.winfo_width() / 2 - 300 / 2)),
            int(self.root.winfo_y() + (self.root.winfo_height() / 2 - 100 / 2))
        ))
        toplevel_window.grab_set()
        toplevel_window.focus_set()

        # 设置标题
        toplevel_window.title(title)

        # 设置提示标签
        Label(toplevel_window, text=message, justify=LEFT).pack(anchor="nw", padx=5, pady=5)

        # 设置文本框
        entry_file_name = Entry(toplevel_window)
        entry_file_name.pack(anchor="n", fill="x", expand=True, padx=5)
        entry_file_name.bind("<Return>", lambda event: on_btn_ok())
        entry_file_name.focus_set()

        # 设置确认按钮
        btn_ok = Button(toplevel_window, text="确定", command=on_btn_ok)
        btn_ok.pack(side=LEFT, padx=30, pady=10)

        # 设置取消按钮
        btn_cancel = Button(toplevel_window, text="取消", command=on_btn_cancel)
        btn_cancel.pack(side=RIGHT, padx=30, pady=10)

        return toplevel_window, entry_file_name

    def __get_file_list_selected_part_object(self):
        """
        获取选定的part对象

        :return: part对象
        """
        part_object = None

        for item in self.treeview_file_list.selection():
            # 获取文件名
            file_name = self.treeview_file_list.item(item, "values")[0]

            # 通过文件夹名找到part对象
            part_object = self.disk[self.current_disk_block].get_part_object_by_name(file_name)

        return part_object

    def __tree_go(self):
        """
        文件树中点击文件夹进入

        :return: 无
        """

        dest_block_index = None

        for item in self.treeview_tree.selection():
            # 获取盘块号
            dest_block_index = self.treeview_tree.item(item, "values")[0]

            # 如果为空则不进入
            if dest_block_index is None:
                return

            # 新栈
            stack = []

            # 找父节点直至到根目录
            while True:
                item = self.treeview_tree.parent(item)
                if item == "":
                    break
                stack.append(int(self.treeview_tree.item(item, "values")[0]))

            # 反转，否则不是栈
            stack.reverse()

            # 修改当前盘块号并压栈
            self.block_stack = stack
            self.current_disk_block = int(dest_block_index)

            # 刷新
            self.__refresh_all()

    def __open(self):
        """
        打开文件或目录

        :return: 无
        """

        part_object = self.__get_file_list_selected_part_object()

        try:
            # 不同文件不同打开方法

            if part_object.is_dir():
                self.__open_dir(part_object)
            if part_object.is_ordinary_file():
                self.__open_file(part_object)
            if part_object.is_system_file():
                self.__message_box("提示", "系统文件" + part_object.get_name() + "禁止访问")
                return
        except AttributeError:
            return

    def __open_dir(self, part_object):
        """
        打开目录

        :return: 无
        """

        # 入栈
        self.block_stack.append(self.current_disk_block)

        # 修改当前盘块号
        # 处理异常为了防止因为双击其它地方而抛出异常
        try:
            self.current_disk_block = part_object.get_begin_block_index()
        except AttributeError:
            return

        # 刷新
        self.__refresh_all()

    def __open_file(self, part_object):
        """
        打开文件

        :param part_object: part对象
        :return: 无
        """

        def on_exit():
            # 点击退出时事件

            # 如果文本框中的内容与磁盘中的一致则直接退出
            if text_content.get(1.0, END)[:-1] == self.disk.get_full_content(part_object.get_begin_block_index()):
                toplevel_file_editor.destroy()
                # 编辑窗口数-1
                self.current_editor_window_count -= 1
                return

            toplevel_yes_no = self.__show_yes_no_box(
                "提示",
                "是否保存文件" + part_object.get_name() + "？",
                lambda: on_btn_yes(toplevel_yes_no),
                lambda: on_btn_no(toplevel_yes_no)
            )

        def on_btn_yes(toplevel_save_confirm):
            # 退出时是否保存选是事件

            save_file()
            toplevel_save_confirm.destroy()
            toplevel_file_editor.destroy()

            # 编辑窗口数-1
            self.current_editor_window_count -= 1

        def on_btn_no(toplevel_save_confirm):
            # 退出时是否保存选否事件

            toplevel_save_confirm.destroy()
            toplevel_file_editor.destroy()

            # 编辑窗口数-1
            self.current_editor_window_count -= 1

        def save_file():
            # 保存文件

            # 系统文件或者只读文件拒绝保存
            if part_object.is_system_file() or part_object.is_readonly():
                self.__message_box("错误", "该文件内容不可被修改")
                return

            # 异常
            try:
                length = self.disk.set_full_content(part_object.get_begin_block_index(),
                                                    text_content.get(1.0, END)[:-1])
            except Exception as e:
                self.__message_box("错误", str(e))
                return

            # 存储长度
            part_object.set_length(length)

            # 写盘
            self.disk.write_disk()

            # 刷新
            self.__refresh_all()

            # 弹出提示
            self.__message_box("提示", part_object.get_name() + "保存完成，共占用" + str(length) + "个磁盘块")

        # 查看编辑窗口数是否已满
        if self.current_editor_window_count == self.__MAX_EDITOR_WINDOW_COUNT:
            self.__message_box("提示", "最多只能打开5个编辑器")
            return

        # 设置窗口
        toplevel_file_editor = Toplevel()
        toplevel_file_editor.title("文件编辑器：" + self.__get_current_path() + part_object.get_name())
        toplevel_file_editor.geometry("{}x{}+{}+{}".format(
            650,
            350,
            int(self.root.winfo_x() + (self.root.winfo_width() / 2 - 650 / 2)),
            int(self.root.winfo_y() + (self.root.winfo_height() / 2 - 350 / 2))
        ))
        toplevel_file_editor.minsize(650, 350)
        toplevel_file_editor.focus_set()
        toplevel_file_editor.resizable(True, True)

        # 设置文本编辑部份
        frame_editor = Frame(toplevel_file_editor)
        frame_editor.pack(side=TOP, fill=BOTH, expand=True)

        # 设置多行文本框
        text_content = Text(frame_editor)
        text_content.focus_set()
        text_content.pack(anchor="center", side=LEFT, fill=BOTH, expand=True)

        # 设置滚动条
        scrollbar_text = Scrollbar(frame_editor)
        scrollbar_text.pack(fill="y", side=RIGHT)
        text_content.config(yscrollcommand=scrollbar_text.set)
        scrollbar_text.config(command=text_content.yview)

        # 设置状态栏
        label_status = Label(toplevel_file_editor)
        label_status.pack(anchor="s", side=TOP, fill="x")

        # 设置菜单栏
        menu_bar = Menu(toplevel_file_editor, tearoff=False)
        menu_file = Menu(menu_bar, tearoff=False)
        menu_file.add_command(label="保存", command=save_file)
        menu_bar.add_cascade(label="文件", menu=menu_file)
        toplevel_file_editor.config(menu=menu_bar)

        # 保存快捷键
        toplevel_file_editor.bind("<Control-KeyPress-s>", lambda event: save_file())

        # 关闭事件
        toplevel_file_editor.protocol("WM_DELETE_WINDOW", on_exit)

        # 设置文本框内容
        text_content.insert(END, self.disk.get_full_content(part_object.get_begin_block_index()))

        # 初始化状态栏
        label_status.config(text="长度：" + str(len(text_content.get(1.0, END)) - 1))

        # 随时更新状态栏
        toplevel_file_editor.bind("<KeyPress>", lambda event: label_status.config(
            text="长度：" + str(len(text_content.get(1.0, END)) - 1)
        ))

        # 编辑窗口打开数字加1
        self.current_editor_window_count += 1

    def __back(self):
        """
        返回上一级目录

        :return: 无
        """
        if self.current_disk_block != 2:
            # 根目录不能再后退

            # 出栈盘块号
            block_index = self.block_stack.pop()

            # 设置当前盘块号
            self.current_disk_block = block_index

            # 刷新列表显示
            self.__refresh_all()

    def __message_box(self, title, message):
        """
        弹出信息框

        :param title: 信息框标题
        :param message: 信息框内容
        :return: 无
        """

        # 设置信息框
        toplevel_message_window = Toplevel()
        toplevel_message_window.resizable(False, False)
        toplevel_message_window.geometry("{}x{}+{}+{}".format(
            400,
            100,
            int(self.root.winfo_x() + (self.root.winfo_width() / 2 - 400 / 2)),
            int(self.root.winfo_y() + (self.root.winfo_height() / 2 - 100 / 2))
        ))
        toplevel_message_window.title(title)
        toplevel_message_window.grab_set()
        toplevel_message_window.focus_set()

        # 设置信息内容
        Label(toplevel_message_window, text="\n" + message).pack(anchor="n", padx=10, pady=10)
        btn_error_ok = Button(toplevel_message_window, text="确定", command=lambda: toplevel_message_window.destroy())
        btn_error_ok.pack(anchor="s", pady=5)
        btn_error_ok.focus_set()
        btn_error_ok.bind("<Return>", lambda event: toplevel_message_window.destroy())

        # 下面是另一种显示错误信息的方法，但此处有些问题，故不使用
        # messagebox.showinfo(title="错误", message=error)

    def __go(self, path):
        """
        前往路径

        :param path: 指定路径
        :return: 无
        """

        # 分割路径
        split_path = path.split("/")

        # 模拟用户打开文件夹的过程寻找
        current_block_index = 2
        block_stack = []

        for dir_name in split_path:

            # 跳过空格
            if dir_name == "":
                continue

            block = self.disk[current_block_index]

            # 尝试查找，如果抛出异常则显示错误信息
            try:
                part_object = block.get_part_object_by_name(dir_name)
            except Exception:
                self.__message_box("错误", "没有该路径")
                return

            # 如果不是目录则拒绝进入
            if not part_object.is_dir():
                self.__message_box("错误", "没有该路径")
                return

            block_stack.append(current_block_index)
            current_block_index = part_object.get_begin_block_index()

        # 保存给实际的当前盘块号和栈
        self.current_disk_block = current_block_index
        self.block_stack = block_stack

        # 刷新列表
        self.__refresh_all()

    def __rename(self):
        """
        重命名项目

        :return: 无
        """

        def on_btn_ok():
            """
            点击ok时

            :return: 无
            """
            # 按钮确认事件

            # 获取新建文件名称
            file_name = entry_file_name.get()

            # 有禁止字符的禁止保存
            for ch in file_name:
                if ch in ["$", ".", "/"]:
                    self.__message_box("错误", "不能包含非法字符：$ . /")
                    return

            if not part_object.set_name(file_name):
                self.__message_box("错误", "名字非法")
                return

            # 关闭窗口
            toplevel_window.destroy()

            # 刷新
            self.__refresh_all()

            # 写盘
            self.disk.write_disk()

        # 获取part对象
        part_object = self.__get_file_list_selected_part_object()

        # 如果是系统文件则拒绝重命名
        if part_object.is_system_file():
            self.__message_box("提示", "系统文件" + part_object.get_name() + "禁止被重命名")
            return

        toplevel_window, entry_file_name = \
            self.__show_name_input_box(
                title="重命名",
                message="输入新名称：",
                on_btn_ok=on_btn_ok,
                on_btn_cancel=lambda: toplevel_window.destroy())

    def __show_yes_no_box(self, title, message, on_btn_yes, on_btn_no):
        """
        显示 是和否 对话框

        :param title: 标题
        :param message: 信息
        :param on_btn_yes: 点击确认事件
        :param on_btn_no: 点击取消事件
        :return:
        """

        # 创建询问是否保存窗口
        toplevel_yes_no = Toplevel()
        toplevel_yes_no.geometry("{}x{}+{}+{}".format(
            400,
            100,
            int(self.root.winfo_x() + (self.root.winfo_width() / 2 - 400 / 2)),
            int(self.root.winfo_y() + (self.root.winfo_height() / 2 - 100 / 2))
        ))
        toplevel_yes_no.resizable(False, False)
        toplevel_yes_no.grab_set()
        toplevel_yes_no.focus_set()
        toplevel_yes_no.bind("<Return>", lambda event: on_btn_yes())
        toplevel_yes_no.title(title)

        # 设置label
        Label(toplevel_yes_no, text="\n" + message).pack(anchor="n", padx=5, pady=5)

        # 设置yes
        btn_yes = Button(toplevel_yes_no, text="是", command=on_btn_yes)
        btn_yes.pack(side=LEFT, padx=30, pady=10)
        btn_yes.focus_set()

        # 设置no
        btn_no = Button(toplevel_yes_no, text="否", command=on_btn_no)
        btn_no.pack(side=RIGHT, padx=30, pady=10)

        return toplevel_yes_no

    def __delete(self):
        """
        删除文件

        :return: 无
        """

        def on_btn_yes():
            if part_object.is_dir():
                self.disk.delete_dir(
                    self.current_disk_block,
                    part_object.get_name()
                )
            if part_object.is_ordinary_file():
                self.disk.delete_ordinary_file(
                    self.current_disk_block,
                    part_object.get_name()
                )

            # 关闭窗口
            toplevel_yes_no.destroy()

            self.__refresh_all()

            # 写盘
            self.disk.write_disk()

        def on_btn_no():

            toplevel_yes_no.destroy()

        part_object = self.__get_file_list_selected_part_object()

        # 获取失败
        if part_object is None:
            return

        # 提示消息
        message = ""

        if part_object.is_dir():

            # 检查是否为空目录
            if not self.disk[part_object.get_begin_block_index()].is_empty():
                message = "目录" + part_object.get_name() + "为非空，是否确定删除？"
            else:
                message = "是否删除空目录" + part_object.get_name() + "？"

        if part_object.is_ordinary_file():
            message = "是否删除文件" + part_object.get_name() + "？"

        if part_object.is_system_file():
            self.__message_box("提示", "系统文件" + part_object.get_name() + "不可删除")
            return

        toplevel_yes_no = self.__show_yes_no_box(
            "提示",
            message,
            on_btn_yes,
            on_btn_no
        )

    def __open_fat(self):
        """
        选定的FAT表内容项对应的盘块内容

        :return: 无
        """

        # 获取选中的FAT
        for item in self.treeview_fat.selection():
            block_index = self.treeview_fat.item(item, "values")[0]

            # 获取01字符串表
            block_list = self.disk[int(block_index)].get_block_list()

            # 新窗口
            toplevel_block_content = Toplevel()
            toplevel_block_content.geometry("{}x{}+{}+{}".format(
                700,
                300,
                int(self.root.winfo_x() + (self.root.winfo_width() / 2 - 700 / 2)),
                int(self.root.winfo_y() + (self.root.winfo_height() / 2 - 300 / 2))
            ))
            toplevel_block_content.title("磁盘块" + block_index + "内容（点击刷新）")
            toplevel_block_content.focus_set()
            toplevel_block_content.resizable(False, False)

            # 显示内容
            label_hex_content = Label(
                toplevel_block_content,
                text=self.block_hex_list[int(block_index)],
                font=("Courier New", 14)
            )
            label_hex_content.pack()

            # 点击界面更新
            label_hex_content.bind(
                "<Button-1>",
                lambda event: label_hex_content.config(text=self.block_hex_list[int(block_index)])
            )

    def __modify_properties(self):
        """
        修改文件属性

        :return: 无
        """

        def on_btn_ok():
            # 确定按钮事件

            # 系统文件必须是只读的，否则弹出错误
            if stringvar_file_property.get() == "System" and \
                    stringvar_permission.get() != "Readonly":
                self.__message_box("提示", "系统文件必须为只读")
                return

            # 普通文件或系统文件的选择与修改
            if stringvar_file_property.get() == "Ordinary":
                part_object.set_ordinary_file(True)
                part_object.set_system_file(False)
            if stringvar_file_property.get() == "System":
                part_object.set_ordinary_file(False)
                part_object.set_system_file(True)

            # 是否为只读的修改
            if stringvar_permission.get() == "Readonly":
                part_object.set_readonly(True)
            if stringvar_permission.get() == "NULL":
                part_object.set_readonly(False)

            # 刷新列表
            self.__refresh_all()

            # 写盘
            self.disk.write_disk()

            toplevel_modify.destroy()

        # 获取part对象
        part_object = self.__get_file_list_selected_part_object()

        # 修改属性窗口
        toplevel_modify = Toplevel()
        toplevel_modify.geometry("{}x{}+{}+{}".format(
            300,
            160,
            int(self.root.winfo_x() + (self.root.winfo_width() / 2 - 300 / 2)),
            int(self.root.winfo_y() + (self.root.winfo_height() / 2 - 160 / 2))
        ))
        toplevel_modify.title("修改属性")
        toplevel_modify.focus_set()
        toplevel_modify.grab_set()
        toplevel_modify.resizable(False, False)

        # 文件类型提示label
        Label(toplevel_modify, text="文件类型：", justify=LEFT).pack()

        # 该变量用于跟踪用户选择的文件类型
        stringvar_file_property = StringVar()

        # 获取当前值
        if part_object.is_system_file():
            stringvar_file_property.set("System")
        if part_object.is_ordinary_file():
            stringvar_file_property.set("Ordinary")

        # 单选框
        radiobutton_ordinary = Radiobutton(
            toplevel_modify,
            text="普通文件",
            variable=stringvar_file_property,
            value="Ordinary"
        )
        radiobutton_ordinary.pack()

        radiobutton_system = Radiobutton(
            toplevel_modify,
            text="系统文件",
            variable=stringvar_file_property,
            value="System"
        )
        radiobutton_system.pack()

        # 文件权限提示label
        Label(toplevel_modify, text="文件权限：", justify=LEFT).pack()

        # 跟踪用户选择的权限类型
        stringvar_permission = StringVar()

        # 获取当前权限类型
        if part_object.is_readonly():
            stringvar_permission.set("Readonly")

        # 只读复选框
        checkbutton_readonly = Checkbutton(
            toplevel_modify,
            text="只读",
            onvalue="Readonly",
            offvalue="NULL",
            variable=stringvar_permission
        )
        checkbutton_readonly.pack()

        # 确定按钮
        button_ok = Button(toplevel_modify, text="确定", command=lambda: on_btn_ok())
        button_ok.pack(anchor="s", side=LEFT, padx=30, pady=10)

        # 取消按钮
        button_cancel = Button(toplevel_modify, text="取消", command=lambda: toplevel_modify.destroy())
        button_cancel.pack(anchor='s', side=RIGHT, padx=30, pady=10)

        # 要执行这一个方法才会显示选择的默认值
        toplevel_modify.mainloop()
