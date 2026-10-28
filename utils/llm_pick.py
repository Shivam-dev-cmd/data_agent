import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


# ============================================================
# PROVIDER CONFIGURATION
# ============================================================
# Set LLM_PROVIDER in .env to switch between providers.
# Default: "groq"

PROVIDER = os.environ.get("LLM_PROVIDER", "groq")

PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
}

# ============================================================
# MODEL MAPPINGS PER PROVIDER
# ============================================================
# Roles:
#   "low"    — Fast tasks: question curation, result summarization
#   "medium" — SQL generation, safety judge (needs structured_outputs)
#   "high"   — Complex reasoning
#   "coder"  — Python/Pandas code generation
#   "tool"   — Tool calling & structured output (routing, ETL tool binding)

MODELS = {
    "groq": {
        "low":    "openai/gpt-oss-20b",
        "medium": "openai/gpt-oss-120b",
        "high":   "openai/gpt-oss-120b",
        "coder":  "openai/gpt-oss-120b",
        "tool":   "openai/gpt-oss-120b",
    },
    "openrouter": {
        "low":    "meta-llama/llama-3.1-8b-instruct:free",
        "medium": "meta-llama/llama-3.3-70b-instruct:free",
        "high":   "qwen/qwen-2.5-coder-32b-instruct:free",
        "coder":  "qwen/qwen-2.5-coder-32b-instruct:free",
        "tool":   "meta-llama/llama-3.3-70b-instruct:free",
    },
}


def pick_llm(level: str):
    """
    Picks the appropriate LLM based on the task complexity level.

    Args:
        level (str): The complexity level - "low", "medium", "high", "coder", or "tool".

    Returns:
        ChatOpenAI: The LLM instance configured for the selected provider and model.

    Raises:
        ValueError: If the level is unsupported or the API key is missing.
    """
    if PROVIDER not in PROVIDERS:
        raise ValueError(f"Unsupported provider: {PROVIDER}. Choose from: {list(PROVIDERS.keys())}")

    provider_cfg = PROVIDERS[PROVIDER]
    model_name = MODELS.get(PROVIDER, {}).get(level.lower())

    if model_name is None:
        raise ValueError(
            f"Unsupported level: '{level}' for provider: '{PROVIDER}'. "
            f"Available levels: {list(MODELS[PROVIDER].keys())}"
        )

    # Resolve API key
    api_key_env = provider_cfg["api_key_env"]
    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        raise ValueError(
            f"Missing API key: set '{api_key_env}' in your .env file."
        )

    return ChatOpenAI(
        model=model_name,
        temperature=0,
        base_url=provider_cfg["base_url"],
        api_key=api_key,
    )


if __name__ == "__main__":
    llm_obj = pick_llm("low")
    print(llm_obj.invoke("What is the capital of France?"))
