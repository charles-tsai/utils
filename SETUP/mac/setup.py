#!/usr/bin/env python3

import subprocess
import sys
import os

# Add the parent directory of this script to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import run_cmd, is_command_installed, check_git, setup_git_config, install_golang, install_nodejs

def setup_homebrew():
    """Check and install Homebrew if missing."""
    print("Checking for Homebrew...")
    if not is_command_installed("brew"):
        print("Homebrew is not installed. Installing Homebrew non-interactively...")
        env = os.environ.copy()
        env["NONINTERACTIVE"] = "1"
        install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        run_cmd(install_cmd, shell=True, capture_output=False, env=env)

        # After installation on Apple Silicon, brew might not be in PATH immediately for this script
        if os.path.exists("/opt/homebrew/bin/brew"):
            os.environ["PATH"] = f"/opt/homebrew/bin:{os.environ['PATH']}"
        elif os.path.exists("/usr/local/bin/brew"):
            os.environ["PATH"] = f"/usr/local/bin:{os.environ['PATH']}"

        print("Homebrew installation completed.")
    else:
        print("Homebrew is installed.")

def install_system_dependencies():
    """Install fish and python (which includes pip3) if they are not already installed via brew."""
    packages_to_install = []

    if not is_command_installed("fish"):
        packages_to_install.append("fish")
    else:
        print("fish shell is already installed. Skipping.")

    if not is_command_installed("pip3"):
        packages_to_install.append("python")
    else:
        print("pip3 is already installed. Skipping.")

    if packages_to_install:
        print(f"Installing missing packages via Homebrew: {', '.join(packages_to_install)}")
        run_cmd(["brew", "update"], capture_output=False)
        run_cmd(["brew", "install"] + packages_to_install, capture_output=False)
    else:
        print("System dependencies already installed.")

def switch_to_fish():
    """Switch default shell to fish for the current user."""
    print("Checking default shell...")
    user = os.environ.get("USER")
    if not user:
        print("Could not determine user from $USER. Skipping shell change.")
        return

    # Find the path to the fish executable
    fish_path_result = run_cmd(["which", "fish"], capture_output=True)
    fish_path = fish_path_result.stdout.strip()

    if not fish_path:
        print("ERROR: Could not find fish path. Shell change failed.")
        sys.exit(1)

    # Check if fish is currently the default shell
    current_shell_result = run_cmd(["dscl", ".", "-read", f"/Users/{user}", "UserShell"], capture_output=True, check=False)
    if current_shell_result.returncode == 0:
        if fish_path in current_shell_result.stdout:
            print(f"fish ({fish_path}) is already the default shell. Skipping.")
            return

    # Check if fish is in /etc/shells, if not, append it
    try:
        with open("/etc/shells", "r") as f:
            shells = f.read()
    except Exception as e:
        print(f"Warning: Could not read /etc/shells: {e}")
        shells = ""

    if fish_path not in shells:
        print(f"Adding {fish_path} to /etc/shells. You may be prompted for your sudo password.")
        append_cmd = f"echo {fish_path} | sudo tee -a /etc/shells"
        run_cmd(append_cmd, shell=True, capture_output=False)
        print(f"Added {fish_path} to /etc/shells.")

    print(f"Changing default shell to {fish_path} for user {user}...")
    # This might ask for a password
    run_cmd(["chsh", "-s", fish_path], capture_output=False)
    print("Shell changed successfully. You may need to log out and log back in, or open a new terminal tab, for changes to take effect.")

def main():
    print("Starting macOS Setup...")
    check_git()
    setup_homebrew()
    install_system_dependencies()
    switch_to_fish()
    setup_git_config()
    install_golang()
    install_nodejs()
    print("macOS Setup completed successfully!")

if __name__ == "__main__":
    main()
