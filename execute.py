"""Initialize mcp2cli plugin — installs mcp2cli into the active environment."""
import subprocess
import sys
import shutil


def main():
    # Check if already available via uvx (zero-install path)
    if shutil.which("uvx"):
        print("uvx is available — mcp2cli can run via 'uvx mcp2cli' without a dedicated install.")

    # Install mcp2cli into current Python env for faster invocations
    print("Installing mcp2cli via pip...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet", "mcp2cli"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"pip install failed:\n{result.stderr}")
        if shutil.which("uvx"):
            print("Falling back to uvx — plugin will still work.")
            return 0
        return 1

    # Verify
    if shutil.which("mcp2cli"):
        ver = subprocess.run(["mcp2cli", "--version"], capture_output=True, text=True)
        print(f"mcp2cli installed successfully: {ver.stdout.strip()}")
    else:
        print("mcp2cli installed (may need shell restart to appear on PATH).")

    return 0


def uninstall_main():
    """Uninstall mcp2cli from the active Python environment."""
    print("Uninstalling mcp2cli via pip...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "--quiet", "-y", "mcp2cli"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"pip uninstall failed:\n{result.stderr}")
        return 1

    print("mcp2cli uninstalled successfully.")
    return 0



if __name__ == "__main__":
    sys.exit(main())
