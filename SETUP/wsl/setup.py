#!/usr/bin/env python3

import subprocess
import sys
import os

def run_cmd(cmd, check=True, capture_output=True, text=True, shell=False):
    """Utility to run a subprocess command."""
    try:
        result = subprocess.run(cmd, check=check, capture_output=capture_output, text=text, shell=shell)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def is_command_installed(cmd_name):
    """Check if a command exists in the system."""
    result = subprocess.run(["which", cmd_name], capture_output=True, text=True)
    return result.returncode == 0

def check_git():
    """Fail fast if Git is not installed."""
    print("Checking for Git...")
    if not is_command_installed("git"):
        print("ERROR: Git is not installed. Please install git before running this setup script.")
        sys.exit(1)
    print("Git is installed.")

def install_system_dependencies():
    """Install fish and pip if they are not already installed."""
    packages_to_install = []

    if not is_command_installed("fish"):
        packages_to_install.append("fish")
    else:
        print("fish shell is already installed. Skipping.")

    if not is_command_installed("pip3"):
        packages_to_install.append("python3-pip")
    else:
        print("pip3 is already installed. Skipping.")

    if packages_to_install:
        print(f"Installing missing packages: {', '.join(packages_to_install)}")
        print("You may be prompted for your sudo password.")
        run_cmd(["sudo", "apt-get", "update"], capture_output=False)
        run_cmd(["sudo", "apt-get", "install", "-y"] + packages_to_install, capture_output=False)
    else:
        print("System dependencies already installed.")

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

def setup_git_config():
    """Set up global Git configuration if not already set."""
    print("Configuring global Git settings...")

    expected_email = "weichetsai@gmail.com"
    expected_name = "charlestsai"

    # Check Email
    current_email_result = run_cmd(["git", "config", "--global", "user.email"], check=False)
    if current_email_result.returncode != 0 or current_email_result.stdout.strip() != expected_email:
        print(f"Setting git global user.email to {expected_email}...")
        run_cmd(["git", "config", "--global", "user.email", expected_email])
    else:
        print(f"Git user.email is already set to {expected_email}. Skipping.")

    # Check Name
    current_name_result = run_cmd(["git", "config", "--global", "user.name"], check=False)
    if current_name_result.returncode != 0 or current_name_result.stdout.strip() != expected_name:
        print(f"Setting git global user.name to {expected_name}...")
        run_cmd(["git", "config", "--global", "user.name", expected_name])
    else:
        print(f"Git user.name is already set to {expected_name}. Skipping.")

def main():
    print("Starting WSL Setup...")
    check_git()
    install_system_dependencies()
    switch_to_fish()
    setup_git_config()
    print("WSL Setup completed successfully!")

if __name__ == "__main__":
    main()
