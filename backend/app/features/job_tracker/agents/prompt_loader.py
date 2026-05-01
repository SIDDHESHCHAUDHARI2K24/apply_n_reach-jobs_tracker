"""Load prompt and skill markdown files for agent nodes."""
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_SKILLS_DIR = Path(__file__).parent / "skills"


def load_prompt(name: str) -> str:
    """Load a prompt markdown file by name (without extension).

    Args:
        name: Prompt filename stem, e.g. 'node_1_extract'.

    Returns:
        The markdown content as a string.

    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
    """
    path = _PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def load_skill(name: str) -> str:
    """Load a skill markdown file by name (without extension).

    Args:
        name: Skill filename stem, e.g. 'refine_bullet_point'.

    Returns:
        The markdown content as a string.

    Raises:
        FileNotFoundError: If the skill file doesn't exist.
    """
    path = _SKILLS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Skill file not found: {path}")
    return path.read_text(encoding="utf-8")
