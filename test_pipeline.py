# test_pipeline.py
# Tests the full pipeline with sample Nigerian political posts
from datetime import datetime
from database.mongodb_client import mongodb_client
from agents.interpreter_agent import interpreter_agent
from agents.aggregator_agent import aggregator_agent
from loguru import logger

print("=" * 50)
print("TESTING FULL PIPELINE WITH SAMPLE DATA")
print("=" * 50)

# Sample Nigerian political posts for testing
SAMPLE_POSTS = [
    {
        "source": "X",
        "content": (
            "This government don finish us o. "
            "Fuel price don reach 1000 naira, "
            "sapa don catch everybody. "
            "Emilokan people where una dey?"
        ),
        "location": "Lagos",
        "hashtags": ["#Nigeria", "#FuelPrice"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
    {
        "source": "Nairaland",
        "content": (
            "Peter Obi and the obidient movement "
            "are still strong. Labour Party has "
            "the structure now. E go loud for "
            "the next election!"
        ),
        "location": "Abuja",
        "hashtags": ["#Obidient", "#LabourParty"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
    {
        "source": "NewsComment",
        "content": (
            "Wonderful government we have! "
            "They remove fuel subsidy, "
            "naira don crash, people dey suffer "
            "but they say e go better. "
            "God bless our caring leaders!"
        ),
        "location": "Port Harcourt",
        "hashtags": ["#Nigeria"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
    {
        "source": "X",
        "content": (
            "The security situation for Kano "
            "is getting worse everyday. "
            "Bandits dey operate freely, "
            "wahala everywhere. "
            "Government must act now!"
        ),
        "location": "Kano",
        "hashtags": ["#Security", "#Nigeria"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
    {
        "source": "Nairaland",
        "content": (
            "INEC must do better next election. "
            "The electoral process needs reform. "
            "Nigerians deserve free and fair elections. "
            "No more stomach infrastructure politics!"
        ),
        "location": "Abuja",
        "hashtags": ["#INEC", "#Election"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
    {
        "source": "X",
        "content": (
            "Japa wave no go stop until "
            "this government fix things. "
            "Brain drain dey happen everyday. "
            "All my mates don comot Nigeria."
        ),
        "location": "Lagos",
        "hashtags": ["#Japa", "#Nigeria"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
    {
        "source": "NewsComment",
        "content": (
            "APC structure too strong for PDP "
            "in the southwest. But Labour Party "
            "dey grow. 2027 election go be "
            "very interesting to watch."
        ),
        "location": "Ibadan",
        "hashtags": ["#APC", "#PDP", "#LabourParty"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
    {
        "source": "X",
        "content": (
            "CBN policies don affect everybody. "
            "Dollar don go up again, "
            "naira don fall. "
            "How ordinary Nigerians go survive?"
        ),
        "location": "Lagos",
        "hashtags": ["#CBN", "#Naira", "#Economy"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
    {
        "source": "Nairaland",
        "content": (
            "I get hope for Nigeria still. "
            "Young Nigerians dey mobilize, "
            "dey vote, dey hold government "
            "accountable. Change go come!"
        ),
        "location": "Enugu",
        "hashtags": ["#Nigeria", "#Hope"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
    {
        "source": "X",
        "content": (
            "Governor just commission another "
            "road wey dem build in 1985. "
            "Na so dem dey do us every election year. "
            "Ghana must go politics still dey strong."
        ),
        "location": "Benin City",
        "hashtags": ["#Corruption", "#Nigeria"],
        "bot_risk": "Low",
        "scraped_at": datetime.utcnow(),
    },
]


def run_test():
    """Run complete pipeline test"""

    # STEP 1: Save sample posts to database
    print("\nSTEP 1: Saving sample posts to MongoDB...")
    try:
        saved = mongodb_client.save_many_raw_posts(
            SAMPLE_POSTS
        )
        print(f"✅ Saved {saved} sample posts")
    except Exception as e:
        print(f"❌ Failed to save posts: {e}")
        return

    # STEP 2: Interpret posts with Claude
    print("\nSTEP 2: Interpreting posts with Claude AI...")
    print("(This will make API calls - may take 1-2 minutes)")

    interpreted = []
    for i, post in enumerate(SAMPLE_POSTS):
        try:
            print(
                f"  Interpreting post {i+1}"
                f"/{len(SAMPLE_POSTS)}..."
            )
            result = interpreter_agent.interpret_post(post)
            if result:
                interpreted.append(result)
                print(
                    f"  ✅ Post {i+1}: "
                    f"{result.get('polarity')} | "
                    f"{result.get('emotional_tone')} | "
                    f"Sarcasm: {result.get('sarcasm_detected')}"
                )
        except Exception as e:
            print(f"  ❌ Post {i+1} failed: {e}")

    print(
        f"\n✅ Interpreted {len(interpreted)}"
        f"/{len(SAMPLE_POSTS)} posts"
    )

    # STEP 3: Aggregate results
    print("\nSTEP 3: Aggregating results...")
    try:
        summary = aggregator_agent.aggregate(interpreted)

        polarity = summary.get("polarity", {})
        emotion = summary.get("emotional_tone", {})
        volume = summary.get("volume", {})

        print("\n" + "=" * 40)
        print("PIPELINE TEST RESULTS")
        print("=" * 40)
        print(
            f"Total Posts Analyzed: "
            f"{summary.get('total_posts_analyzed', 0)}"
        )
        print(f"Top Topic: {volume.get('top_topic', 'N/A')}")
        print(
            f"\nPOLARITY:"
            f"\n  Positive: "
            f"{polarity.get('positive_percent', 0)}%"
            f"\n  Negative: "
            f"{polarity.get('negative_percent', 0)}%"
            f"\n  Neutral:  "
            f"{polarity.get('neutral_percent', 0)}%"
        )
        print(
            f"\nDOMINANT EMOTION: "
            f"{emotion.get('dominant_emotion', 'Mixed')}"
        )
        print(
            f"\nSARCASM DETECTED: "
            f"{polarity.get('sarcasm_count', 0)} posts"
        )
        print("=" * 40)
        print(
            "\n✅ Test complete! "
            "Check your dashboard at "
            "http://localhost:8501"
        )

    except Exception as e:
        print(f"❌ Aggregation failed: {e}")


if __name__ == "__main__":
    run_test()