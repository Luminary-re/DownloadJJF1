打包发布
pyinstaller --onefile --noconsole --add-data "assets/logo.png;assets" --icon=assets/favicon.ico --name DownloadJJF-uninstall-v1.0.0 src/main.py