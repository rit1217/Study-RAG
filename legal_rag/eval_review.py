import glob
import json
import os
import re
from dataclasses import dataclass, field

from google import genai

from legal_rag.eval import (
    create_legal_reference_scorer,
    create_legal_judgement_scorer,
    create_legal_suggestion_scorer,
)
from legal_rag.prompts import load_prompt


# ── Data classes ─────────────────────────────────────────────

@dataclass
class ScorerResult:
    """Result from re-running a single scorer on one entry."""
    scorer_name: str
    score: float
    choice: str
    rationale: str


@dataclass
class EntryReview:
    """Complete review for a single eval entry."""
    index: int
    input: str
    output: str
    expected: str
    scorer_results: list[ScorerResult]
    human_scores: dict[str, float]
    human_feedback: str
    auto_scores: dict[str, float]
    source_file: str = ""
    score_diff: dict[str, float] = field(default_factory=dict)
    discrepancy_summary: str = ""


@dataclass
class ReviewReport:
    """Full review report across all entries."""
    entries: list[EntryReview]
    overall_score_analysis: str = ""
    prompt_suggestions: dict[str, str] = field(default_factory=dict)


# ── Mappings ─────────────────────────────────────────────────

# Raw Braintrust JSON keys → simplified keys
AUTO_SCORE_MAP = {
    "1. Reference": "reference",
    "2. Judgement": "judgement",
    "3. Conclusion & Suggestion": "suggestion",
}

HUMAN_SCORE_MAP = {
    "Human: Reference": "reference",
    "Human: Judgement": "judgement",
    "Human: Summary & Suggestion": "suggestion",
}

# Simplified key → scorer factory function
SCORER_FACTORIES = {
    "reference": create_legal_reference_scorer,
    "judgement": create_legal_judgement_scorer,
    "suggestion": create_legal_suggestion_scorer,
}

# Simplified key → scorer prompt file name (without version suffix)
SCORER_PROMPT_NAMES = {
    "reference": "legal_reference_scorer",
    "judgement": "legal_judgement_scorer",
    "suggestion": "legal_suggestion_scorer",
}


# ── Main class ───────────────────────────────────────────────

