#!/usr/bin/env python3
"""
Modified example script with automatic FreeCAD path detection.
This script tries to find FreeCAD installation and generates a 3D CAD file.
"""
import sys
import os
from pathlib import Path

def find_and_setup_freecad():
    """Search for FreeCAD and add to sys.path."""
    possible_paths = [
        # Common Windows installation paths
        Path("C:/Program Files/FreeCAD 1.0/bin"),
        Path("C:/Program Files/FreeCAD 0.21/bin"),
        Path("C:/Program Files/FreeCAD/bin"),
        Path(os.path.expanduser("~/AppData/Local/Programs/FreeCAD/bin")),
        # Conda-based installations
        Path("C:/Users/" + os.environ.get("USERNAME", "") + "/AppData/Local/FreeCAD/bin"),
        # Check for FreeCAD.pyd in current Python's site-packages
    ]
    
    # Also check environment variable
    freecad_path = os.environ.get("FREECAD_PATH")
    if freecad_path:
        possible_paths.insert(0, Path(freecad_path) / "bin")
    
    for base_path in possible_paths:
        if not base_path.exists():
            continue
        
        # Add FreeCAD paths to sys.path
        sys.path.insert(0, str(base_path))
        sys.path.insert(0, str(base_path.parent / "lib"))
        sys.path.insert(0, str(base_path.parent / "Mod"))
        
        try:
            import FreeCAD
            print(f"[OK] Found FreeCAD at: {base_path}")
            print(f"[OK] FreeCAD version: {FreeCAD.Version()}")
            return True
        except ImportError:
            # Remove the paths and try next location
            sys.path.remove(str(base_path))
            sys.path.remove(str(base_path.parent / "lib"))
            sys.path.remove(str(base_path.parent / "Mod"))
            continue
    
    return False

# Try to setup FreeCAD
if not find_and_setup_freecad():
    print("[ERROR] Could not find FreeCAD installation!")
    print("\nPlease either:")
    print("1. Set FREECAD_PATH environment variable to your FreeCAD installation directory")
    print("2. Use FreeCAD's bundled Python instead:")
    print('   "C:\\path\\to\\FreeCAD\\bin\\python.exe" run_example.py')
    sys.exit(1)

# Now import project modules
from typing import List
from text_to_cad_common.geometric_primitives import (
    SupportedShapes,
    Parameters,
    Translation,
    RotationEuler,
)
from generative_cad.freecad_tools import generate_freecad_file, Object3D

if __name__ == "__main__":
    print("\n[INFO] Creating 3D objects...")
    
    # Create a sphere
    sphere = Object3D(
        name=SupportedShapes.SPHERE,
        parameters=Parameters(shape=SupportedShapes.SPHERE, radius=1),
        translation=Translation(x=0, y=2, z=2),
        rotation=RotationEuler(x_rad=0, y_rad=0, z_rad=0),
    )
    
    # Create a torus
    torus = Object3D(
        name=SupportedShapes.TORUS,
        parameters=Parameters(shape=SupportedShapes.TORUS, radius1=0.1, radius2=10),
        translation=Translation(x=-1, y=0, z=1),
        rotation=RotationEuler(x_rad=1.57, y_rad=0, z_rad=0),
    )
    
    objects: List[Object3D] = [sphere, torus]
    freecad_file_name = "example_output.FCStd"
    
    print(f"[INFO] Generating FreeCAD file: {freecad_file_name}")
    generate_freecad_file(objects=objects, output_file=freecad_file_name)
    
    print(f"\n[SUCCESS] Generated {freecad_file_name}!")
    print(f"[INFO] Open this file in FreeCAD to view the 3D objects.")
    print(f"[INFO] In FreeCAD: View -> Visibility -> Show all objects")
    
    # Don't try to open FreeCAD automatically on Windows (may not work)
    # Instead, just tell the user to open it manually
