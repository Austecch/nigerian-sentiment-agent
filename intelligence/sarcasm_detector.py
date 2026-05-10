# intelligence/sarcasm_detector.py
from loguru import logger
from intelligence.cultural_lexicon import cultural_lexicon


class SarcasmDetector:
    """
    Detects sarcasm in Nigerian political posts
    Uses rule-based detection plus lexicon analysis
    """

    # Phrases that are almost always sarcastic
    # in Nigerian political context
    HIGH_CONFIDENCE_SARCASM = [
        "e go better",
        "wonderful government",
        "best president ever",
        "best governor ever",
        "we are lucky to have",
        "thank god for this government",
        "our caring government",
        "they are working hard",
        "typical nigeria",
        "only in nigeria",
        "as per usual",
        "nothing to see here",
        "government is trying",
        "we don suffer reach",
    ]

    # Patterns that suggest sarcasm
    SARCASM_PATTERNS = [
        # Praise followed by suffering context
        ("great job", ["suffering", "hungry", "no light",
                       "no fuel", "sapa", "wahala"]),
        ("well done", ["still", "yet", "but", "however",
                       "despite", "meanwhile"]),
        ("congratulations", ["poverty", "hunger",
                             "suffering", "hardship"]),
    ]

    def detect_sarcasm(
        self,
        text: str,
        context_clues: list = None
    ) -> dict:
        """
        Detect sarcasm in a post
        Returns detection result with confidence
        """
        if not text:
            return {
                "is_sarcastic": False,
                "confidence": 0.0,
                "indicator": None
            }

        text_lower = text.lower()

        # Check high confidence sarcasm phrases
        for phrase in self.HIGH_CONFIDENCE_SARCASM:
            if phrase in text_lower:
                logger.debug(
                    f"High confidence sarcasm: '{phrase}'"
                )
                return {
                    "is_sarcastic": True,
                    "confidence": 0.85,
                    "indicator": phrase
                }

        # Check lexicon sarcasm indicators
        if cultural_lexicon.detect_sarcasm_indicators(text):
            return {
                "is_sarcastic": True,
                "confidence": 0.75,
                "indicator": "lexicon_match"
            }

        # Check sarcasm patterns
        for positive_phrase, negative_words in \
                self.SARCASM_PATTERNS:
            if positive_phrase in text_lower:
                for neg_word in negative_words:
                    if neg_word in text_lower:
                        return {
                            "is_sarcastic": True,
                            "confidence": 0.70,
                            "indicator": (
                                f"{positive_phrase} + "
                                f"{neg_word}"
                            )
                        }

        # Check for excessive punctuation sarcasm
        exclamation_count = text.count("!")
        if exclamation_count >= 3:
            # Multiple exclamations often indicate sarcasm
            return {
                "is_sarcastic": True,
                "confidence": 0.55,
                "indicator": "excessive_exclamation"
            }

        return {
            "is_sarcastic": False,
            "confidence": 0.80,
            "indicator": None
        }

    def adjust_polarity_for_sarcasm(
        self,
        polarity: str,
        is_sarcastic: bool
    ) -> str:
        """
        Flip polarity if sarcasm is detected
        Positive sarcasm is actually negative intent
        """
        if not is_sarcastic:
            return polarity

        polarity_flip = {
            "Positive": "Negative",
            "Negative": "Positive",
            "Neutral": "Neutral"
        }

        flipped = polarity_flip.get(polarity, polarity)
        if flipped != polarity:
            logger.debug(
                f"Polarity flipped due to sarcasm: "
                f"{polarity} -> {flipped}"
            )
        return flipped


# Single instance to use across project
sarcasm_detector = SarcasmDetector()