import shutil


def check_dependencies() -> dict[str, bool]:
    """Return a dict of common external dependencies and whether they are available."""
    deps = {
        "wpctl": shutil.which("wpctl") is not None,
        "brightnessctl": shutil.which("brightnessctl") is not None,
        "grim": shutil.which("grim") is not None,
        "wl-clipboard": shutil.which("wl-clipboard") is not None,
        "wmctrl": shutil.which("wmctrl") is not None,
        "xdotool": shutil.which("xdotool") is not None,
        "gnome-screenshot": shutil.which("gnome-screenshot") is not None,
        "scrot": shutil.which("scrot") is not None,
    }
    return deps


def print_missing() -> None:
    deps = check_dependencies()
    missing = [name for name, present in deps.items() if not present]
    if not missing:
        print("[SetupHelper] All dependencies present")
    else:
        print("[SetupHelper] Missing dependencies: " + ", ".join(missing))

def list_dependencies() -> str:
    deps = check_dependencies()
    missing = [name for name, present in deps.items() if not present]
    if not missing:
        return "[SetupHelper] All dependencies present"
    return "[SetupHelper] Missing dependencies: " + ", ".join(missing)
