# scrapers/geo_filter.py
import re
from typing import Optional
from loguru import logger


class GeoFilter:
    """Identifies Nigerian locations in posts"""

    # Nigerian states and cities to detect
    NIGERIAN_LOCATIONS = {
        # Major cities
        "lagos": "Lagos",
        "abuja": "Abuja",
        "kano": "Kano",
        "port harcourt": "Port Harcourt",
        "ph": "Port Harcourt",
        "ibadan": "Ibadan",
        "benin city": "Benin City",
        "benin": "Benin City",
        "kaduna": "Kaduna",
        "enugu": "Enugu",
        "owerri": "Owerri",
        "calabar": "Calabar",
        "warri": "Warri",
        "jos": "Jos",
        "ilorin": "Ilorin",
        "abeokuta": "Abeokuta",
        "onitsha": "Onitsha",
        "maiduguri": "Maiduguri",
        "sokoto": "Sokoto",
        "zaria": "Zaria",
        # States
        "rivers": "Port Harcourt",
        "delta": "Warri",
        "anambra": "Onitsha",
        "imo": "Owerri",
        "cross river": "Calabar",
        "borno": "Maiduguri",
        "plateau": "Jos",
        "kwara": "Ilorin",
        "ogun": "Abeokuta",
        "oyo": "Ibadan",
        "edo": "Benin City",
        "kogi": "Lokoja",
        "niger": "Minna",
        "nasarawa": "Lafia",
        "benue": "Makurdi",
        "taraba": "Jalingo",
        "adamawa": "Yola",
        "gombe": "Gombe",
        "bauchi": "Bauchi",
        "jigawa": "Dutse",
        "kebbi": "Birnin Kebbi",
        "zamfara": "Gusau",
        "yobe": "Damaturu",
        "akwa ibom": "Uyo",
        "abia": "Umuahia",
        "ebonyi": "Abakaliki",
        "ekiti": "Ado-Ekiti",
        "ondo": "Akure",
        "osun": "Osogbo",
        "lagos island": "Lagos",
        "victoria island": "Lagos",
        "lekki": "Lagos",
        "ikeja": "Lagos",
        "surulere": "Lagos",
        "wuse": "Abuja",
        "garki": "Abuja",
        "maitama": "Abuja",
        "gwarinpa": "Abuja",
    }

    # Nigerian slang location references
    SLANG_LOCATIONS = {
        "eko": "Lagos",
        "lag": "Lagos",
        "9ja": "Nigeria",
        "naija": "Nigeria",
        "the rock city": "Abuja",
        "garden city": "Port Harcourt",
    }

    def detect_location(
        self,
        text: str,
        profile_location: str = None
    ) -> str:
        """
        Detect Nigerian location from post text or profile
        Returns the detected location or 'Unknown'
        """
        if not text:
            return "Unknown"

        text_lower = text.lower()

        # Check profile location first
        if profile_location:
            profile_lower = profile_location.lower()
            for key, value in self.NIGERIAN_LOCATIONS.items():
                if key in profile_lower:
                    return value

        # Check post text for location mentions
        for key, value in self.NIGERIAN_LOCATIONS.items():
            if key in text_lower:
                logger.debug(
                    f"Location detected: {value} from '{key}'"
                )
                return value

        # Check slang locations
        for key, value in self.SLANG_LOCATIONS.items():
            if key in text_lower:
                return value

        # Check for Nigerian flag or common Nigerian terms
        nigerian_indicators = [
            "naija", "9ja", "nigeria", "nigerian",
            "nairalnad", "abeg", "oga", "wahala"
        ]
        for indicator in nigerian_indicators:
            if indicator in text_lower:
                return "Nigeria"

        return "Unknown"

    def is_nigerian_content(self, text: str) -> bool:
        """
        Check if content is likely Nigerian
        Returns True if Nigerian indicators found
        """
        if not text:
            return False

        text_lower = text.lower()

        nigerian_indicators = [
            # Pidgin words
            "naija", "9ja", "abeg", "oga", "wahala",
            "sabi", "no be", "wetin", "abi", "sha",
            "ehen", "e don", "e go", "na im", "chai",
            # Political terms
            "emilokan", "obidient", "sapa", "structure",
            "tinubu", "peter obi", "atiku", "apc", "pdp",
            "labour party", "inec", "buhari",
            # Local terms
            "nairaland", "nairalnd", "dangote",
        ]

        for indicator in nigerian_indicators:
            if indicator in text_lower:
                return True

        # Check for Nigerian locations
        location = self.detect_location(text)
        if location != "Unknown":
            return True

        return False


# Single instance to use across project
geo_filter = GeoFilter()