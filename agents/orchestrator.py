# agents/orchestrator.py
from loguru import logger
from agents.scout_agent import scout_agent
from agents.interpreter_agent import interpreter_agent
from agents.aggregator_agent import aggregator_agent


class Orchestrator:
    """
    Master controller that coordinates all three agents
    Runs the complete pipeline from scraping to insights
    """

    def __init__(self):
        self.name = "Pipeline Orchestrator"
        logger.info(f"{self.name} initialized")

    def run_full_pipeline(
        self,
        max_posts_per_source: int = 50
    ) -> dict:
        """
        Run the complete sentiment analysis pipeline
        Scout -> Interpret -> Aggregate
        """
        logger.info(
            "=" * 50 +
            "\nStarting Full Pipeline Run\n" +
            "=" * 50
        )

        results = {
            "pipeline_status": "started",
            "scout_results": None,
            "interpreted_count": 0,
            "aggregated_summary": None,
            "errors": [],
        }

        # STEP 1: Scout Agent collects data
        logger.info("STEP 1: Scout Agent collecting data...")
        try:
            scout_results = scout_agent.collect_all_sources(
                max_posts_per_source=max_posts_per_source
            )
            results["scout_results"] = {
                "total_collected": scout_results[
                    "total_collected"
                ],
                "total_clean": scout_results["total_clean"],
            }
            raw_posts = scout_results["posts"]
            logger.info(
                f"Scout complete: "
                f"{len(raw_posts)} clean posts"
            )
        except Exception as e:
            error_msg = f"Scout Agent failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["pipeline_status"] = "scout_failed"
            return results

        if not raw_posts:
            logger.warning("No posts collected. Stopping.")
            results["pipeline_status"] = "no_data"
            return results

        # STEP 2: Interpreter Agent processes posts
        logger.info(
            "STEP 2: Interpreter Agent analyzing posts..."
        )
        try:
            interpreted_posts = (
                interpreter_agent.interpret_batch(raw_posts)
            )
            results["interpreted_count"] = len(
                interpreted_posts
            )
            logger.info(
                f"Interpretation complete: "
                f"{len(interpreted_posts)} posts"
            )
        except Exception as e:
            error_msg = f"Interpreter Agent failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["pipeline_status"] = "interpreter_failed"
            return results

        if not interpreted_posts:
            logger.warning(
                "No posts interpreted. Stopping."
            )
            results["pipeline_status"] = "no_interpretations"
            return results

        # STEP 3: Aggregator synthesizes insights
        logger.info(
            "STEP 3: Aggregator synthesizing insights..."
        )
        try:
            summary = aggregator_agent.aggregate(
                interpreted_posts
            )
            results["aggregated_summary"] = summary
            logger.info("Aggregation complete")
        except Exception as e:
            error_msg = f"Aggregator Agent failed: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["pipeline_status"] = "aggregator_failed"
            return results

        results["pipeline_status"] = "success"

        logger.info(
            "=" * 50 +
            "\nPipeline Run Complete\n" +
            "=" * 50
        )
        self._print_summary(results)

        return results

    def _print_summary(self, results: dict):
        """Print a readable summary of pipeline results"""
        summary = results.get("aggregated_summary", {})
        polarity = summary.get("polarity", {})
        emotion = summary.get("emotional_tone", {})
        volume = summary.get("volume", {})

        logger.info(
            f"\n{'=' * 40}"
            f"\nPIPELINE SUMMARY"
            f"\n{'=' * 40}"
            f"\nTotal Posts: {volume.get('total_mentions', 0)}"
            f"\nTop Topic: {volume.get('top_topic', 'N/A')}"
            f"\n\nPOLARITY:"
            f"\n  Positive: "
            f"{polarity.get('positive_percent', 0)}%"
            f"\n  Negative: "
            f"{polarity.get('negative_percent', 0)}%"
            f"\n  Neutral:  "
            f"{polarity.get('neutral_percent', 0)}%"
            f"\n\nDOMINANT EMOTION: "
            f"{emotion.get('dominant_emotion', 'Mixed')}"
            f"\n{'=' * 40}"
        )


# Single instance
orchestrator = Orchestrator()