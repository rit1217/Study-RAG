import os


def load_prompt(agent_type, model, name, version="v02", prompts_dir="./prompts"):
    """Load a prompt from a .md file in the prompts directory.

    Args:
        agent_type: e.g. "legal_qa", "eval_scorer"
        model: e.g. "gemini-3-flash-preview"
        name: prompt name, e.g. "legal_qa", "legal_judgement_scorer"
        version: prompt version, e.g. "v02"
        prompts_dir: root directory for prompts

    Returns:
        Prompt text as string.
    """
    path = os.path.join(prompts_dir, agent_type, model, f"{name}_{version}.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
