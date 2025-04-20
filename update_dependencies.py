import sys
import os
import subprocess
import pkg_resources
import argparse
import re
from tabulate import tabulate
from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
import questionary
from packaging import version

try:
    from colorama import init, Fore, Style
except ImportError:
    print("Missing required dependencies. Installing now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

def get_installed_packages():
    """Get all installed packages and their versions"""
    installed_packages = [(d.project_name, d.version) for d in pkg_resources.working_set]
    return installed_packages

def get_latest_version(package_name):
    """Get the latest version of a package from PyPI"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "index", "versions", package_name],
            capture_output=True,
            text=True
        )
        match = re.search(r"Latest:\s+(\S+)", result.stdout)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        print(f"Error checking {package_name}: {e}")
        return None

def check_updates(packages_to_check=None):
    """Check for updates to installed packages"""
    installed = get_installed_packages()
    
    # Filter to specific packages if requested
    if packages_to_check:
        installed = [pkg for pkg in installed if pkg[0].lower() in [p.lower() for p in packages_to_check]]
    
    # Sort packages alphabetically
    installed.sort(key=lambda x: x[0].lower())
    
    console = Console()
    console.print("Checking for dependency updates...\n")
    
    updates_available = []
    with console.status("[bold green]Checking package versions...") as status:
        for i, (pkg_name, current_version) in enumerate(installed):
            status.update(f"[bold green]Checking {pkg_name} ({i+1}/{len(installed)})...")
            latest = get_latest_version(pkg_name)
            if latest and latest != current_version:
                try:
                    # Only add if the latest version is actually newer
                    if version.parse(latest) > version.parse(current_version):
                        updates_available.append((pkg_name, current_version, latest))
                except Exception:
                    # If version comparison fails, add it anyway
                    updates_available.append((pkg_name, current_version, latest))
    
    if not updates_available:
        console.print(Panel.fit("[bold green]All packages are up to date!", title="Dependency Check"))
        return []
    
    # Format the table
    table_data = [(i+1, pkg, curr, latest) for i, (pkg, curr, latest) in enumerate(updates_available)]
    print("\nUpdates available:")
    print(tabulate(table_data, headers=["#", "Package", "Current Version", "Latest Version"], tablefmt="grid"))
    
    return updates_available

def update_packages(packages_to_update):
    """Update selected packages"""
    if not packages_to_update:
        print("No packages selected for update.")
        return
    
    console = Console()
    
    # Create pip command with all packages to update
    update_cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    package_specs = []
    
    for pkg_name, _, latest_version in packages_to_update:
        # For the openai package, don't update beyond 0.28.x to maintain compatibility
        if pkg_name.lower() == "openai":
            # Find the latest 0.28.x version
            spec = f"{pkg_name}>=0.28.0,<0.29.0"
            console.print(f"[bold yellow]Note: Limiting {pkg_name} to v0.28.x for compatibility")
        # For Flask, stay within 2.x for compatibility
        elif pkg_name.lower() == "flask":
            spec = f"{pkg_name}>=2.0.1,<3.0.0"
            console.print(f"[bold yellow]Note: Limiting {pkg_name} to v2.x for compatibility")
        # For Werkzeug, stay compatible with Flask 2.x
        elif pkg_name.lower() == "werkzeug":
            spec = f"{pkg_name}>=2.0.1,<3.0.0"
            console.print(f"[bold yellow]Note: Limiting {pkg_name} to v2.x for Flask compatibility")
        else:
            spec = f"{pkg_name}=={latest_version}"
        
        package_specs.append(spec)
    
    update_cmd.extend(package_specs)
    
    console.print(f"\n[bold]Running: {' '.join(update_cmd)}")
    console.print(Panel.fit("[bold yellow]Updating packages. This may take a few minutes...", title="Update Progress"))
    
    result = subprocess.run(update_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        console.print(Panel.fit("[bold green]Packages updated successfully!", title="Update Complete"))
        return True
    else:
        console.print(Panel.fit(f"[bold red]Error updating packages:\n{result.stderr}", title="Update Failed"))
        return False

def main():
    # Define packages critical to the Solar Assistant app
    core_packages = [
        "flask", "werkzeug", "wtforms", "flask-wtf", "gunicorn", "openai", 
        "python-dotenv", "python-docx", "flask-limiter", "flask-talisman", 
        "markupsafe", "requests", "packaging", "pytest", "pyjwt", "bcrypt"
    ]
    
    # Check for updates to core packages
    updates_available = check_updates(core_packages)
    
    if not updates_available:
        return
    
    # Create choices for the questionary
    choices = [
        {
            "name": f"{pkg} ({curr} → {latest})",
            "value": (pkg, curr, latest),
            "checked": False  # Default to unchecked
        }
        for pkg, curr, latest in updates_available
    ]
    
    # Safe updates that won't break compatibility
    safe_packages = ["python-dotenv", "python-docx", "flask-talisman", "requests", "packaging"]
    
    # Pre-select safe packages
    for choice in choices:
        if choice["value"][0].lower() in safe_packages:
            choice["checked"] = True
    
    # Let user select packages to update
    selected = questionary.checkbox(
        "Select packages to update (space to select, enter to confirm):",
        choices=choices
    ).ask()
    
    if selected:
        update_packages(selected)
    else:
        print("No packages selected for update.")

if __name__ == "__main__":
    main()