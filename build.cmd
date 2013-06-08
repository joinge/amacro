copy /b macro.py+,,
copy /b gui.py+,,
copy /b sync.py+,,
python pyinstaller/pyinstaller.py gui.py
python pyinstaller/pyinstaller.py --onefile sync.py