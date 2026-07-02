import os
import sys

from kivy.app import App
from kivy.core.window import Window
from kivy.config import Config
from kivy.resources import resource_add_path

# Khi chạy dưới dạng .exe (PyInstaller), tài nguyên được giải nén vào thư mục
# tạm (_MEIPASS). Chuyển thư mục làm việc / thêm đường dẫn tài nguyên về đó để
# các đường dẫn tương đối 'Resources/...' vẫn tìm thấy ảnh, font.
if getattr(sys, 'frozen', False):
    _bundleDir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    os.chdir(_bundleDir)
    resource_add_path(_bundleDir)

from Menus import MainMenu
from Utility.Settings import Settings

Config.set('kivy', 'exit_on_escape', '0')
# Áp dụng chế độ hiển thị đã lưu (toàn màn hình / cửa sổ) từ cài đặt.
Settings.applyDisplay()

if __name__ == '__main__':
    mainApp = App()
    mainApp.root = MainMenu(mainApp)
    mainApp.run()