import os

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/nemotron-3-nano-30b-a3b"


def get_nvidia_api_key():
    key = os.environ.get("NVIDIA_API_KEY")

    if not key:
        raise RuntimeError(
            "NVIDIA_API_KEY is not set in the current PowerShell session."
        )

    return key
