import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser

from handleReq import start_work, load_default_directory, get_resource_path
from PIL import Image, ImageTk  # 需要安装 pillow 库
import os
import json


def show_text():
    """获取文本框内容并显示在弹窗中"""
    text = entry.get()
    if text and text != placeholder:
        try:
            res_code, res_msg = start_work(text)  # 这里可能会发生异常
            if res_code == 200:
                saved_dir = load_default_directory()
                default_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                downloads_folder = saved_dir if saved_dir else default_downloads
                messagebox.showinfo("下载成功", f"文件已下载至 {downloads_folder} 目录中")
            else:
                messagebox.showwarning("下载失败", res_msg)
        except Exception as e:
            print(f"发生异常: {e}")
            messagebox.showwarning("下载失败", f"程序执行发生异常，异常原因如下：\n{e}")
    else:
        messagebox.showwarning("警告", "文本框为空！")


def open_file():
    """打开文件对话框"""
    saved_dir = load_default_directory()
    default_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    print(f'saved_dir: {saved_dir}')
    print(f'default_downloads: {default_downloads}')
    if saved_dir:
        os.startfile(saved_dir)
    else:
        os.startfile(default_downloads)


def show_about():
    """显示关于对话框"""
    messagebox.showinfo("关于", "版本 1.0")


def show_disclaimer():
    messagebox.showinfo("免责说明",
                        "本软件由程序开发爱好者制作，仅供学习参考，产生任何后果由用户承担！请自觉遵守法律，使用获取渠道合法的正版规范文件！")


def clear_text():
    """清空文本输入框，并让其失去焦点"""
    entry.delete(0, tk.END)
    set_placeholder()  # 重新设置占位符
    root.focus_set()  # 让窗口本身获得焦点，使 Entry 失去焦点


def set_placeholder():
    """设置占位符"""
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(fg="gray")


def remove_placeholder(event):
    """点击输入框时清除占位符"""
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(fg="black")


def restore_placeholder(event):
    """如果输入框为空，恢复占位符"""
    if not entry.get():
        set_placeholder()


def toggle_fullscreen(event=None):
    """切换全屏模式"""
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes('-fullscreen', is_fullscreen)


def exit_fullscreen(event=None):
    """退出全屏模式"""
    global is_fullscreen
    is_fullscreen = False
    root.attributes('-fullscreen', False)


def init_config():
    """初始化 JSON 配置文件"""
    default_config = {
        "default_directory": "",
        "background_color": "#f0f0f0"  # 默认背景颜色（白色）
    }
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(default_config, f)


def load_config():
    """加载 JSON 配置"""
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"default_directory": "", "background_color": "#f0f0f0"}


