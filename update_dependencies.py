import sys
import os
import subprocess
import pkg_resources
import argparse
try:
    import inquirer
    import requests
    from packaging import version
    from tabulate import tabulate
    from colorama import init, Fore, Style
except ImportError:
    print("Missing required dependencies. Installing now...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "inquirer", "requests", "packaging", "tabulate", "colorama"])
    import inquirer
    import requests
    from packaging import version
    from tabulate import tabulate
    from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

def get_latest_version(package_name):
    """Get the latest version of a package from PyPI"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        if response.status_code == 200:
            return response.json()["info"]["version"]
        return None
    except Exception:
        return None

def check_updates():
    """Check for updates to dependencies in requirements.txt"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    req_path = os.path.join(current_dir, "requirements.txt")
    
    # Check if requirements.txt exists
    if not os.path.exists(req_path):
        print(f"{Fore.RED}Error: requirements.txt not found.{Style.RESET_ALL}")
        return
    
    # Read requirements file
    with open(req_path, "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    updates_available = []
    errors = []
    
    # Parse requirements and check for updates
    for req in requirements:
        try:
            # Extract package name and version constraint
            if "==" in req:
                package_name, current_version = req.split("==")
            else:
                # For requirements without a specific version
                package_name = req.split(">=")[0].split(">")[0].split("<")[0].split("~=")[0].strip()
                try:
                    current_version = pkg_resources.get_distribution(package_name).version
                except:
                    errors.append(f"Package '{package_name}' not installed")
                    continue
            
            # Get latest version from PyPI
            latest_version = get_latest_version(package_name)
            
            if latest_version and version.parse(latest_version) > version.parse(current_version):
                updates_available.append({
                    "package": package_name,
                    "current": current_version,
                    "latest": latest_version
                })
        except Exception as e:
            errors.append(f"Error checking {req}: {str(e)}")
    
    return updates_available, errors

def update_packages(packages_to_update):
    """Update selected packages"""
    success = []
    failed = []
    
    for package in packages_to_update:
        package_name = package["package"]
        latest_version = package["latest"]
        
        print(f"{Fore.YELLOW}Updating {package_name} to {latest_version}...{Style.RESET_ALL}")
        
        try:
            # Run pip install with the new version
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                f"{package_name}=={latest_version}", "--upgrade"
            ])
            
            # Update requirements.txt
            update_requirements_file(package_name, latest_version)
            
            success.append(package_name)
        except Exception as e:
            failed.append(f"{package_name}: {str(e)}")
    
    return success, failed

def update_requirements_file(package_name, new_version):
    """Update the version of a package in requirements.txt"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    req_path = os.path.join(current_dir, "requirements.txt")
    
    with open(req_path, "r") as f:
        lines = f.readlines()
    
    with open(req_path, "w") as f:
        for line in lines:
            if line.strip().startswith(f"{package_name}=="):
                f.write(f"{package_name}=={new_version}\n")
            else:
                f.write(line)

def is_security_update(package, current_version, latest_version):
    """Determine if an update is likely security-related based on version pattern"""
    # For now, consider any patch version update potentially security-related
    current_parts = current_version.split('.')
    latest_parts = latest_version.split('.')
    
    # If major/minor versions differ, it's likely not just a security patch
    if len(current_parts) >= 2 and len(latest_parts) >= 2:
        if current_parts[0] != latest_parts[0] or current_parts[1] != latest_parts[1]:
            return False
    
    # Check against known vulnerable packages
    try:
        response = requests.get(
            f"https://pypi.org/pypi/{package}/json",
            timeout=5
        )
        if response.status_code == 200:
            releases = response.json().get("releases", {})
            if latest_version in releases:
                # Look for security-related keywords in release notes
                release_info = releases[latest_version]
                for item in release_info:
                    description = item.get("description", "").lower()
                    if any(keyword in description for keyword in ["security", "vulnerability", "cve", "fix", "exploit", "attack"]):
                        return True
    except Exception:
        # If we can't determine, err on the side of caution for security updates
        pass
        
    return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Check for dependency updates")
    parser.add_argument("--ci-mode", action="store_true", help="Run in CI mode (non-interactive)")
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}Checking for dependency updates...{Style.RESET_ALL}")
    
    updates_available, errors = check_updates()
    
    if errors:
        print(f"\n{Fore.RED}Errors encountered:{Style.RESET_ALL}")
        for error in errors:
            print(f"- {error}")
    
    if not updates_available:
        print(f"{Fore.GREEN}All dependencies are up to date!{Style.RESET_ALL}")
        return
    
    # Display available updates in a table
    print(f"\n{Fore.CYAN}Updates available:{Style.RESET_ALL}")
    
    table_data = []
    for i, pkg in enumerate(updates_available, 1):
        table_data.append([
            i, 
            pkg["package"], 
            pkg["current"], 
            pkg["latest"]
        ])
    
    print(tabulate(
        table_data,
        headers=["#", "Package", "Current Version", "Latest Version"],
        tablefmt="pretty"
    ))
    
    # In CI mode, just report findings and exit with appropriate status code
    if args.ci_mode:
        print(f"{Fore.YELLOW}Running in CI mode - not updating packages{Style.RESET_ALL}")
        security_updates = [p for p in updates_available if is_security_update(p["package"], p["current"], p["latest"])]
        
        if security_updates:
            print(f"{Fore.RED}Security updates available:{Style.RESET_ALL}")
            for pkg in security_updates:
                print(f"- {pkg['package']} ({pkg['current']} → {pkg['latest']})")
            sys.exit(1)  # Exit with error code to trigger notification in CI
        else:
            print(f"{Fore.GREEN}No urgent security updates required{Style.RESET_ALL}")
            sys.exit(0)
    
    # Interactive mode for user selection
    choices = [
        inquirer.Checkbox('packages',
                          message="Select packages to update (space to select, enter to confirm):",
                          choices=[(f"{pkg['package']} ({pkg['current']} → {pkg['latest']})", i) 
                                   for i, pkg in enumerate(updates_available)])
    ]
    
    answers = inquirer.prompt(choices)
    
    if not answers or not answers['packages']:
        print(f"{Fore.YELLOW}No packages selected for update.{Style.RESET_ALL}")
        return
    
    # Get selected packages
    selected_indices = answers['packages']
    selected_packages = [updates_available[i] for i in selected_indices]
    
    # Update selected packages
    success, failed = update_packages(selected_packages)
    
    if success:
        print(f"\n{Fore.GREEN}Successfully updated:{Style.RESET_ALL}")
        for pkg in success:
            print(f"- {pkg}")
    
    if failed:
        print(f"\n{Fore.RED}Failed to update:{Style.RESET_ALL}")
        for failure in failed:
            print(f"- {failure}")
    
    print(f"\n{Fore.CYAN}Update process completed.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()