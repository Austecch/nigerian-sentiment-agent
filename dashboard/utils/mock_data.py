import random
from datetime import datetime, timedelta

SAMPLE_POSTS = [
    {"content": "The fuel subsidy removal is really hurting ordinary Nigerians. Sapa don catch everyone. We need real solutions not just announcements.", "source": "X", "polarity": "Negative", "emotional_tone": "Anger", "topic": "fuel_subsidy", "location": "Lagos", "sarcasm_detected": False, "confidence_score": 0.92, "target_of_sentiment": "Policy", "explanation": "Clear complaint about fuel subsidy impact, using Nigerian Pidgin 'sapa' for hardship"},
    {"content": "Tinubu's speech yesterday showed direction for the economy. I see hope for real change. #RenewedHope", "source": "X", "polarity": "Positive", "emotional_tone": "Hope", "topic": "governance", "location": "Abuja", "sarcasm_detected": False, "confidence_score": 0.85, "target_of_sentiment": "Personality", "explanation": "Supportive of presidential address, expressed optimism"},
    {"content": "INEC don ready for Edo election? See the way dem dey do parallel VAS, election fit be interesting.", "source": "X", "polarity": "Neutral", "emotional_tone": "Mixed", "topic": "election", "location": "Benin", "sarcasm_detected": False, "confidence_score": 0.78, "target_of_sentiment": "Governance", "explanation": "Discussing election readiness, mixed Pidgin-English"},
    {"content": "E go better. After all the wahala, nothing change. Best president ever wey dey sleep while country burn.", "source": "Nairaland", "polarity": "Negative", "emotional_tone": "Anger", "topic": "governance", "location": "Port Harcourt", "sarcasm_detected": True, "confidence_score": 0.95, "target_of_sentiment": "Personality", "explanation": "Heavy sarcasm - 'best president ever' while describing neglect"},
    {"content": "Bandit attack for Zamfara again, 20 people killed. Government need to do something. Security is in shambles.", "source": "Nairaland", "polarity": "Negative", "emotional_tone": "Anger", "topic": "security", "location": "Zamfara", "sarcasm_detected": False, "confidence_score": 0.91, "target_of_sentiment": "Security", "explanation": "Reporting security incident, demanding government action"},
    {"content": "Naira dey fall everyday. Dollar rate don reach 1800. How we go survive with this fuel price sef?", "source": "X", "polarity": "Negative", "emotional_tone": "Apathy", "topic": "economy", "location": "Kano", "sarcasm_detected": False, "confidence_score": 0.88, "target_of_sentiment": "Economy", "explanation": "Economic complaint about currency devaluation and fuel prices"},
    {"content": "Peter Obi supporters dem call Obidient. This movement is different from regular politics.", "source": "Nairaland", "polarity": "Positive", "emotional_tone": "Excitement", "topic": "election", "location": "Onitsha", "sarcasm_detected": False, "confidence_score": 0.82, "target_of_sentiment": "Personality", "explanation": "Positive reference to Obidient movement"},
    {"content": "APC and PDP na the same thing. Stomach infrastructure dey work for both parties. We just dey choose between evil and evil.", "source": "X", "polarity": "Negative", "emotional_tone": "Apathy", "topic": "governance", "location": "Lagos", "sarcasm_detected": True, "confidence_score": 0.89, "target_of_sentiment": "Party", "explanation": "Cynical view of both major parties, calling them equivalent"},
    {"content": "The Dangote refinery go change everything. PMS price go finally come down. Just dey patient.", "source": "NewsComment", "polarity": "Neutral", "emotional_tone": "Hope", "topic": "economy", "location": "Ibadan", "sarcasm_detected": False, "confidence_score": 0.74, "target_of_sentiment": "Economy", "explanation": "Cautious optimism about Dangote refinery impact"},
    {"content": "Buhari regime corruption case dey open everyday. EFCC dey try but d truth dey bitter. Dem don Ghana must go plenty money.", "source": "Nairaland", "polarity": "Negative", "emotional_tone": "Anger", "topic": "governance", "location": "Abuja", "sarcasm_detected": False, "confidence_score": 0.87, "target_of_sentiment": "Governance", "explanation": "Reference to corruption probe and 'Ghana must go' bribery bags"},
    {"content": "I just collect my PVC. 2027 election go be different. We need real change for this country.", "source": "X", "polarity": "Positive", "emotional_tone": "Hope", "topic": "election", "location": "Enugu", "sarcasm_detected": False, "confidence_score": 0.80, "target_of_sentiment": "Governance", "explanation": "Civic engagement with optimism about upcoming election"},
    {"content": "Shey dem think we be mumu? Same people wey dey rule us since 1999 dey come again with new packaging.", "source": "X", "polarity": "Negative", "emotional_tone": "Anger", "topic": "election", "location": "Kaduna", "sarcasm_detected": True, "confidence_score": 0.93, "target_of_sentiment": "Personality", "explanation": "Anger at political continuity, using 'mumu' and 'packaging' as Nigerian slang"},
    {"content": "Kidnapping for Abuja-Kaduna highway don increase again. Dem dey collect ransom like is normal. Na wa o!", "source": "NewsComment", "polarity": "Negative", "emotional_tone": "Anger", "topic": "security", "location": "Kaduna", "sarcasm_detected": False, "confidence_score": 0.90, "target_of_sentiment": "Security", "explanation": "Security concern with highway kidnappings"},
    {"content": "The budget presentation was comprehensive. I like the focus on infrastructure and health. Good direction.", "source": "NewsComment", "polarity": "Positive", "emotional_tone": "Hope", "topic": "governance", "location": "Abuja", "sarcasm_detected": False, "confidence_score": 0.76, "target_of_sentiment": "Policy", "explanation": "Supporting budget priorities"},
    {"content": "Labour Party go shock everybody for 2027. The Obidient movement dey grow pass what dem think.", "source": "Nairaland", "polarity": "Positive", "emotional_tone": "Excitement", "topic": "election", "location": "Awka", "sarcasm_detected": False, "confidence_score": 0.83, "target_of_sentiment": "Party", "explanation": "Confident prediction about Labour Party growth"},
    {"content": "Fuel price go up again! N617 per litre? We are finished in this country. #SapaNation", "source": "X", "polarity": "Negative", "emotional_tone": "Anger", "topic": "fuel_subsidy", "location": "Ibadan", "sarcasm_detected": False, "confidence_score": 0.94, "target_of_sentiment": "Economy", "explanation": "Direct complaint about fuel price increase"},
    {"content": "Abeg make dem fix this ASUU strike. My pikin don dey house for 8 months. Education na priority abi?", "source": "X", "polarity": "Negative", "emotional_tone": "Anger", "topic": "governance", "location": "Ilorin", "sarcasm_detected": False, "confidence_score": 0.86, "target_of_sentiment": "Policy", "explanation": "Frustration with ASUU strike affecting children's education"},
    {"content": "Port Harcourt refinery dey work! I see with my own two eyes. This one no be rumor.", "source": "X", "polarity": "Positive", "emotional_tone": "Excitement", "topic": "economy", "location": "Port Harcourt", "sarcasm_detected": False, "confidence_score": 0.79, "target_of_sentiment": "Economy", "explanation": "First-hand account of refinery operations"},
    {"content": "Northern governors meeting for Kaduna. Dem dey talk about economy and security. Hope e no be another talk shop.", "source": "Nairaland", "polarity": "Neutral", "emotional_tone": "Mixed", "topic": "governance", "location": "Kaduna", "sarcasm_detected": True, "confidence_score": 0.81, "target_of_sentiment": "Governance", "explanation": "Skepticism about governors' meeting outcomes"},
    {"content": "God bless Nigeria! We are making progress step by step. The Renewed Hope agenda is working.", "source": "X", "polarity": "Positive", "emotional_tone": "Hope", "topic": "governance", "location": "Abuja", "sarcasm_detected": False, "confidence_score": 0.72, "target_of_sentiment": "Personality", "explanation": "Supportive government sentiment"},
    {"content": "Herdsmen and farmers crisis for Benue no get solution. Everyday people dey die. Sorrowful.", "source": "NewsComment", "polarity": "Negative", "emotional_tone": "Apathy", "topic": "security", "location": "Benue", "sarcasm_detected": False, "confidence_score": 0.88, "target_of_sentiment": "Security", "explanation": "Ongoing farmers-herders conflict reporting"},
    {"content": "CBN don release new monetary policy. Let me read tire before I talk. But e look promising.", "source": "X", "polarity": "Neutral", "emotional_tone": "Mixed", "topic": "economy", "location": "Lagos", "sarcasm_detected": False, "confidence_score": 0.73, "target_of_sentiment": "Policy", "explanation": "Cautious response to CBN policy announcement"},
    {"content": "My brother, INEC go rig again. Dem never see free and fair election for this country since 1999.", "source": "Nairaland", "polarity": "Negative", "emotional_tone": "Apathy", "topic": "election", "location": "Owerri", "sarcasm_detected": False, "confidence_score": 0.85, "target_of_sentiment": "Governance", "explanation": "Distrust of electoral process"},
    {"content": "Best infrastructure development since independence. The roads are finally being fixed. We must give credit where due. #ProgressiveNigeria", "source": "X", "polarity": "Positive", "emotional_tone": "Hope", "topic": "governance", "location": "Abuja", "sarcasm_detected": True, "confidence_score": 0.77, "target_of_sentiment": "Personality", "explanation": "Potentially sarcastic praise"},
    {"content": "The election tribunal judgment today show say judiciary still dey work. Justice prevail.", "source": "Nairaland", "polarity": "Positive", "emotional_tone": "Excitement", "topic": "governance", "location": "Abuja", "sarcasm_detected": False, "confidence_score": 0.84, "target_of_sentiment": "Governance", "explanation": "Positive reaction to tribunal ruling"},
]

