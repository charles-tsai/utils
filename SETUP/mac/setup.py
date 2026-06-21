#!/usr/bin/env python3

import subprocess
import sys
import os

def run_cmd(cmd, check=True, capture_output=True, text=True, shell=False, env=None):
    """Utility to run a subprocess command."""
    try:
        result = subprocess.run(cmd, check=check, capture_output=capture_output, text=text, shell=shell, env=env)
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
        print("ERROR: Git is not installed. On macOS, you can install it by running 'xcode-select --install'. Please install git before running this setup script.")
        sys.exit(1)
    print("Git is installed.")

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
    print("Starting macOS Setup...")
    check_git()
    setup_homebrew()
    install_system_dependencies()
    switch_to_fish()
    setup_git_config()
    print("macOS Setup completed successfully!")

if __name__ == "__main__":
    main()
