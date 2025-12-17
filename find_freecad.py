"""
Helper script to find and configure FreeCAD for Python.
This script searches common FreeCAD installation locations and adds them to sys.path.
"""
import sys
import os
from pathlib import Path

def find_freecad():
    """Search for FreeCAD installation directories."""
    possible_paths = [
        # Common Windows installation paths
        Path("C:/Program Files/FreeCAD"),
        Path("C:/Program Files/FreeCAD 1.0"),
        Path("C:/Program Files/FreeCAD 0.21"),
        Path(os.path.expanduser("~/AppData/Local/Programs/FreeCAD")),
        Path(os.path.expanduser("~/AppData/Local/Microsoft/WinGet/Packages/FreeCAD.FreeCAD_Microsoft.Winget.Source_8wekyb3d8bbwe")),
        # Check environment variables
        Path(os.environ.get("FREECAD_PATH", "")),
    ]
    
    # Try to find FreeCAD exe in common locations
    for drive in ["C:/", "D:/"]:
        for version in ["1.0", "0.21", "0.20"]:
            possible_paths.append(Path(f"{drive}FreeCAD {version}"))
            possible_paths.append(Path(f"{drive}Program Files/FreeCAD {version}"))
    
    for base_path in possible_paths:
        if not base_path.exists():
            continue
            
        # Look for typical FreeCAD subdirectories
        for subdir in ["", "bin", "lib", "Mod"]:
            check_path = base_path / subdir
            if check_path.exists():
                # Check if FreeCAD.pyd or FreeCAD.so exists
                if any((check_path / file).exists() for file in ["FreeCAD.pyd", "FreeCAD.so", "_FreeCAD.pyd"]):
                    return check_path
                
                # Check subdirectories
                lib_path = check_path / "lib"
                if lib_path.exists() and any((lib_path / file).exists() for file in ["FreeCAD.pyd", "FreeCAD.so"]):
                    return lib_path
    
    return None

def setup_freecad():
    """Configure Python path for FreeCAD."""
    freecad_path = find_freecad()
    
    if freecad_path:
        print(f"Found FreeCAD at: {freecad_path}")
        sys.path.insert(0, str(freecad_path))
        sys.path.insert(0, str(freecad_path.parent / "bin"))
        sys.path.insert(0, str(freecad_path.parent / "lib"))
        sys.path.insert(0, str(freecad_path.parent / "Mod"))
        
        try:
            import FreeCAD
            print(f"[OK] FreeCAD imported successfully!")
            print(f"[OK] FreeCAD version: {FreeCAD.Version()}")
            return True
        except ImportError as e:
            print(f"[ERROR] Could not import FreeCAD: {e}")
            print(f"  Added paths to sys.path but import still failed.")
            return False
    else:
        print("[ERROR] FreeCAD installation not found!")
        print("\nPlease install FreeCAD manually:")
        print("1. Download from: https://www.freecad.org/downloads.php")
        print("2. Or run: winget install FreeCAD.FreeCAD")
        return False

if __name__ == "__main__":
    success = setup_freecad()
    sys.exit(0 if success else 1)
