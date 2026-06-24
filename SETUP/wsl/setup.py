#!/usr/bin/env python3

import subprocess
import sys
import os

# Add the parent directory of this script to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import run_cmd, is_command_installed, check_git, setup_git_config, install_golang, install_nodejs

def install_system_dependencies():
    """Install fish (via PPA), pip and curl."""
    print("Ensuring fish shell is up to date via PPA...")
    print("You may be prompted for your sudo password.")

    # Add fish PPA
    run_cmd(["sudo", "apt-add-repository", "-y", "ppa:fish-shell/release-3"], capture_output=False)
    run_cmd(["sudo", "apt-get", "update"], capture_output=False)

    # Install or upgrade fish, and ensure pip3 and curl are installed
    run_cmd(["sudo", "apt-get", "install", "-y", "fish", "python3-pip", "curl"], capture_output=False)

def switch_to_fish():
    """Switch default shell to fish for the current user."""
    print("Checking default shell...")
    user = os.environ.get("USER")
    if not user:
        print("Could not determine user from $USER. Skipping shell change.")
        return

    # Check current shell in /etc/passwd
    # Format: username:x:uid:gid:comment:home:shell
    try:
        with open("/etc/passwd", "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) >= 7 and parts[0] == user:
                    current_shell = parts[6]
                    if current_shell.endswith("fish"):
                        print("fish is already the default shell. Skipping.")
                        return
                    break
    except Exception as e:
        print(f"Warning: Could not read /etc/passwd: {e}")

    # Find the path to the fish executable
    fish_path_result = run_cmd(["which", "fish"], capture_output=True)
    fish_path = fish_path_result.stdout.strip()

    if not fish_path:
        print("ERROR: Could not find fish path. Shell change failed.")
        sys.exit(1)

    print(f"Changing default shell to {fish_path} for user {user}...")
    # This might ask for a password
    run_cmd(["sudo", "chsh", "-s", fish_path, user], capture_output=False)
    print("Shell changed successfully. You may need to log out and log back in for changes to take effect.")

def main():
    print("Starting WSL Setup...")
    check_git()
    install_system_dependencies()
    switch_to_fish()
    setup_git_config()
    install_golang()
    install_nodejs()
    print("WSL Setup completed successfully!")

if __name__ == "__main__":
    main()
