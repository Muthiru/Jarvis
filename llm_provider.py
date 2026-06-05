import json
import sys
from pathlib import Path
from typing import Any


NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_NVIDIA_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1.5"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"


class LLMResponse:
    def __init__(self, text: str):
        self.text = text


class LLMModel:
    def __init__(self, model_name: str | None = None, system_instruction: str | None = None):
        self.model_name = model_name
        self.system_instruction = system_instruction

    def generate_content(self, contents: Any, **kwargs) -> LLMResponse:
        return generate_content(
            contents,
            model_name=self.model_name,
            system_instruction=self.system_instruction,
            **kwargs,
        )


def load_config() -> dict:
    if not API_CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(API_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_provider() -> str:
    config = load_config()
    provider = config.get("ai_provider", "").strip().lower()
    if provider:
        return provider
    if config.get("nvidia_api_key"):
        return "nvidia"
    return "gemini"


def get_api_key(provider: str | None = None) -> str:
    config = load_config()
    selected = (provider or get_provider()).strip().lower()
    if selected == "nvidia":
        return config.get("nvidia_api_key") or config.get("gemini_api_key", "")
    return config.get("gemini_api_key") or config.get("nvidia_api_key", "")


def get_text_model(model_name: str | None = None, system_instruction: str | None = None) -> LLMModel:
    return LLMModel(model_name=model_name, system_instruction=system_instruction)


def generate_text(
    prompt: Any,
    model_name: str | None = None,
    system_instruction: str | None = None,
    **kwargs,
) -> str:
    return generate_content(
        prompt,
        model_name=model_name,
        system_instruction=system_instruction,
        **kwargs,
    ).text


def generate_content(
    contents: Any,
    model_name: str | None = None,
    system_instruction: str | None = None,
    **kwargs,
) -> LLMResponse:
    provider = get_provider()
    if provider == "nvidia":
        return _nvidia_generate(contents, model_name, system_instruction, **kwargs)
    return _gemini_generate(contents, model_name, system_instruction, **kwargs)


def _gemini_generate(
    contents: Any,
    model_name: str | None,
    system_instruction: str | None,
    **kwargs,
) -> LLMResponse:
    import google.generativeai as genai

    api_key = get_api_key("gemini")
    if not api_key:
        raise RuntimeError("gemini_api_key is missing from config/api_keys.json")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name or DEFAULT_GEMINI_MODEL,
        system_instruction=system_instruction,
    )
    response = model.generate_content(contents, **kwargs)
    return LLMResponse((getattr(response, "text", "") or "").strip())


def _nvidia_generate(
    contents: Any,
    model_name: str | None,
    system_instruction: str | None,
    **kwargs,
) -> LLMResponse:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The NVIDIA provider requires the openai package. Run: pip install openai") from exc

    api_key = get_api_key("nvidia")
    if not api_key:
        raise RuntimeError("nvidia_api_key is missing from config/api_keys.json")

    config = load_config()
    client = OpenAI(
        base_url=config.get("nvidia_base_url", NVIDIA_BASE_URL),
        api_key=api_key,
    )

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": _contents_to_text(contents)})

    completion = client.chat.completions.create(
        model=config.get("nvidia_model") or model_name or DEFAULT_NVIDIA_MODEL,
        messages=messages,
        temperature=kwargs.get("temperature", 0.2),
    )
    text = completion.choices[0].message.content or ""
    return LLMResponse(text.strip())


def _contents_to_text(contents: Any) -> str:
    if isinstance(contents, str):
        return contents
    if isinstance(contents, list):
        parts: list[str] = []
        for item in contents:
            if isinstance(item, str):
                parts.append(item)
            else:
                raise RuntimeError("NVIDIA text models cannot process image or binary inputs.")
        return "\n\n".join(parts)
    return str(contents)
