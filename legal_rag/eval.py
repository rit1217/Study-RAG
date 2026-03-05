from autoevals import LLMClassifier

from skill import load_prompt


def create_legal_reference_scorer(model="gemini-3-flash-preview", version="v02"):
    return LLMClassifier(
        name="1. Reference",
        model=model,
        prompt_template=load_prompt("eval_scorer", model, "legal_reference_scorer", version),
        choice_scores={
            "อ้างอิงมาตรากฎหมายถูกต้องและครอบคลุมตามเฉลย": 1.0,
            "อ้างอิงมาตรากฎหมายไม่ถูกต้อง หรือไม่เกี่ยวข้อง": 0.0,
            "อ้างอิงมาตรากฎหมายถูกต้อง แต่ไม่ครอบคลุม มีมาตราสำคัญตกหล่น": 0.5,
        },
        extra_body={"tool_choice": "auto"},
        max_tokens=None,
    )


def create_legal_judgement_scorer(model="gemini-3-flash-preview", version="v02"):
    return LLMClassifier(
        name="2. Judgement",
        model=model,
        prompt_template=load_prompt("eval_scorer", model, "legal_judgement_scorer", version),
        choice_scores={
            "ตอบได้ถูกต้อง ชัดเจน ครอบคลุม": 1.0,
            "ไม่ถูกต้องตามเฉลย": 0.0,
            "ตอบได้ถูกต้อง แต่ไม่ครอบคลุม มีเนื้อหาสำคัญตกหล่น": 0.5,
        },
        extra_body={"tool_choice": "auto"},
        max_tokens=None,
    )


def create_legal_suggestion_scorer(model="gemini-3-flash-preview", version="v02"):
    return LLMClassifier(
        name="3. Conclusion & Suggestion",
        model=model,
        prompt_template=load_prompt("eval_scorer", model, "legal_suggestion_scorer", version),
        choice_scores={
            "ตอบได้ถูกต้อง ชัดเจน ครอบคลุม ให้ข้อเสนอแนะที่เป็นไปได้จริง": 1.0,
            "ไม่ถูกต้องตามเฉลย": 0.0,
            "ตอบได้ถูกต้อง แต่ไม่ครอบคลุม มีเนื้อหาสำคัญตกหล่น": 0.5,
        },
        extra_body={"tool_choice": "auto"},
        max_tokens=None,
    )


def create_gemini_distance_scorer(model="gemini-3-flash-preview", version="v02"):
    return LLMClassifier(
        name="Gemini Embedding Similarity",
        model=model,
        prompt_template=load_prompt("eval_scorer", model, "gemini_distance", version),
        choice_scores={
            "Identical Meaning": 1.0,
            "Minor Deviations": 0.8,
            "Major Deviations": 0.4,
            "Unrelated": 0.0,
        },
        extra_body={"tool_choice": "auto"},
        max_tokens=None,
    )


def create_gemini_sim_scorer(model="gemini-3-flash-preview", version="v02"):
    return LLMClassifier(
        name="Gemini Answer Similarity",
        model=model,
        prompt_template=load_prompt("eval_scorer", model, "gemini_answer_similarity", version),
        choice_scores={
            "Equivalent": 1.0,
            "Mostly Similar": 0.7,
            "Partially Similar": 0.3,
            "Different": 0.0,
        },
        extra_body={"tool_choice": "auto"},
        max_tokens=None,
    )


def create_gemini_fact_scorer(model="gemini-3-flash-preview", version="v02"):
    return LLMClassifier(
        name="Gemini Factuality",
        model=model,
        prompt_template=load_prompt("eval_scorer", model, "gemini_factuality", version),
        choice_scores={
            "A": 0.4,
            "B": 0.6,
            "C": 1,
            "D": 0,
            "E": 1,
        },
        use_cot=True,
        description="Test whether an output is factual, compared to an original (`expected`) value.",
        extra_body={"tool_choice": "none"},
        max_tokens=None,
    )
