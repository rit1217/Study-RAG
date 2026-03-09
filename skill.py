import os

from config import INSTRUCTION_ARCHIVE_DIR, INSTRUCTIONS_DIR


def load_instruction(group, name, instructions_dir=None):
    """Load an agent instruction from instructions/.

    Args:
        group: Instruction group, e.g. "legal_agentic" or "legal_rag".
        name: Instruction file name (without .md), e.g. "sc-query".
        instructions_dir: Override path. Defaults to config.INSTRUCTIONS_DIR.

    Returns:
        Instruction text as string.
    """
    instructions_dir = instructions_dir or INSTRUCTIONS_DIR
    path = os.path.join(instructions_dir, group, f"{name}.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_prompt(agent_type, name, version="v02", prompts_dir=None):
    """Load a versioned prompt from instruction_archive.

    Args:
        agent_type: e.g. "legal_qa", "eval_scorer"
        name: prompt name, e.g. "legal_qa", "legal_judgement_scorer"
        version: prompt version, e.g. "v02"
        prompts_dir: root directory for prompts. Defaults to config.INSTRUCTION_ARCHIVE_DIR.

    Returns:
        Prompt text as string.
    """
    prompts_dir = prompts_dir or INSTRUCTION_ARCHIVE_DIR
    path = os.path.join(prompts_dir, agent_type, f"{name}_{version}.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
