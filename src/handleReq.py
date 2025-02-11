import os
import re
import sys

import requests
import time
import logging
import json


# Input and Parse URL
def input_and_parse_url(raw_url):
    while True:
        pattern = r'http://jjg.spc.org.cn/resmea/standard/([A-Z]{3})%2520([0-9.-]{3,20})/[?]?'
        if raw_url.startswith("https"):
            raw_url = raw_url.replace("https", "http", 1)  # 只替换第一个出现的 https
        match = re.match(pattern, raw_url)
        if match:
            std_type, std_no = match.groups()
            is_success = True
            return is_success, std_type, std_no, raw_url
        else:
            is_success = False
            std_type = ''
            std_no = ''
            return is_success, std_type, std_no, raw_url


# Generate Session
def generate_session(std_type, std_no):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'jjg.spc.org.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0'
    }
    session = requests.session()
    session.headers.update(headers)
    response = session.get(url=f'http://jjg.spc.org.cn/resmea/view/stdonline?a100={std_type}+{std_no}&standclass=')
    return session, response


# Get PDF Session Response
def get_pdf_response(session, token, Myfoxit, std_type, std_no):
    url = f'http://jjg.spc.org.cn/resmea/view/onlinereading?token={token[0]}&Myfoxit={Myfoxit[0]}'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'jjg.spc.org.cn',
        'Pragma': 'no-cache',
        'Referer': f'http://jjg.spc.org.cn/resmea/view/stdonline?a100={std_type}+{std_no}&standclass=',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
        'myfoxit': f'{Myfoxit[0]}'
    }
    response = session.get(url, headers=headers)
    return response


def get_resource_path(relative_path):
    """获取正确的资源文件路径（兼容 PyInstaller 和 Python 运行模式）"""
    # if hasattr(sys, "_MEIPASS"):  # PyInstaller 运行时的临时目录
    #     return os.path.join(sys._MEIPASS, relative_path)
    if getattr(sys, 'frozen', False):  # 运行于 PyInstaller 打包的 exe
        return os.path.join(os.path.dirname(sys.executable), relative_path)

    # 开发模式
    base_path = os.path.abspath(os.path.dirname(__file__))  # 获取 main.py 所在目录
    return os.path.join(base_path, "..", relative_path)  # 返回正确的路径


def load_default_directory():
    """加载默认目录配置"""
    try:
        with open(get_resource_path("assets/config.json"), "r") as f:
            config = json.load(f)
            return config.get("default_directory", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""


# Main function
def download_pdf(session, token, Myfoxit, std_type, std_no):
    logging.basicConfig(level=logging.INFO)
    logging.StreamHandler().setLevel(logging.INFO)
    start_time = time.time()

    # 获取用户的默认下载目录
    print(f'os.path: {os.path}')
    saved_dir = load_default_directory()
    default_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    downloads_folder = saved_dir if saved_dir else default_downloads
    print(f'downloads_folder: {downloads_folder}')

    # 确保下载目录存在
    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)

    # 设置完整的文件路径
    file_path = os.path.join(downloads_folder, f'{std_type} {std_no}.pdf')
    if os.path.exists(file_path):
        for i in range(1, 10001):  # 如果下载的文件加下有10000后缀(1)~(10000)的文件，就随他去吧
            file_path = os.path.join(downloads_folder, f'{std_type} {std_no}({i}).pdf')
            if os.path.exists(file_path) is False:
                break

    # 下载 PDF 并保存
    with open(file_path, 'wb') as f:
        f.write(get_pdf_response(session, token, Myfoxit, std_type, std_no).content)

    end_time = time.time()
    if os.path.exists(file_path):
        res_code = 200
        res_msg = f'下载成功， 用时{end_time - start_time:.2f}秒'
        return res_code, res_msg
    else:
        res_code = 500
        res_msg = '下载失败！\n请检查“查看详细”页网址是否复制正确'
        return res_code, res_msg


def start_work(url_text):
    is_success, std_type, std_no, raw_url = input_and_parse_url(url_text)  # 从输入的url获取规范型号、号码和本身url
    if is_success is False:
        res_code = 500
        res_msg = f"输入的网址格式有误！\n标准格式为：\nhttp://jjg.spc.org.cn/resmea/standard/([A-Z]{3})%2520([0-9.-]{3, 20})/[?]?.*\n而输入的内容为：{url_text}！"
        return res_code, res_msg
    print(f'is_success: {is_success}')
    print(f'std_type: {std_type}')
    print(f'std_no: {std_no}')
    print(f'raw_url: {raw_url}')
    session, response = generate_session(std_type, std_no)  # 根据规范型号、号码得到会话和返回体
    print(f'session: {session}')
    print(f'response: {response}')
    Myfoxit = re.findall('var enc = "([^"]*)"', response.text)
    token = re.findall('var rc = "([^"]*)"', response.text)
    print(f'Myfoxit: {Myfoxit}')
    print(f'token: {token}')
    res_code, res_msg = download_pdf(session, token, Myfoxit, std_type, std_no)  # 执行下载
    return res_code, res_msg