LOCATIONS = [
    {"location": "Lagos", "latitude": 6.5244, "longitude": 3.3792},
    {"location": "Abuja", "latitude": 9.0765, "longitude": 7.3986},
    {"location": "Kano", "latitude": 12.0022, "longitude": 8.5920},
    {"location": "Ibadan", "latitude": 7.3775, "longitude": 3.9470},
    {"location": "Port Harcourt", "latitude": 4.8156, "longitude": 7.0498},
    {"location": "Kaduna", "latitude": 10.5105, "longitude": 7.4165},
    {"location": "Benin", "latitude": 6.3176, "longitude": 5.6145},
    {"location": "Enugu", "latitude": 6.4483, "longitude": 7.5088},
    {"location": "Jos", "latitude": 9.8965, "longitude": 8.8583},
    {"location": "Maiduguri", "latitude": 11.8333, "longitude": 13.1500},
    {"location": "Calabar", "latitude": 4.9757, "longitude": 8.3417},
    {"location": "Onitsha", "latitude": 6.1469, "longitude": 6.8069},
    {"location": "Aba", "latitude": 5.1066, "longitude": 7.3667},
    {"location": "Sokoto", "latitude": 13.0622, "longitude": 5.2430},
    {"location": "Ilorin", "latitude": 8.4857, "longitude": 4.6694},
    {"location": "Owerri", "latitude": 5.4850, "longitude": 7.0350},
    {"location": "Yola", "latitude": 9.2035, "longitude": 12.4954},
    {"location": "Awka", "latitude": 6.2100, "longitude": 7.0700},
    {"location": "Uyo", "latitude": 5.0389, "longitude": 7.9095},
    {"location": "Zamfara", "latitude": 12.1557, "longitude": 6.4843},
    {"location": "Benue", "latitude": 7.3369, "longitude": 8.7404},
    {"location": "Gombe", "latitude": 10.2824, "longitude": 11.1748},
    {"location": "Bauchi", "latitude": 10.3103, "longitude": 9.8428},
    {"location": "Akure", "latitude": 7.2571, "longitude": 5.2058},
]

