# Building the Executable

## Prerequisites

1. Python 3.8 or higher installed
2. Required Python packages:
   ```bash
   pip install pyinstaller pillow
   ```

## Build Instructions

### Option 1: Using the Build Script (Recommended)

**Windows:**
```bash
build_exe.bat
```

**Linux/Mac:**
```bash
chmod +x build_exe.sh
./build_exe.sh
```

### Option 2: Manual Build

Run the following command from the project root directory:

```bash
python -m PyInstaller --onefile --windowed --name "7D2D-ServerConfigEditor" --icon="icon.ico" --add-data "icon.ico;." --add-data "Logos and Images;Logos and Images" 7d2d_server_config_editor.py
```

**Note:** On Linux/Mac, use `:` instead of `;` in the `--add-data` arguments.

## Output

The executable will be created in the `dist` folder:
- **Location:** `dist/7D2D-ServerConfigEditor.exe`
- **Size:** ~22 MB (standalone, no dependencies required)
- **Icon:** Windows icon is embedded in the executable

## What Gets Bundled

The PyInstaller build includes:
- Python interpreter and all required libraries
- Application icon (`icon.ico`)
- Tooltip icon (`Logos and Images/tooltip-icon.png`)
- All other resources in the `Logos and Images` folder

## Resource Loading

The application uses the `resource_path()` helper function to correctly locate bundled resources both when:
- Running from source (development)
- Running as compiled executable (production)

## Troubleshooting

### Icon Not Showing
- Ensure `icon.ico` exists in the project root
- The icon is embedded in the EXE during build
- Windows Explorer may need to refresh icon cache

### Missing Resources
If you see "file not found" errors:
1. Verify all resources exist in the correct folders
2. Check the `--add-data` arguments in the build command
3. Rebuild the executable

### Build Fails
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version (3.8+)
3. Clear previous builds: `rmdir /s /q build dist` (Windows) or `rm -rf build dist` (Linux/Mac)
4. Try building again

## Cleaning Build Artifacts

To clean up build files:

**Windows:**
```bash
rmdir /s /q build
rmdir /s /q dist
del *.spec
```

**Linux/Mac:**
```bash
rm -rf build dist
rm *.spec
```
