"""
Minimal Gemini chat (terminal REPL)
- Reads GOOGLE_API_KEY from .env
- No system prompts; behaves like a plain chat
- Streams responses token-by-token when available

Usage:
  python gemini_chat.py

Type 'exit' or 'quit' to leave.
"""
import os
import sys
import time
from typing import Optional

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

try:
    import google.generativeai as genai
except Exception as e:  # pragma: no cover
    print("Error: google-generativeai is not installed in this environment.")
    print("Fix: activate your venv and install requirements, e.g.\n  pip install google-generativeai python-dotenv")
    sys.exit(1)


def _configure_from_env() -> Optional[str]:
    """Load .env and configure the Gemini client. Returns model name or None on failure."""
    if load_dotenv:
        load_dotenv()

    # Prefer GEMINI_API_KEY, fallback to GOOGLE_API_KEY
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Missing GEMINI_API_KEY/GOOGLE_API_KEY in environment.")
        print("- Add GEMINI_API_KEY=AIza... to your .env file (from Google AI Studio)")
        return None
    if not api_key.startswith("AIza"):
        print("It looks like your Gemini API key is not in the expected 'AIza' format.")
        print("Use a simple API key from Google AI Studio, not a service account JSON.")
        return None

    try:
        genai.configure(api_key=api_key)
    except Exception as e:  # pragma: no cover
        print(f"Failed to configure Google AI client: {e}")
        return None

    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
    return model_name


def _print_header(model_name: str) -> None:
    print("\n==========================================")
    print("  Gemini Chat — minimal terminal client  ")
    print("==========================================")
    print(f"Model: {model_name}")
    print("Type 'exit' or 'quit' to end the session.\n")


def _stream_response(resp) -> None:
    """Stream response chunks safely if streaming is enabled."""
    first = True
    try:
        for chunk in resp:
            text = getattr(chunk, "text", None)
            if text:
                if first:
                    print("Gemini:", end=" ", flush=True)
                    first = False
                print(text, end="", flush=True)
        if not first:
            print()  # newline after streaming
    except TypeError:
        # Not a stream; print normally
        try:
            text = getattr(resp, "text", None)
            if text:
                print("Gemini:", text)
            else:
                print("Gemini: [no text in response]")
        except Exception as e:
            print(f"Gemini: [error reading response: {e}]")


def main() -> int:
    model_name = _configure_from_env()
    if not model_name:
        return 1

    try:
        # Preflight: ensure model supports generateContent, pick fallback if needed
        try:
            available = list(genai.list_models())
        except Exception:
            available = []
        def _strip_models_prefix(name: str) -> str:
            return name.split("/", 1)[1] if name and name.startswith("models/") else name
        supported = []
        for m in available:
            methods = getattr(m, "supported_generation_methods", []) or []
            if "generateContent" in methods or "generate_content" in methods:
                supported.append(_strip_models_prefix(getattr(m, "name", "")))
        chosen = model_name
        if supported and _strip_models_prefix(model_name) not in supported:
            fallback = next((m for m in supported if "flash" in m), None) or next((m for m in supported if "pro" in m), None)
            if fallback:
                print(f"Auto-selecting available model: {fallback}")
                chosen = fallback
        model = genai.GenerativeModel(chosen)
        chat = model.start_chat(history=[])
    except Exception as e:
        # Try to auto-select a compatible model by listing models
        print("Failed to initialize Gemini model/chat:", e)
        try:
            available = list(genai.list_models())
            def _strip_models_prefix(name: str) -> str:
                return name.split("/", 1)[1] if name and name.startswith("models/") else name
            supported = []
            for m in available:
                methods = getattr(m, "supported_generation_methods", []) or []
                if "generateContent" in methods or "generate_content" in methods:
                    supported.append(_strip_models_prefix(getattr(m, "name", "")))
            fallback = next((m for m in supported if "flash" in m), None) or next((m for m in supported if "pro" in m), None)
            if not fallback:
                print("No compatible Gemini models with generateContent found for this API key.")
                return 1
            print(f"Auto-selecting available model: {fallback}")
            model = genai.GenerativeModel(fallback)
            chat = model.start_chat(history=[])
        except Exception as e2:
            print("Could not auto-select a model:", e2)
            print("- Ensure your Generative Language API is enabled and your key has access to Gemini models.")
            return 1

    _print_header(model_name)

    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting…")
            return 0

        if user.lower() in {"exit", "quit"}:
            print("Goodbye!")
            return 0
        if not user:
            continue

        try:
            # Stream the response when possible
            resp = chat.send_message(user, stream=True)
            _stream_response(resp)
        except Exception as e:
            msg = str(e)
            if "API key" in msg or "PermissionDenied" in msg or "Request had insufficient authentication" in msg:
                print("Authentication error. Double-check GEMINI_API_KEY/GOOGLE_API_KEY in your .env.")
                print("- It must be a simple API key (starts with AIza) from Google AI Studio.")
            else:
                print("Error from Gemini:", e)


if __name__ == "__main__":
    sys.exit(main())