SENTIMENTS = {"Positive": 0, "Negative": 0, "Neutral": 0}
EMOTIONS = {"Hope": 0, "Anger": 0, "Apathy": 0, "Excitement": 0, "Mixed": 0}
TOPICS = {}
SOURCE_COUNTS = {}

for post in SAMPLE_POSTS:
    SENTIMENTS[post["polarity"]] = SENTIMENTS.get(post["polarity"], 0) + 1
    EMOTIONS[post["emotional_tone"]] = EMOTIONS.get(post["emotional_tone"], 0) + 1
    TOPICS[post["topic"]] = TOPICS.get(post["topic"], 0) + 1
    SOURCE_COUNTS[post["source"]] = SOURCE_COUNTS.get(post["source"], 0) + 1

total = len(SAMPLE_POSTS)

TREND_DATA = []
now = datetime.now()
for i in range(24):
    ts = (now - timedelta(hours=23-i)).strftime("%Y-%m-%d %H:00")
    TREND_DATA.append({
        "timestamp": ts,
        "positive": random.randint(1, 8),
        "negative": random.randint(3, 15),
        "neutral": random.randint(2, 10),
    })

HOTSPOT_DATA = []
for loc in LOCATIONS:
    loc_total = random.randint(3, 25)
    pos_pct = random.randint(10, 60)
    neg_pct = random.randint(20, 70)
    dominant = "Positive" if pos_pct > neg_pct else "Negative" if neg_pct > pos_pct else "Neutral"
    emotions_list = ["Hope", "Anger", "Apathy", "Excitement", "Mixed"]
    HOTSPOT_DATA.append({
        "location": loc.get("location", loc.get("position", "Unknown")),
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        "mention_count": loc_total,
        "dominant_sentiment": dominant,
        "dominant_emotion": random.choice(emotions_list),
        "positive_percent": pos_pct,
        "negative_percent": neg_pct,
    })

TOPICS_DATA = [{"topic": t, "mention_count": c} for t, c in sorted(TOPICS.items(), key=lambda x: -x[1])]
SOURCE_DATA = {s: {"total": c, "positive": 0, "negative": 0, "neutral": 0} for s, c in SOURCE_COUNTS.items()}
