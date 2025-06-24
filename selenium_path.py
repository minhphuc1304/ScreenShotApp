import selenium_stealth
import os

print(os.path.join(selenium_stealth.__path__[0], "js"))

# C:\Users\Admin\.conda\envs\gia_env\lib\site-packages\selenium_stealth\js

# pyinstaller --noconfirm --onefile --windowed --icon=logo.ico --add-data="C:/Users/Admin/.conda/envs/gia_env/lib/site-packages/selenium_stealth/js;selenium_stealth/js" --name=GIA_Downloader GIA_download_window_v1.py
