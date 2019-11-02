CreateObject("WScript.Shell").Run "pipenv install -d", 1, true
' https://pyinstaller.readthedocs.io/en/stable/usage.html#options
' Don't support UPX!
CreateObject("WScript.Shell").Run "pipenv run pyinstaller -F Zen6GTP.py --distpath=./dist/6 --specpath=./spec", 1, true
CreateObject("WScript.Shell").Run "pipenv run pyinstaller -F Zen7GTP.py --distpath ./dist/7 --specpath ./spec", 1, true