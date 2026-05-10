# intelligence/language_detector.py
from langdetect import detect, DetectorFactory
from loguru import logger

# Set seed for consistent results
DetectorFactory.seed = 42


class LanguageDetector:
    """
    Detects languages in Nigerian political posts
    Handles code-mixing and Pidgin English
    """

    # Yoruba indicator words
    YORUBA_INDICATORS = [
        "emi", "eyin", "awa", "won", "eleyi",
        "bawo", "kilode", "rara", "beeni", "beko",
        "ebi", "owo", "ile", "ode", "agba",
        "olorun", "ase", "jowo", "e jo", "daju",
    ]

    # Igbo indicator words
    IGBO_INDICATORS = [
        "nna", "nne", "obi", "chi", "ike",
        "onye", "ulo", "anya", "aka", "ndi",
        "oge", "ife", "udo", "maka", "biko",
        "chukwu", "igwe", "oga", "nwanne",
    ]

    # Hausa indicator words
    HAUSA_INDICATORS = [
        "kai", "kin", "mun", "sun", "suna",
        "allah", "dan", "mai", "abu", "gari",
        "kasa", "mutum", "rana", "dare", "ruwa",
        "gwamnati", "soja", "yan", "arewa",
    ]

    # Nigerian Pidgin indicators
    PIDGIN_INDICATORS = [
        "wetin", "abeg", "wahala", "abi", "na",
        "no be", "e don", "e go", "dey", "dem",
        "una", "wey", "fit", "sef", "sha",
        "ehen", "chai", "haba", "shey", "comot",
        "chop", "sabi", "ginger", "packaging",
        "yab", "mumu", "agbaya", "ode",
    ]

    def detect_languages(self, text: str) -> list:
        """
        Detect all languages present in a text
        Returns list of detected languages
        """
        if not text:
            return ["Unknown"]

        detected_languages = []
        text_lower = text.lower()

        # Check for Yoruba
        yoruba_count = sum(
            1 for word in self.YORUBA_INDICATORS
            if word in text_lower
        )
        if yoruba_count >= 1:
            detected_languages.append("Yoruba")

        # Check for Igbo
        igbo_count = sum(
            1 for word in self.IGBO_INDICATORS
            if word in text_lower
        )
        if igbo_count >= 1:
            detected_languages.append("Igbo")

        # Check for Hausa
        hausa_count = sum(
            1 for word in self.HAUSA_INDICATORS
            if word in text_lower
        )
        if hausa_count >= 1:
            detected_languages.append("Hausa")

        # Check for Pidgin
        pidgin_count = sum(
            1 for word in self.PIDGIN_INDICATORS
            if word in text_lower
        )
        if pidgin_count >= 2:
            detected_languages.append("Pidgin")

        # Always check for English using langdetect
        try:
            detected = detect(text)
            if detected == "en":
                if "English" not in detected_languages:
                    detected_languages.append("English")
        except Exception:
            pass

        # Default to English if nothing detected
        if not detected_languages:
            detected_languages = ["English"]

        return detected_languages

    def is_code_mixed(self, text: str) -> bool:
        """Check if text mixes multiple languages"""
        languages = self.detect_languages(text)
        return len(languages) > 1

    def get_primary_language(self, text: str) -> str:
        """Get the dominant language in a text"""
        languages = self.detect_languages(text)
        if not languages:
            return "English"
        return languages[0]


# Single instance to use across project
language_detector = LanguageDetector()