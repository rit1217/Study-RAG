import os

from config import SKILLS_DIR, SKILL_ARCHIVE_DIR


def load_skill(group, name, skills_dir=None):
    """Load the current best skill from .claude/skills/.

    Args:
        group: Skill group, e.g. "legal_agentic" or "legal_rag".
        name: Skill directory name, e.g. "general-law-query".
        skills_dir: Override path. Defaults to config.SKILLS_DIR.

    Returns:
        Skill prompt text (SKILL.md body, without YAML frontmatter).
    """
    skills_dir = skills_dir or SKILLS_DIR
    path = os.path.join(skills_dir, group, name, "SKILL.md")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # Strip YAML frontmatter (between --- markers)
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:].strip()

    return content


def load_prompt(agent_type, model, name, version="v02", prompts_dir=None):
    """Load a versioned prompt from skill_archive (backward compatibility).

    Args:
        agent_type: e.g. "legal_qa", "eval_scorer"
        model: e.g. "gemini-3-flash-preview"
        name: prompt name, e.g. "legal_qa", "legal_judgement_scorer"
        version: prompt version, e.g. "v02"
        prompts_dir: root directory for prompts. Defaults to config.SKILL_ARCHIVE_DIR.

    Returns:
        Prompt text as string.
    """
    prompts_dir = prompts_dir or SKILL_ARCHIVE_DIR
    path = os.path.join(prompts_dir, agent_type, model, f"{name}_{version}.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
