打包发布
pyinstaller --onedir --noconsole --add-data "assets;assets" src/main.py
pyinstaller --onefile --noconsole --add-data "assets;assets" src/main.py