def save_config(config1):
    """保存 JSON 配置"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config1, f)


def apply_background_color(color):
    """应用背景颜色"""
    root.config(bg=color)


def save_default_directory(directory):
    """保存默认目录到 JSON"""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"default_directory": directory}, f)


def open_settings():
    """打开设置窗口（居中显示）"""
    settings_win = tk.Toplevel(root)
    settings_win.title("设置")
    settings_win.geometry("400x300")
    settings_win.resizable(False, False)

    # 获取主窗口位置 & 计算弹窗居中位置
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()

    settings_width = 400
    settings_height = 300

    pos_x = root_x + (root_width - settings_width) // 2
    pos_y = root_y + (root_height - settings_height) // 2

    settings_win.geometry(f"{settings_width}x{settings_height}+{pos_x}+{pos_y}")
    settings_win.transient(root)
    settings_win.grab_set()

    # 创建框架（左右布局）
    left_frame = tk.Frame(settings_win, width=120, height=300, bg="#f0f0f0")
    right_frame = tk.Frame(settings_win, width=280, height=300, bg="white")

    left_frame.pack(side="left", fill="y")
    right_frame.pack(side="right", expand=True, fill="both")

    # 右侧内容标签
    content_label = tk.Label(right_frame, text="请选择设置项", font=("microsoft yahei", 12), bg="white")
    content_label.pack(pady=10)

    # 按钮默认颜色
    default_bg = "#f0f0f0"
    selected_bg = "#c9a161"

    def reset_buttons():
        """重置按钮颜色"""
        btn_theme.config(bg=default_bg)
        btn_file.config(bg=default_bg)
        btn_hotkey.config(bg=default_bg)

    def show_theme_settings():
        """显示主题设置"""
        reset_buttons()
        btn_theme.config(bg=selected_bg)

        for widget in right_frame.winfo_children():
            if widget != content_label:
                widget.destroy()

        content_label.config(text="🎨 主题设置")

        # 读取当前背景颜色
        config = load_config()
        current_color = config["background_color"]
        color_var = tk.StringVar(value=current_color)

        def change_color():
            """打开颜色选择器"""
            new_color = colorchooser.askcolor(title="选择背景颜色")[1]
            if new_color:
                color_var.set(new_color)
                root.config(bg=new_color)
                btn_frame.config(bg=new_color)
                apply_color()

        def apply_color():
            """应用并保存颜色"""
            selected_color = color_var.get()
            root.config(bg=selected_color)
            config = load_config()
            config["background_color"] = selected_color
            save_config(config)
            show_theme_settings()

        def reset_default():
            """恢复默认背景颜色"""
            default_color = "#f0f0f0"
            color_var.set(default_color)
            root.config(bg=default_color)
            btn_frame.config(bg=default_color)
            config = load_config()
            config["background_color"] = default_color
            save_config(config)
            show_theme_settings()

        color_entry = tk.Entry(right_frame, textvariable=color_var, width=20, state="readonly")
        color_entry.pack(pady=10)

        btn_choose_color = tk.Button(right_frame, text="选择颜色", command=change_color)
        btn_choose_color.pack(pady=5)

        # “恢复默认” 按钮
        if current_color != "#f0f0f0":
            btn_reset1 = tk.Button(right_frame, text="恢复默认", command=reset_default)
            btn_reset1.pack(side="bottom", pady=5)

    def show_file_settings():
        """显示文件管理设置，并高亮按钮"""
        reset_buttons()
        btn_file.config(bg=selected_bg)

        for widget in right_frame.winfo_children():
            if widget != content_label:
                widget.destroy()

        content_label.config(text="📂 文件管理设置")

        # 读取默认目录,config.json配置
        saved_dir = load_default_directory()
        default_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        dir_var = tk.StringVar()
        dir_var.set(saved_dir if saved_dir else default_downloads)

        # **添加文本框上方的描述标签**
        dir_label = tk.Label(right_frame, text="当前文件默认导出到以下目录：", font=("microsoft yahei", 12), bg="white")
        dir_label.pack(pady=(10, 0))  # 只在上方留一点空隙

        dir_entry = tk.Entry(right_frame, textvariable=dir_var, width=30, state="readonly")
        dir_entry.pack(pady=10)

        def change_directory():
            """更改目录"""
            selected_dir = filedialog.askdirectory(title="选择文件夹")
            if selected_dir:
                dir_var.set(selected_dir)
                config = load_config()
                config["default_directory"] = selected_dir
                save_config(config)
                refresh_file_settings()

        def open_directory():
            """打开目录"""
            directory = dir_var.get()
            if os.path.exists(directory):
                os.startfile(directory)
            else:
                messagebox.showerror("错误", "目录不存在")

        def reset_to_default():
            """恢复默认目录"""
            config = load_config()
            config["default_directory"] = ""
            save_config(config)
            refresh_file_settings()

        def refresh_file_settings():
            """刷新文件管理 UI"""
            show_file_settings()

        # 按钮布局
        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=5)

        btn_change_dir = tk.Button(button_frame, text="更改目录", command=change_directory)
        btn_open_dir = tk.Button(button_frame, text="打开目录", command=open_directory)

        btn_change_dir.pack(side="left", padx=5)
        btn_open_dir.pack(side="left", padx=5)

        # “恢复默认” 按钮（如果配置了目录则显示）
        if saved_dir:
            btn_reset2 = tk.Button(right_frame, text="恢复默认", command=reset_to_default)
            btn_reset2.pack(side="bottom", pady=5)

    def show_hotkey_settings():
        """显示热键说明"""
        reset_buttons()
        btn_hotkey.config(bg=selected_bg)  # 设置高亮效果

        for widget in right_frame.winfo_children():
            if widget != content_label:
                widget.destroy()

        content_label.config(text="⌨️热键说明")

        hotkey_text = """
        📌 常用快捷键：
        - F11  -> 切换全屏
        - Esc  -> 退出全屏
        
        """

        hotkey_label = tk.Label(right_frame, text=hotkey_text, font=("microsoft yahei", 12), bg="white", justify="left",
                                anchor="w")
        hotkey_label.pack(padx=10, pady=5, anchor="w")

    # 左侧按钮
    btn_theme = tk.Button(left_frame, text="主题管理", command=show_theme_settings, width=12, bg=default_bg)
    btn_file = tk.Button(left_frame, text="文件管理", command=show_file_settings, width=12, bg=default_bg)
    btn_hotkey = tk.Button(left_frame, text="热键说明", command=show_hotkey_settings, width=12, bg=default_bg)

    btn_theme.pack(pady=10)
    btn_file.pack(pady=10)
    btn_hotkey.pack(pady=10)


if __name__ == '__main__':
    # JSON 配置文件路径
    CONFIG_FILE = get_resource_path("assets/config.json")

    # 创建主窗口
    root = tk.Tk()
    root.title("国家计量技术规范下载器")

    # 初始化 JSON 配置
    init_config()
    config = load_config()
    apply_background_color(config["background_color"])

    # 加载 PNG 或 JPG 图片
    icon_image = Image.open(get_resource_path("assets/logo.png"))  # 读取 PNG/JPG
    icon_photo = ImageTk.PhotoImage(icon_image)  # 转换为 Tkinter 可用格式

    # 设置窗口图标
    root.iconphoto(True, icon_photo)
    root.geometry("800x580")  # 初始化窗口大小

    # 创建菜单栏
    menu_bar = tk.Menu(root)

    # 文件菜单
    file_menu = tk.Menu(menu_bar, tearoff=0)  # `tearoff=0` 取消默认的虚线
    file_menu.add_command(label="打开", command=open_file)
    file_menu.add_command(label="设置", command=open_settings)  # 添加“设置”选项
    file_menu.add_separator()
    file_menu.add_command(label="退出", command=root.quit)

    # 关于菜单
    about_menu = tk.Menu(menu_bar, tearoff=0)
    about_menu.add_command(label="关于本软件", command=show_about)
    about_menu.add_command(label="免责说明", command=show_disclaimer)

    # 添加菜单到菜单栏
    menu_bar.add_cascade(label="文件", menu=file_menu)
    menu_bar.add_cascade(label="关于", menu=about_menu)

    # 关联菜单栏到窗口
    root.config(menu=menu_bar)
    root.minsize(600, 400)  # 设置最小大小
    is_fullscreen = False  # 初始为非全屏

    # 计算居中位置
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = (screen_width - 800) // 2
    center_y = (screen_height - 580) // 2
    root.geometry(f"800x580+{center_x}+{center_y}")  # 设置窗口位置

    # 绑定键盘事件
    root.bind("<F11>", toggle_fullscreen)  # 按 F11 切换全屏
    root.bind("<Escape>", exit_fullscreen)  # 按 ESC 退出全屏

    # 占位符文本
    placeholder = "请输入“查看详细”页网址，例如：https://jjg.spc.org.cn/resmea/standard/JJG%25201028-2024/?"

    # 创建文本输入框
    entry = tk.Entry(root, font=("microsoft yahei", 12), width=80, fg="gray")
    entry.pack(pady=20)

    # 绑定事件
    entry.insert(0, placeholder)  # 预填充占位符
    entry.bind("<FocusIn>", remove_placeholder)  # 点击输入框时清除占位符
    entry.bind("<FocusOut>", restore_placeholder)  # 失去焦点时恢复占位符

    # 创建按钮框架
    btn_frame = tk.Frame(root, bg=config["background_color"])
    btn_frame.pack()

    show_button = tk.Button(btn_frame, text="下载文件", font=("microsoft yahei", 13), command=show_text)
    show_button.pack(side=tk.LEFT, padx=20)

    clear_button = tk.Button(btn_frame, text="清空", font=("microsoft yahei", 13), command=clear_text)
    clear_button.pack(side=tk.RIGHT, padx=20)

    # 运行主循环
    root.mainloop()
