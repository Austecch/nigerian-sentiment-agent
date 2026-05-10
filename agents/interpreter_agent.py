# agents/interpreter_agent.py
import json
import anthropic
from loguru import logger
from config import config
from intelligence.cultural_lexicon import cultural_lexicon
from intelligence.language_detector import language_detector
from intelligence.sarcasm_detector import sarcasm_detector
from intelligence.system_prompts import CULTURAL_INTERPRETER_PROMPT
from database.mongodb_client import mongodb_client


class InterpreterAgent:
    """
    Agent B - The Cultural Interpreter
    Decodes Nigerian political language using
    Claude 3.5 and cultural lexicon
    """

    def __init__(self):
        self.name = "Cultural Interpreter Agent"
        self.client = anthropic.Anthropic(
            api_key=config.ANTHROPIC_API_KEY
        )
        self.model = "claude-3-5-sonnet-20241022"
        logger.info(f"{self.name} initialized")

    def interpret_post(self, post: dict) -> dict:
        """
        Interpret a single post using Claude
        and cultural lexicon
        """
        content = post.get("content", "")
        if not content:
            return None

        try:
            # Step 1: Pre-process with cultural lexicon
            lexicon_context = (
                cultural_lexicon.build_context_summary(content)
            )
            detected_topic = cultural_lexicon.detect_topic(
                content
            )
            pre_sarcasm = sarcasm_detector.detect_sarcasm(
                content
            )
            languages = language_detector.detect_languages(
                content
            )

            # Step 2: Build enhanced prompt with context
            user_message = f"""
Analyze this Nigerian political post and return JSON:

POST: {content}

LOCATION: {post.get('location', 'Unknown')}
SOURCE: {post.get('source', 'Unknown')}

{f'CULTURAL CONTEXT: {lexicon_context}' if lexicon_context else ''}
{f'DETECTED TOPIC: {detected_topic}'}
{f'PRE-DETECTED SARCASM: {pre_sarcasm["is_sarcastic"]}'}

Return ONLY valid JSON with these exact fields:
polarity, emotional_tone, target_of_sentiment,
sarcasm_detected, language_mix, confidence_score,
explanation
"""

            # Step 3: Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=CULTURAL_INTERPRETER_PROMPT,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            # Step 4: Parse Claude response
            response_text = message.content[0].text.strip()

            # Clean response if needed
            if "```json" in response_text:
                response_text = response_text.split(
                    "```json"
                )[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split(
                    "```"
                )[1].split("```")[0].strip()

            interpretation = json.loads(response_text)

            # Step 5: Build final interpreted post
            interpreted = {
                "raw_post_id": str(
                    post.get("_id", "")
                ),
                "source": post.get("source", "Unknown"),
                "location": post.get("location", "Unknown"),
                "content": content,
                "topic": detected_topic,
                "language_mix": interpretation.get(
                    "language_mix", languages
                ),
                "polarity": interpretation.get(
                    "polarity", "Neutral"
                ),
                "emotional_tone": interpretation.get(
                    "emotional_tone", "Mixed"
                ),
                "target_of_sentiment": interpretation.get(
                    "target_of_sentiment", "General"
                ),
                "sarcasm_detected": interpretation.get(
                    "sarcasm_detected",
                    pre_sarcasm["is_sarcastic"]
                ),
                "bot_or_campaign_risk": post.get(
                    "bot_risk", "Low"
                ),
                "confidence_score": interpretation.get(
                    "confidence_score", 0.7
                ),
                "explanation": interpretation.get(
                    "explanation", ""
                ),
            }

            # Save to database
            mongodb_client.save_interpreted_post(interpreted)

            return interpreted

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return self._fallback_interpretation(post)
        except Exception as e:
            logger.error(f"Interpretation failed: {e}")
            return self._fallback_interpretation(post)

    def interpret_batch(
        self,
        posts: list,
        batch_size: int = 10
    ) -> list:
        """
        Interpret a batch of posts
        Processes in smaller batches to manage API costs
        """
        logger.info(
            f"{self.name}: Interpreting "
            f"{len(posts)} posts"
        )

        interpreted_posts = []

        for i, post in enumerate(posts):
            try:
                result = self.interpret_post(post)
                if result:
                    interpreted_posts.append(result)

                # Log progress every 10 posts
                if (i + 1) % 10 == 0:
                    logger.info(
                        f"Interpreted {i + 1}"
                        f"/{len(posts)} posts"
                    )

            except Exception as e:
                logger.error(
                    f"Failed to interpret post {i}: {e}"
                )
                continue

        logger.info(
            f"Batch interpretation complete: "
            f"{len(interpreted_posts)} posts interpreted"
        )

        return interpreted_posts

    def _fallback_interpretation(
        self,
        post: dict
    ) -> dict:
        """
        Fallback when Claude API fails
        Uses rule-based interpretation only
        """
        content = post.get("content", "")
        pre_sarcasm = sarcasm_detector.detect_sarcasm(content)
        languages = language_detector.detect_languages(content)
        topic = cultural_lexicon.detect_topic(content)

        return {
            "raw_post_id": str(post.get("_id", "")),
            "source": post.get("source", "Unknown"),
            "location": post.get("location", "Unknown"),
            "content": content,
            "topic": topic,
            "language_mix": languages,
            "polarity": "Neutral",
            "emotional_tone": "Mixed",
            "target_of_sentiment": "General",
            "sarcasm_detected": pre_sarcasm["is_sarcastic"],
            "bot_or_campaign_risk": post.get(
                "bot_risk", "Low"
            ),
            "confidence_score": 0.3,
            "explanation": "Fallback rule-based interpretation",
        }


# Single instance
interpreter_agent = InterpreterAgent()