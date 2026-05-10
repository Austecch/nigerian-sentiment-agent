# intelligence/cultural_lexicon.py
import json
import os
from loguru import logger


class CulturalLexicon:
    """
    Manages the Nigerian political and cultural
    language database
    """

    def __init__(self):
        self.lexicon_path = os.path.join(
            os.path.dirname(__file__),
            "lexicon_data.json"
        )
        self.lexicon = {}
        self.load_lexicon()

    def load_lexicon(self):
        """Load the lexicon from JSON file"""
        try:
            with open(self.lexicon_path, "r") as f:
                self.lexicon = json.load(f)
            logger.info("Cultural lexicon loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load lexicon: {e}")
            self.lexicon = {}

    def get_term_info(self, term: str) -> dict:
        """Get information about a specific term"""
        term_lower = term.lower().strip()

        # Search across all categories
        all_categories = [
            "political_slang",
            "economic_slang",
            "pidgin_expressions",
        ]

        for category in all_categories:
            category_data = self.lexicon.get(category, {})
            if term_lower in category_data:
                return category_data[term_lower]

        return {}

    def detect_terms_in_text(self, text: str) -> list:
        """Find all known lexicon terms in a text"""
        if not text:
            return []

        text_lower = text.lower()
        found_terms = []

        all_categories = [
            "political_slang",
            "economic_slang",
            "pidgin_expressions",
        ]

        for category in all_categories:
            category_data = self.lexicon.get(category, {})
            for term, info in category_data.items():
                if term in text_lower:
                    found_terms.append({
                        "term": term,
                        "category": category,
                        "meaning": info.get("meaning", ""),
                        "sentiment_hint": info.get(
                            "sentiment_hint", "neutral"
                        ),
                    })

        return found_terms

    def detect_sarcasm_indicators(self, text: str) -> bool:
        """Check if text contains sarcasm indicators"""
        if not text:
            return False

        text_lower = text.lower()
        indicators = self.lexicon.get(
            "sarcasm_indicators", []
        )

        for indicator in indicators:
            if indicator in text_lower:
                logger.debug(
                    f"Sarcasm indicator found: {indicator}"
                )
                return True

        return False

    def detect_topic(self, text: str) -> str:
        """Detect the main political topic of a post"""
        if not text:
            return "General"

        text_lower = text.lower()
        topic_keywords = self.lexicon.get(
            "topic_keywords", {}
        )

        topic_scores = {}

        for topic, keywords in topic_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            if score > 0:
                topic_scores[topic] = score

        if not topic_scores:
            return "General"

        # Return topic with highest keyword matches
        return max(topic_scores, key=topic_scores.get)

    def get_political_entity(
        self,
        text: str
    ) -> dict:
        """Identify political entities mentioned in text"""
        if not text:
            return {}

        text_lower = text.lower()
        entities = self.lexicon.get("political_entities", {})
        found = {}

        # Check parties
        parties = entities.get("parties", {})
        for abbrev, full_name in parties.items():
            if abbrev in text_lower:
                found["party"] = full_name
                break

        # Check institutions
        institutions = entities.get("institutions", {})
        for abbrev, full_name in institutions.items():
            if abbrev in text_lower:
                found["institution"] = full_name
                break

        return found

    def build_context_summary(self, text: str) -> str:
        """
        Build a context summary for the LLM
        highlighting detected Nigerian terms
        """
        found_terms = self.detect_terms_in_text(text)

        if not found_terms:
            return ""

        context_parts = []
        for term_info in found_terms:
            context_parts.append(
                f"'{term_info['term']}' means "
                f"{term_info['meaning']}"
            )

        return (
            "Nigerian cultural context detected: "
            + "; ".join(context_parts)
        )


# Single instance to use across project
cultural_lexicon = CulturalLexicon()