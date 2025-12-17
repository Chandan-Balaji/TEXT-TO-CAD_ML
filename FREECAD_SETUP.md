# Text-to-CAD Setup - Manual FreeCAD Configuration

## Current Status
✅ **All dependencies and packages installed successfully**  
⚠️ **FreeCAD installed but needs manual path configuration**

## The Issue
FreeCAD 1.0.2 is installed via winget, but its installation location couldn't be automatically detected. This is common with Windows Store/winget installations.

## How to Find FreeCAD

### Option 1: Use Windows Search
1. Open Start Menu and search for "FreeCAD"
2. Right-click on FreeCAD app → "Open file location"
3. If it shows a shortcut, right-click the shortcut → "Open file location" again
4. Note the full path (e.g., `C:\Program Files\FreeCAD 1.0\bin`)

### Option 2: Check Start Menu Shortcut Properties
1. Open Start Menu
2. Find "FreeCAD" in the app list
3. Right-click → "More" → "Open file location"
4. Right-click the shortcut → "Properties"
5. Look at the "Target" field - the path shows where FreeCAD.exe is located

### Option 3: Manual Search in File Explorer
Search these locations in File Explorer:
- `C:\Program Files\FreeCAD 1.0\`
- `C:\Users\chand\AppData\Local\Programs\FreeCAD\`
- `C:\Program Files\WindowsApps\` (may need admin access)

## Once You Find FreeCAD

### Method A: Set Environment Variable (Permanent)
1. Copy the FreeCAD bin directory path (e.g., `C:\Program Files\FreeCAD 1.0\bin`)
2. Open PowerShell and run:
   ```powershell
   [Environment]::SetEnvironmentVariable("FREECAD_PATH", "C:\path\to\FreeCAD\bin", "User")
   ```
3. Restart your terminal/PowerShell
4. Run: `python run_example.py`

### Method B: Use FreeCAD's Python (Recommended - Simplest!)
1. Find FreeCAD's Python executable in the bin folder: `python.exe`
2. Run the example using FreeCAD's Python:
   ```powershell
   "C:\path\to\FreeCAD\bin\python.exe" run_example.py
   ```

### Method C: Modify run_example.py
1. Open `run_example.py`
2. Add this line at the top, replacing the path:
   ```python
   import sys
   sys.path.insert(0, r"C:\path\to\FreeCAD\bin")
   ```
3. Run: `python run_example.py`

## Test the Setup

After configuration, you should be able to run:
```bash
python run_example.py
```

This will:
1. Detect FreeCAD
2. Generate a 3D model with a sphere and torus
3. Save it as `example_output.FCStd`
4. You can then open this file in FreeCAD to view the 3D objects

## Need Help?
If you still can't find FreeCAD or have issues:
1. Open FreeCAD from the Start Menu to confirm it works
2. Try reinstalling: `winget uninstall FreeCAD.FreeCAD` then `winget install FreeCAD.FreeCAD`
3. Or download manually from: https://www.freecad.org/downloads.php
