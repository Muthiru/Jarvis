import json
import sys
from pathlib import Path

def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent

BASE_DIR    = get_base_dir()
CONFIG_DIR  = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "api_keys.json"

def ensure_config_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def config_exists() -> bool:
    return CONFIG_FILE.exists()

def save_api_keys(api_key: str, provider: str = "nvidia") -> None:
    ensure_config_dir()

    data: dict = {}
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {}

    provider = provider.strip().lower() or "nvidia"
    data["ai_provider"] = provider
    if provider == "nvidia":
        data["nvidia_api_key"] = api_key.strip()
        data.setdefault("nvidia_model", "nvidia/llama-3.3-nemotron-super-49b-v1.5")
    else:
        data["gemini_api_key"] = api_key.strip()

    CONFIG_FILE.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

def load_api_keys() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Failed to load api_keys.json: {e}")
        return {}

def get_gemini_key() -> str | None:
    return load_api_keys().get("gemini_api_key")

def get_nvidia_key() -> str | None:
    return load_api_keys().get("nvidia_api_key")

def is_configured() -> bool:
    data = load_api_keys()
    key = data.get("nvidia_api_key") or data.get("gemini_api_key")
    return bool(key and len(key) > 15)
