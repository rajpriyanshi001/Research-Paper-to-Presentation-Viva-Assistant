"""
PaperMate AI - Model Management & Verification Module
Handles dynamic discovery of supported Gemini API models, generateContent filtering,
centralized model configuration, and live API connection verification.
"""

import time
import re
from typing import List, Tuple, Optional, Dict

DEFAULT_MODEL_CANDIDATE = "gemini-3.8-flash"

# Fallback candidates representing modern currently supported Gemini models
FALLBACK_SUPPORTED_MODELS = [
    "gemini-3.8-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite"
]

# In-memory session caches to eliminate duplicate API requests
_DISCOVERED_MODELS_CACHE: Dict[str, List[str]] = {}
_VERIFICATION_CACHE: Dict[Tuple[str, str], Tuple[bool, str, float]] = {}


def fetch_available_gemini_models(api_key: str, force_refresh: bool = False) -> List[str]:
    """
    Dynamically queries the Google Gen AI API using the provided API key
    to discover all models that support 'generateContent'.
    Caches results per API key so it is NOT called on every UI refresh.
    """
    if not api_key or not api_key.strip():
        return list(FALLBACK_SUPPORTED_MODELS)

    clean_key = api_key.strip()
    cache_key = clean_key[-10:] if len(clean_key) >= 10 else clean_key

    # Return cached discovery unless explicitly forced
    if not force_refresh and cache_key in _DISCOVERED_MODELS_CACHE:
        return list(_DISCOVERED_MODELS_CACHE[cache_key])

    models: List[str] = []

    # 1. Query via google.generativeai (Google AI Studio SDK)
    try:
        import google.generativeai as genai
        genai.configure(api_key=clean_key)
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", []) or []
            if "generateContent" in methods:
                name = m.name
                if name.startswith("models/"):
                    name = name[len("models/"):]
                name_lower = name.lower()
                # Exclude embedding and experimental non-generative endpoints
                if "embedding" not in name_lower and "aqa" not in name_lower and "imagen" not in name_lower:
                    models.append(name)
    except Exception:
        pass

    # 2. Query via google.genai if available and list is still empty
    if not models:
        try:
            from google import genai
            client = genai.Client(api_key=clean_key)
            for m in client.models.list():
                methods = getattr(m, "supported_generation_methods", []) or []
                name = getattr(m, "name", "") or getattr(m, "model", "")
                if name.startswith("models/"):
                    name = name[len("models/"):]
                name_lower = name.lower()
                if not methods or "generateContent" in methods:
                    if "embedding" not in name_lower and "aqa" not in name_lower and "imagen" not in name_lower:
                        models.append(name)
        except Exception:
            pass

    # 3. Clean and sort discovered models
    if models:
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for m in models:
            if m not in seen:
                seen.add(m)
                deduped.append(m)
        models = deduped

        # Ensure DEFAULT_MODEL_CANDIDATE is placed as the first option
        if DEFAULT_MODEL_CANDIDATE in models:
            models.remove(DEFAULT_MODEL_CANDIDATE)
            models.insert(0, DEFAULT_MODEL_CANDIDATE)
        else:
            models.insert(0, DEFAULT_MODEL_CANDIDATE)

        _DISCOVERED_MODELS_CACHE[cache_key] = models
        return list(models)

    # Fallback to modern supported models
    _DISCOVERED_MODELS_CACHE[cache_key] = list(FALLBACK_SUPPORTED_MODELS)
    return list(FALLBACK_SUPPORTED_MODELS)


def test_gemini_model_connection(api_key: str, model_name: str, force_test: bool = False) -> Tuple[bool, str, float]:
    """
    Performs a single, lightweight live API call to verify the model supports generateContent.
    Caches successful verifications to prevent repeated calls during UI reruns.
    Does NOT trigger duplicate secondary API calls on failure.
    """
    if not api_key or not api_key.strip():
        return False, "API key is missing or empty.", 0.0

    clean_key = api_key.strip()
    cache_key = (clean_key[-10:] if len(clean_key) >= 10 else clean_key, model_name)

    # Return cached verification if valid and not forcing a re-test
    if not force_test and cache_key in _VERIFICATION_CACHE:
        cached = _VERIFICATION_CACHE[cache_key]
        if cached[0]:  # Only reuse successful verifications from cache
            return cached

    start_time = time.time()

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage

        # Strict max_retries=1 prevents LangChain retry storms that burn the 5 RPM quota
        test_llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=clean_key,
            temperature=0.0,
            max_output_tokens=5,
            max_retries=1
        )
        response = test_llm.invoke([HumanMessage(content="Hi")])
        latency_ms = (time.time() - start_time) * 1000.0

        res_tuple = (True, f"Model '{model_name}' verified! generateContent active ({latency_ms:.0f}ms).", latency_ms)
        _VERIFICATION_CACHE[cache_key] = res_tuple
        return res_tuple

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000.0
        err_str = str(e)

        if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "quota" in err_str.lower():
            msg = f"Rate limit reached (Free tier 5 RPM). Please wait 15–30s before testing again."
        elif "404" in err_str or "not found" in err_str.lower():
            msg = f"Model '{model_name}' is not supported on this API key."
        elif "403" in err_str or "permission" in err_str.lower():
            msg = f"API key lacks permission for model '{model_name}'."
        elif "API_KEY_INVALID" in err_str or "invalid" in err_str.lower():
            msg = "Google Gemini API key is invalid or expired."
        else:
            msg = f"Verification failed: {err_str[:160]}"

        # Do NOT call a secondary fallback SDK, to prevent duplicate requests!
        return False, msg, latency_ms
