from tkinter import *
from tkinter import messagebox
from tkinter.messagebox import askyesno
from tkinter.ttk import *
import traceback

import FileExceptions
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

        # 导航栏和文件操作窗口
        self.frame_manager = Frame(self.root)
        self.frame_manager.pack(side=TOP, fill=BOTH)

        # 导航栏frame
        self.frame_guide = Frame(self.frame_manager)
        self.frame_guide.pack(side=TOP, fill="x", anchor="n")

        # 后退按钮
        self.btn_back = Button(self.frame_guide, text="后退", command=self.__back)
        self.btn_back.pack(side=LEFT, fill="y", padx=5, pady=5)

        # 路径栏
        self.entry_path = Entry(self.frame_guide)
        self.entry_path.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.entry_path.bind("<Return>", self.__go)

        # 前往按钮
        self.btn_go = Button(self.frame_guide, text="前往", command=self.__go)
        self.btn_go.pack(side=LEFT, fill="y", padx=5, pady=5)

        # 文件操作部分分为了左边的文件树和右边的文件列表，所以需要一个容易装这两个
        self.frame_op = Frame(self.frame_manager)
        self.frame_op.pack(side=LEFT, fill=BOTH, expand=True)

        # 文件树
        self.treeview_tree = Treeview(
            self.frame_op,
            columns=["Name"],
            show="tree"
        )
        self.treeview_tree.column("Name", width=0)
        self.treeview_tree.pack(side=LEFT, fill=BOTH, padx=5, pady=5)

        # 文件列表
        self.treeview_file_list = Treeview(
            self.frame_op,
            columns=["Name", "Properties", "Permission"],
            show="headings",
            selectmode=EXTENDED
        )
        self.treeview_file_list.pack(padx=5, pady=5)
        self.treeview_file_list.pack(fill=BOTH, expand=True)
        self.treeview_file_list.column("Name", width=100)
        self.treeview_file_list.column("Properties", width=100)
        self.treeview_file_list.column("Permission", width=100)
        self.treeview_file_list.heading("Name", text="名称")
        self.treeview_file_list.heading("Properties", text="属性")
        self.treeview_file_list.heading("Permission", text="权限")

        # 获取文件内容
        self.__refresh_all()

        # 右键菜单
        self.treeview_file_list.bind("<Button-3>", self.__show_pop_up_menu)

        # 左键双击菜单
        self.treeview_file_list.bind("<Double-Button-1>", self.__open)

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
        if self.__get_selected_part_object() is not None:
            menu_pop_up.add_command(label="重命名", command=self.__rename)
            menu_pop_up.add_command(label="删除文件")

        menu_pop_up.post(event.x_root, event.y_root)

    def __refresh_all(self):
        """
        刷新文件列表

        :return: 无
        """

        # 删除文件显示列表中的所有内容
        self.treeview_file_list.delete(*self.treeview_file_list.get_children())

        # 获取存在的part，并添加到显示列表中
        part_list = self.disk[self.current_disk_block].get_exist_part_list()
        for part_object in part_list:
            self.treeview_file_list.insert("", index=END, values=(
                part_object.get_name(),
                part_object.get_properties_string(),
                part_object.get_permission_string()
            ))

        # 获取路径

        path = self.__get_current_path()

        # 删除文本框内容
        self.entry_path.delete(0, END)

        # 将路径插入到文本框
        self.entry_path.insert(END, path)

        # 刷新文件树
        pass

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

        def on_btn_ok(event=None):
            # 按钮确认事件

            # 获取新建文件名称
            file_name = entry_file_name.get()

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
            self.__show_name_input_box(title, on_btn_ok, lambda : toplevel_window.destroy())

    def __show_name_input_box(self, title, on_btn_ok, on_btn_cancel):
        """
        显示命名框

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
        label_guide = Label(toplevel_window, text="输入新建名称：", justify=LEFT)
        label_guide.pack(anchor="nw", padx=5, pady=5)

        # 设置文本框
        entry_file_name = Entry(toplevel_window)
        entry_file_name.pack(anchor="n", fill="x", expand=True, padx=5)
        entry_file_name.bind("<Return>", on_btn_ok)
        entry_file_name.focus_set()

        # 设置确认按钮
        btn_ok = Button(toplevel_window, text="确定", command=on_btn_ok)
        btn_ok.pack(side=LEFT, padx=30, pady=10)

        # 设置取消按钮
        btn_cancel = Button(toplevel_window, text="取消", command=on_btn_cancel)
        btn_cancel.pack(side=RIGHT, padx=30, pady=10)

        return toplevel_window, entry_file_name

    def __get_selected_part_object(self):
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

    def __open(self, event):
        """
        打开文件或目录

        :param event: 事件
        :return: 无
        """

        part_object = self.__get_selected_part_object()

        try:
            # 不同文件不同打开方法

            if part_object.is_dir():
                self.__open_dir(event, part_object)
            if part_object.is_ordinary_file():
                self.__open_file(event, part_object)
        except AttributeError:
            return

    def __open_dir(self, event, part_object):
        """
        打开目录

        :param event: 事件
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

    def __open_file(self, event, part_object):
        """
        打开文件

        :param event: 事件
        :param part_object: part对象
        :return: 无
        """

        def exit_confirm():
            # 点击退出时事件

            # 如果文本框中的内容与磁盘中的一致则直接退出
            if text_content.get(1.0, END)[:-1] == self.disk.get_full_content(part_object.get_begin_block_index()):
                toplevel_file_editor.destroy()
                # 编辑窗口数-1
                self.current_editor_window_count -= 1
                return

            # 创建询问是否保存窗口
            toplevel_save_confirm = Toplevel()
            toplevel_save_confirm.geometry("{}x{}+{}+{}".format(
                400,
                100,
                int(self.root.winfo_x() + (self.root.winfo_width() / 2 - 400 / 2)),
                int(self.root.winfo_y() + (self.root.winfo_height() / 2 - 100 / 2))
            ))
            toplevel_save_confirm.resizable(False, False)
            toplevel_save_confirm.grab_set()
            toplevel_save_confirm.focus_set()
            toplevel_save_confirm.bind("<Return>", lambda key_event: on_btn_yes(toplevel_save_confirm))

            # 设置label
            label_ask = Label(toplevel_save_confirm, text="\n是否保存文件" + part_object.get_name() + "？")
            label_ask.pack(anchor="n", padx=5, pady=5)

            # 设置yes
            btn_yes = Button(toplevel_save_confirm, text="是", command=lambda: on_btn_yes(toplevel_save_confirm))
            btn_yes.pack(side=LEFT, padx=30, pady=10)
            btn_yes.focus_set()

            # 设置no
            btn_no = Button(toplevel_save_confirm, text="否", command=lambda: on_btn_no(toplevel_save_confirm))
            btn_no.pack(side=RIGHT, padx=30, pady=10)

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

        def save_file(key_event=None):
            # 保存文件

            try:
                length = self.disk.set_full_content(part_object.get_begin_block_index(),
                                                    text_content.get(1.0, END)[:-1])
            except Exception as e:
                self.__message_box("错误", str(e))
                return

            part_object.set_length(length)

            # 写盘
            self.disk.write_disk()

            # 弹出提示
            self.__message_box("提示", "保存完成，共占用" + str(length) + "个磁盘块")

        # 查看编辑窗口数是否已满
        if self.current_editor_window_count == self.__MAX_EDITOR_WINDOW_COUNT:
            self.__message_box("提示", "最多只能打开5个编辑器")
            return

        # 设置窗口
        toplevel_file_editor = Toplevel()
        toplevel_file_editor.title("文件编辑器：" + self.__get_current_path() + part_object.get_name())
        toplevel_file_editor.geometry("{}x{}+{}+{}".format(
            600,
            300,
            int(self.root.winfo_x() + (self.root.winfo_width() / 2 - 600 / 2)),
            int(self.root.winfo_y() + (self.root.winfo_height() / 2 - 300 / 2))
        ))
        toplevel_file_editor.focus_set()
        toplevel_file_editor.resizable(False, False)

        # 设置多行文本框
        text_content = Text(toplevel_file_editor)
        text_content.focus_set()
        text_content.pack(anchor="center", side=BOTTOM, fill=BOTH, expand=True, padx=5, pady=5)

        # 设置菜单栏
        menu_bar = Menu(toplevel_file_editor, tearoff=False)
        menu_file = Menu(menu_bar, tearoff=False)
        menu_file.add_command(label="保存", command=save_file)
        menu_bar.add_cascade(label="文件", menu=menu_file)
        toplevel_file_editor.config(menu=menu_bar)

        # 保存快捷键
        toplevel_file_editor.bind("<Control-KeyPress-s>", func=save_file)

        # 关闭事件
        toplevel_file_editor.protocol("WM_DELETE_WINDOW", exit_confirm)

        # 设置文本框内容
        text_content.insert(END, self.disk.get_full_content(part_object.get_begin_block_index()))

        # 设置左下角状态栏
        label_status = Label(toplevel_file_editor)
        label_status.pack(side=BOTTOM)

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
        label_message = Label(toplevel_message_window, text="\n" + message)
        label_message.pack(anchor="n", padx=10, pady=10)
        btn_error_ok = Button(toplevel_message_window, text="确定", command=lambda: toplevel_message_window.destroy())
        btn_error_ok.pack(anchor="s", pady=5)
        btn_error_ok.focus_set()
        btn_error_ok.bind("<Return>", lambda event: toplevel_message_window.destroy())

        # 下面是另一种显示错误信息的方法，但此处有些问题，故不使用
        # messagebox.showinfo(title="错误", message=error)

    def __go(self, event=None):
        """
        前往路径

        :return: 无
        """

        # 获取路径
        path = self.entry_path.get()

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

        def on_btn_ok(event=None):
            """
            点击ok时

            :return: 无
            """
            # 按钮确认事件

            # 获取新建文件名称
            file_name = entry_file_name.get()

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
        part_object = self.__get_selected_part_object()

        toplevel_window, entry_file_name = \
            self.__show_name_input_box(
                title="重命名",
                on_btn_ok=on_btn_ok,
                on_btn_cancel=lambda: toplevel_window.destroy())