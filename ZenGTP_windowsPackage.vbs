
Dim fso
Dim ws
Set fso=CreateObject("Scripting.FileSystemObject")
Set ws=CreateObject("WScript.Shell")
If fso.folderExists(".venv") Then
Else
    ws.Run "python -m venv .venv", 1, true
End If

ws.Run ".\.venv\Scripts\pip install -r requirements.txt", 1, true
ws.Run ".\.venv\Scripts\pyinstaller -F Zen6GTP.py --distpath=./dist/6 --specpath=./spec", 1, false
ws.Run ".\.venv\Scripts\pyinstaller -F Zen7GTP.py --distpath=./dist/7 --specpath=./spec", 1, false