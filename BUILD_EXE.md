# Building ReadMe Hero for Windows

The project includes a PyInstaller specification and a Windows build script.

## Recommended build

From the project root in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller ReadMeHero.spec --clean --noconfirm
```

The executable will be created at:

```text
dist\ReadMeHero.exe
```

You can also double-click `build_exe.bat` from Windows Explorer.

## Notes

- The application is built as a windowed single-file executable.
- The ReadMe Hero icon is embedded from `assets/img/1.ico`.
- Language JSON files, themes, and application assets are bundled.
- User-created README images remain in the selected project's `assets/images` folder.
