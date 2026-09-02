from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "__pycache__",
    ".aider.tags.cache.v4",
}

MAX_FILE_SIZE = 200_000


def is_ignored(path):
    return any(part in IGNORED_DIRECTORIES for part in path.parts)


def list_repository():
    """Return a sorted, read-only list of repository files."""

    files = []

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if is_ignored(path):
            continue

        files.append(str(path.relative_to(PROJECT_ROOT)))

    return sorted(files)


def read_file(relative_path):
    """Read one repository file in read-only mode."""

    path = (PROJECT_ROOT / relative_path).resolve()

    try:
        path.relative_to(PROJECT_ROOT)
    except ValueError:
        raise ValueError("Access outside the repository is not allowed.")

    if is_ignored(path):
        raise ValueError("Access to this path is not allowed.")

    if not path.is_file():
        raise FileNotFoundError(relative_path)

    if path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File is too large to inspect.")

    return path.read_text(encoding="utf-8", errors="replace")


def format_repository():
    """Return repository files as model-readable text."""

    files = list_repository()

    if not files:
        return "(repository contains no visible files)"

    return "\n".join(f"- {file}" for file in files)


if __name__ == "__main__":
    print(format_repository())