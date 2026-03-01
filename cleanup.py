"""
================================================================================
                    CLEANUP SCRIPTS FOR MEDICINE ERP
================================================================================

This script provides various cleanup options for the project.
Run from the project root folder: python cleanup.py

Options:
1. Clean build files only
2. Clean and rebuild executable
3. Clean all including data
4. Create fresh distribution package
"""

import os
import shutil
import sys

# Package name
PACKAGE_NAME = "Gita Medical Hall ERP"

def get_script_path():
    """Get the directory where this script is located"""
    return os.path.dirname(os.path.abspath(__file__))

def clean_build_files():
    """Remove build files (build/, dist/, <package_name>/, *.spec)"""
    script_dir = get_script_path()
    
    print("Cleaning build files...")
    
    # Remove build folder
    build_dir = os.path.join(script_dir, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print("  ✓ Removed build/")
    
    # Remove dist folder
    dist_dir = os.path.join(script_dir, "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
        print("  ✓ Removed dist/")
    
    # Remove package folder
    pkg_dir = os.path.join(script_dir, PACKAGE_NAME)
    if os.path.exists(pkg_dir):
        shutil.rmtree(pkg_dir)
        print(f"  ✓ Removed {PACKAGE_NAME}/")
    
    # Remove spec file
    spec_file = os.path.join(script_dir, "Medicine_ERP.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print("  ✓ Removed Medicine_ERP.spec")
    
    print("Build files cleaned!")

def clean_pycache():
    """Remove __pycache__ folders"""
    script_dir = get_script_path()
    
    print("Cleaning Python cache...")
    
    for root, dirs, files in os.walk(script_dir):
        # Skip package folder
        if PACKAGE_NAME in root:
            continue
        
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path)
            print(f"  ✓ Removed {pycache_path}")
    
    print("Python cache cleaned!")

def clean_all():
    """Clean everything including distribution"""
    script_dir = get_script_path()
    
    print("Cleaning ALL files...")
    
    # Clean build files
    clean_build_files()
    
    # Clean pycache
    clean_pycache()
    
    print("All clean!")

def rebuild_executable():
    """Clean and rebuild the executable"""
    print("Rebuilding executable...")
    
    # Clean first
    clean_build_files()
    
    # Run PyInstaller
    os.system("python -m PyInstaller Medicine_ERP.spec")
    
    print("Rebuild complete!")

def create_dist_package():
    """Create the distribution package with all required files"""
    script_dir = get_script_path()
    dist_dir = os.path.join(script_dir, "dist")
    pkg_dir = os.path.join(script_dir, PACKAGE_NAME)
    
    print("Creating distribution package...")
    
    # Create package directory
    if os.path.exists(pkg_dir):
        print("  Removing existing package...")
        shutil.rmtree(pkg_dir)
    
    os.makedirs(pkg_dir)
    print(f"  ✓ Created {PACKAGE_NAME}/")
    
    # Copy executable
    exe_source = os.path.join(dist_dir, "Medicine_ERP.exe")
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, os.path.join(pkg_dir, "Medicine_ERP.exe"))
        print("  ✓ Copied Medicine_ERP.exe")
    else:
        print("  ✗ ERROR: Medicine_ERP.exe not found! Run build first.")
        return False
    
    # Copy logo
    logo_source = os.path.join(script_dir, "logo.ico")
    if os.path.exists(logo_source):
        shutil.copy2(logo_source, os.path.join(pkg_dir, "logo.ico"))
        print("  ✓ Copied logo.ico")
    
    # Copy data files
    data_source = os.path.join(script_dir, "data")
    data_dest = os.path.join(pkg_dir, "data")
    if os.path.exists(data_source):
        shutil.copytree(data_source, data_dest)
        print("  ✓ Copied data/")
    
    # Create README
    readme_content = """# Medicine ERP - Portable Package

This folder contains the portable version of Medicine ERP.

INSTRUCTIONS:
1. Copy this entire folder to your target PC
2. Run 'Medicine_ERP.exe' to start the application
3. No Python installation required on the target PC!

For data backup and clear, run: python backup_data.py
"""
    
    readme_path = os.path.join(pkg_dir, "README.txt")
    with open(readme_path, "w") as f:
        f.write(readme_content)
    print("  ✓ Created README.txt")
    
    print("\n✓ Distribution package created successfully!")
    print(f"Location: {pkg_dir}")
    
    return True

def main():
    print("=" * 70)
    print("         MEDICINE ERP - CLEANUP AND BUILD TOOLS")
    print("=" * 70)
    print()
    print("Select an option:")
    print("  1. Clean build files only")
    print("  2. Clean Python cache")
    print("  3. Clean ALL (build + cache + package)")
    print("  4. Rebuild executable")
    print("  5. Create distribution package")
    print("  6. Full rebuild (clean + rebuild + package)")
    print("  0. Exit")
    print()
    print("NOTE: For data backup and clear, run: python backup_data.py")
    print()
    
    choice = input("Enter option (0-6): ").strip()
    print()
    
    if choice == "1":
        clean_build_files()
    elif choice == "2":
        clean_pycache()
    elif choice == "3":
        clean_all()
    elif choice == "4":
        rebuild_executable()
    elif choice == "5":
        create_dist_package()
    elif choice == "6":
        clean_build_files()
        clean_pycache()
        rebuild_executable()
        create_dist_package()
    elif choice == "0":
        print("Exiting...")
    else:
        print("Invalid option!")

if __name__ == "__main__":
    main()