class EvalReviewClient:
    """Review and analyze evaluation results, comparing human vs auto scores."""

    def __init__(
        self,
        api_key=None,
        eval_model="gemini-3-pro-preview",
        review_model="gemini-3-pro-preview",
        prompt_version="v01",
        eval_prompt_version="v02",
        prompts_dir="./prompts",
    ):
        """Initialize the review client.

        Args:
            api_key: Gemini API key. If None, reads from GEMINI_API_KEY env var.
            eval_model: Model for re-running scorers via autoevals.
            review_model: Model for meta-analysis (summarization, suggestions).
            prompt_version: Version for review prompts.
            eval_prompt_version: Version for eval scorer prompts.
            prompts_dir: Root directory for prompt template files.
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.eval_model = eval_model
        self.review_model = review_model
        self.prompt_version = prompt_version
        self.eval_prompt_version = eval_prompt_version
        self.prompts_dir = prompts_dir

    # ── Load and convert eval results ────────────────────────────

    @staticmethod
    def load_eval_json(json_path):
        """Load raw Braintrust eval JSON and convert to simplified dict format.

        Args:
            json_path: Path to the eval results JSON file.

        Returns:
            list[dict] with keys: input, output, expected,
            auto_scores, human_scores, human_feedback.
        """
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        data = []
        for entry in raw:
            scores = entry.get("scores", {})

            auto_scores = {
                simplified: scores.get(raw_key)
                for raw_key, simplified in AUTO_SCORE_MAP.items()
            }
            human_scores = {
                simplified: scores.get(raw_key)
                for raw_key, simplified in HUMAN_SCORE_MAP.items()
            }

            # Skip entries where any human score is None (ungraded)
            if any(v is None for v in human_scores.values()):
                continue

            data.append({
                "input": entry.get("input", ""),
                "output": entry.get("output", ""),
                "expected": entry.get("expected", ""),
                "auto_scores": auto_scores,
                "human_scores": human_scores,
                "human_feedback": entry.get("metadata", {}).get("Human: Feedback", ""),
            })

        return data

    @staticmethod
    def load_eval_folder(folder_path):
        """Load all eval JSON files from a folder and merge into one list.

        Each entry gets an extra ``source_file`` key with the basename of
        the originating file so results can be traced back.

        Args:
            folder_path: Path to a directory containing eval result JSON files.

        Returns:
            list[dict] – same format as ``load_eval_json``, with an added
            ``source_file`` key per entry.
        """
        json_files = sorted(glob.glob(os.path.join(folder_path, "*.json")))
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in {folder_path}")

        all_data = []
        for path in json_files:
            entries = EvalReviewClient.load_eval_json(path)
            basename = os.path.splitext(os.path.basename(path))[0]
            for entry in entries:
                entry["source_file"] = basename
            all_data.extend(entries)
            print(f"  Loaded {len(entries)} entries from {basename}")

        print(f"\nTotal: {len(all_data)} entries from {len(json_files)} files")
        return all_data

    # ── Re-run scorers with rationale ────────────────────────────

    def rerun_scorers(self, data, scorer_names=None):
        """Re-run legal scorers on each entry, capturing score, choice, and rationale.

        Args:
            data: list[dict] in simplified format.
            scorer_names: List of scorer keys to run. Defaults to all three:
                ["reference", "judgement", "suggestion"].

        Returns:
            list[EntryReview] with scorer_results populated.
        """
        if scorer_names is None:
            scorer_names = list(SCORER_FACTORIES.keys())

        scorers = {
            name: SCORER_FACTORIES[name](
                model=self.eval_model,
                version=self.eval_prompt_version,
            )
            for name in scorer_names
        }

        reviews = []
        for i, entry in enumerate(data):
            scorer_results = []
            for name, scorer in scorers.items():
                result = scorer(output=entry["output"], expected=entry["expected"])
                scorer_results.append(ScorerResult(
                    scorer_name=name,
                    score=result.score if result.score is not None else 0.0,
                    choice=result.metadata.get("choice", "") if result.metadata else "",
                    rationale=result.metadata.get("rationale", "") if result.metadata else "",
                ))
                print(f"  [{i+1}/{len(data)}] {name}: {result.score}")

            score_diff = {}
            for name in scorer_names:
                auto = entry["auto_scores"].get(name)
                human = entry["human_scores"].get(name)
                if auto is not None and human is not None:
                    score_diff[name] = auto - human
                else:
                    score_diff[name] = None

            reviews.append(EntryReview(
                index=i,
                input=entry["input"],
                output=entry["output"],
                expected=entry["expected"],
                scorer_results=scorer_results,
                human_scores=entry["human_scores"],
                human_feedback=entry["human_feedback"],
                auto_scores=entry["auto_scores"],
                source_file=entry.get("source_file", ""),
                score_diff=score_diff,
            ))

        return reviews

    # ── Summarize human-vs-auto discrepancies ────────────────────

    def summarize_discrepancies(self, reviews):
        """For each entry, compare human feedback vs auto rationale using Gemini.

        Args:
            reviews: list[EntryReview] with scorer_results populated.

        Returns:
            Same list with discrepancy_summary populated.
        """
        prompt_template = load_prompt(
            "eval_review", self.review_model, "discrepancy_summary",
            self.prompt_version, self.prompts_dir,
        )

        for i, review in enumerate(reviews):
            sections = []
            for sr in review.scorer_results:
                human_feedback_section = self._extract_feedback_section(
                    review.human_feedback, sr.scorer_name,
                )
                human_score = review.human_scores.get(sr.scorer_name, "N/A")
                auto_score = review.auto_scores.get(sr.scorer_name, "N/A")

                sections.append(
                    f"### {sr.scorer_name}\n"
                    f"- Human Score: {human_score}\n"
                    f"- Auto Score: {auto_score}\n"
                    f"- Human Feedback: {human_feedback_section}\n"
                    f"- Auto Rationale: {sr.rationale}\n"
                    f"- Auto Choice: {sr.choice}"
                )

            prompt = prompt_template.format(
                question=review.input,
                scorer_sections="\n\n".join(sections),
            )

            response = self.client.models.generate_content(
                model=self.review_model,
                contents=prompt,
            )
            review.discrepancy_summary = response.text
            print(f"  [{i+1}/{len(reviews)}] Discrepancy summary done")

        return reviews

    # ── Analyze score differences ────────────────────────────────

    def analyze_score_differences(self, reviews):
        """Generate overall analysis of human-vs-auto score differences.

        Args:
            reviews: list[EntryReview] with scores populated.

        Returns:
            Markdown-formatted analysis string.
        """
        # Build comparison table
        rows = []
        for review in reviews:
            for sr in review.scorer_results:
                rows.append(
                    f"| {review.index+1} | {sr.scorer_name} | "
                    f"{review.auto_scores.get(sr.scorer_name, 'N/A')} | "
                    f"{review.human_scores.get(sr.scorer_name, 'N/A')} | "
                    f"{review.score_diff.get(sr.scorer_name, 'N/A')} |"
                )

        table = (
            "| Entry | Scorer | Auto Score | Human Score | Diff |\n"
            "|---|---|---|---|---|\n"
            + "\n".join(rows)
        )

        # Collect discrepancy summaries
        summaries = "\n\n".join(
            f"### Entry {r.index+1}\n{r.discrepancy_summary}"
            for r in reviews if r.discrepancy_summary
        )

        prompt_template = load_prompt(
            "eval_review", self.review_model, "score_analysis",
            self.prompt_version, self.prompts_dir,
        )

        prompt = prompt_template.format(
            score_comparison_table=table,
            all_discrepancy_summaries=summaries,
        )

        response = self.client.models.generate_content(
            model=self.review_model,
            contents=prompt,
        )
        return response.text

    # ── Suggest scorer prompt improvements ───────────────────────

    def suggest_prompt_edits(self, reviews, scorer_name):
        """Suggest improvements to a scorer prompt based on discrepancy patterns.

        Args:
            reviews: list[EntryReview] with discrepancy data.
            scorer_name: One of "reference", "judgement", "suggestion".

        Returns:
            Markdown string with suggested prompt modifications.
        """
        # Load current scorer prompt
        prompt_file_name = SCORER_PROMPT_NAMES[scorer_name]
        current_prompt = load_prompt(
            "eval_scorer", self.eval_model, prompt_file_name,
            self.eval_prompt_version, self.prompts_dir,
        )

        # Collect discrepancy data for this scorer
        discrepancy_data = []
        for review in reviews:
            sr = next((s for s in review.scorer_results if s.scorer_name == scorer_name), None)
            if sr is None:
                continue

            human_feedback_section = self._extract_feedback_section(
                review.human_feedback, scorer_name,
            )
            discrepancy_data.append(
                f"### Entry {review.index+1}\n"
                f"- Question: {review.input[:200]}...\n"
                f"- Auto Score: {review.auto_scores.get(scorer_name, 'N/A')}\n"
                f"- Human Score: {review.human_scores.get(scorer_name, 'N/A')}\n"
                f"- Auto Rationale: {sr.rationale[:500]}\n"
                f"- Human Feedback: {human_feedback_section}\n"
                f"- Discrepancy: {review.discrepancy_summary[:500] if review.discrepancy_summary else 'N/A'}"
            )

        prompt_template = load_prompt(
            "eval_review", self.review_model, "prompt_improvement",
            self.prompt_version, self.prompts_dir,
        )

        prompt = prompt_template.format(
            current_prompt=current_prompt,
            discrepancy_analysis="\n\n".join(discrepancy_data),
            scorer_name=scorer_name,
        )

        response = self.client.models.generate_content(
            model=self.review_model,
            contents=prompt,
        )
        return response.text

    # ── Full review pipeline ─────────────────────────────────────

    def run_full_review(self, data, scorer_names=None):
        """Run the complete review pipeline.

        Args:
            data: list[dict] in simplified format.
            scorer_names: Optional filter for which scorers to analyze.

        Returns:
            ReviewReport with all analysis populated.
        """
        if scorer_names is None:
            scorer_names = list(SCORER_FACTORIES.keys())

        print("Step 1/4: Re-running scorers...")
        reviews = self.rerun_scorers(data, scorer_names)

        print("Step 2/4: Summarizing discrepancies...")
        reviews = self.summarize_discrepancies(reviews)

        print("Step 3/4: Analyzing score differences...")
        overall_analysis = self.analyze_score_differences(reviews)

        print("Step 4/4: Suggesting prompt improvements...")
        prompt_suggestions = {}
        for name in scorer_names:
            prompt_suggestions[name] = self.suggest_prompt_edits(reviews, name)

        return ReviewReport(
            entries=reviews,
            overall_score_analysis=overall_analysis,
            prompt_suggestions=prompt_suggestions,
        )

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _extract_feedback_section(feedback, scorer_name):
        """Extract the relevant section from human feedback text.

        Args:
            feedback: Raw human feedback string with numbered sections.
            scorer_name: One of "reference", "judgement", "suggestion".

        Returns:
            Extracted section text, or full feedback if parsing fails.
        """
        if not feedback:
            return ""

        section_map = {"reference": 1, "judgement": 2, "suggestion": 3}
        section_num = section_map.get(scorer_name, 0)
        if section_num == 0:
            return feedback

        # Match "N." or "N)" followed by content until next section or end
        pattern = rf'{section_num}\s*[.)]\s*(.*?)(?=\n\s*[{section_num+1}-9]\s*[.)]|\Z)'
        match = re.search(pattern, feedback, re.DOTALL)
        if match:
            return match.group(1).strip()

        return feedback
