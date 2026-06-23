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

def update_fish():
    """Update fish shell to the latest version using PPA on Linux."""
    import platform
    system = platform.system().lower()
    if system == "linux":
        print("Updating fish shell via PPA...")
        run_cmd(["sudo", "apt-add-repository", "-y", "ppa:fish-shell/release-3"], capture_output=False)
        run_cmd(["sudo", "apt", "update"], capture_output=False)
        run_cmd(["sudo", "apt", "install", "-y", "fish"], capture_output=False)
    elif system == "darwin":
        print("Updating fish shell via Homebrew...")
        run_cmd(["brew", "upgrade", "fish"], capture_output=False, check=False)
    else:
        print(f"Unsupported OS for automatic fish update: {system}")

def install_golang():
    """Install or update Golang to the latest version in ~/develop/bin."""
    print("Checking for Golang updates...")
    import urllib.request
    import platform
    import tarfile
    import shutil

    # Get latest version
    try:
        req = urllib.request.Request("https://go.dev/VERSION?m=text")
        with urllib.request.urlopen(req) as response:
            latest_version = response.read().decode('utf-8').splitlines()[0].strip()
    except Exception as e:
        print(f"Failed to fetch latest Go version: {e}")
        return

    # Determine OS and Arch
    system = platform.system().lower()
    if system == "darwin":
        go_os = "darwin"
    elif system == "linux":
        go_os = "linux"
    else:
        print(f"Unsupported OS for automatic Go installation: {system}")
        return

    machine = platform.machine().lower()
    if machine in ["x86_64", "amd64"]:
        go_arch = "amd64"
    elif machine in ["arm64", "aarch64"]:
        go_arch = "arm64"
    else:
        print(f"Unsupported architecture for automatic Go installation: {machine}")
        return

    target_dir = os.path.expanduser("~/develop/bin")
    go_dir = os.path.join(target_dir, "go")
    go_bin = os.path.join(go_dir, "bin", "go")

    # Check current version
    current_version = None
    if os.path.exists(go_bin):
        result = run_cmd([go_bin, "version"], check=False, capture_output=True)
        if result.returncode == 0:
            # Expected output format: go version go1.21.0 linux/amd64
            parts = result.stdout.strip().split()
            if len(parts) >= 3:
                current_version = parts[2]

    if current_version == latest_version:
        print(f"Golang is already up-to-date ({current_version}) in {go_dir}. Skipping.")
    else:
        if current_version:
            print(f"Updating Golang from {current_version} to {latest_version}...")
        else:
            print(f"Installing Golang {latest_version}...")

        # Download and extract
        filename = f"{latest_version}.{go_os}-{go_arch}.tar.gz"
        download_url = f"https://go.dev/dl/{filename}"
        download_path = os.path.join("/tmp", filename)

        print(f"Downloading {download_url}...")
        try:
            urllib.request.urlretrieve(download_url, download_path)
        except Exception as e:
            print(f"Failed to download Go: {e}")
            return

        os.makedirs(target_dir, exist_ok=True)
        if os.path.exists(go_dir):
            shutil.rmtree(go_dir)

        print(f"Extracting to {target_dir}...")
        try:
            with tarfile.open(download_path, "r:gz") as tar:
                tar.extractall(path=target_dir)
        except Exception as e:
            print(f"Failed to extract Go: {e}")
            return
        finally:
            if os.path.exists(download_path):
                os.remove(download_path)

        print(f"Successfully installed {latest_version} to {go_dir}")

        # Verify installation
        if os.path.exists(go_bin):
            run_cmd([go_bin, "version"], capture_output=False)

    # Add to fish shell path
    fish_config_dir = os.path.expanduser("~/.config/fish")
    fish_config_file = os.path.join(fish_config_dir, "config.fish")

    os.makedirs(fish_config_dir, exist_ok=True)

    path_command = f"fish_add_path {os.path.join(go_dir, 'bin')}"

    path_exists = False
    if os.path.exists(fish_config_file):
        with open(fish_config_file, "r") as f:
            if path_command in f.read():
                path_exists = True

    if not path_exists:
        print(f"Adding Go to fish path in {fish_config_file}...")
        with open(fish_config_file, "a") as f:
            f.write(f"\n# Add Go to path\n{path_command}\n")
    else:
        print("Go path is already in fish config.")
