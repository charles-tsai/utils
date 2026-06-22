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
        if sys.platform == 'darwin':
            print("ERROR: Git is not installed. On macOS, you can install it by running 'xcode-select --install'. Please install git before running this setup script.")
        else:
            print("ERROR: Git is not installed. Please install git before running this setup script.")
        sys.exit(1)
    print("Git is installed.")

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
