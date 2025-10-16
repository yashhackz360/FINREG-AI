import time
import logging
import feedparser
from datetime import datetime
from .kafka_producer import RegulatoryDataProducer
from .rss_monitor import RSSMonitorState

class RegulatoryMonitor:
    """
    The main service that continuously monitors regulatory RSS feeds.
    It runs in a loop, checking for new content and producing it to Kafka.
    """
    def __init__(self, kafka_producer: RegulatoryDataProducer, rss_feeds: dict, check_interval: int):
        self.producer = kafka_producer
        self.rss_feeds = rss_feeds
        self.check_interval = check_interval
        self.state_manager = RSSMonitorState()
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Starts the infinite monitoring loop."""
        self.logger.info("Starting regulatory monitor...")
        
        # --- TROUBLESHOOTING MODIFICATION ---
        # Clear the state on startup for demonstration to ensure messages are always sent.
        # In a real production environment, you would remove this line.
        self.logger.warning("DEVELOPMENT MODE: Clearing RSS state to re-process all items.")
        self.state_manager.clear_state()
        # --- END OF MODIFICATION ---

        while True:
            for source, url in self.rss_feeds.items():
                try:
                    self.logger.info(f"Checking RSS feed for '{source}' at {url}")
                    # Parse the RSS feed URL
                    feed = feedparser.parse(url)
                    if feed.bozo:
                         self.logger.warning(f"Warning: Ill-formed XML for feed '{source}'. Attempting to parse anyway.")

                    # Iterate through entries in reverse to process oldest first
                    for entry in reversed(feed.entries):
                        # Use the state manager to check if the item is new
                        if self.state_manager.is_new(entry):
                            self.logger.info(f"New content found from '{source}': {entry.get('title')}")
                            # Construct the message payload
                            message = {
                                'source': source,
                                'title': entry.get('title', 'No Title'),
                                'url': entry.get('link'),
                                'published': entry.get('published', datetime.now().isoformat()),
                                'timestamp': datetime.now().isoformat()
                            }
                            # Send the new content alert to Kafka
                            self.producer.send_update('regulatory-updates', message)
                except Exception as e:
                    self.logger.error(f"Failed to process feed for '{source}': {e}")

            self.logger.info(f"Monitor sleeping for {self.check_interval} seconds.")
            time.sleep(self.check_interval)