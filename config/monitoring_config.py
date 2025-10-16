from dataclasses import dataclass, field
from typing import Dict

@dataclass
class MonitoringConfig:
    """
    Holds all configuration parameters for the data source monitoring service.
    """
    # A dictionary mapping a source name (e.g., 'rbi') to its RSS feed URL.
    # This makes it easy to add or remove sources without changing the code.
    rss_feeds: Dict[str, str] = field(default_factory=lambda: {
        "rbi": "https://rbi.org.in/Scripts/Rss.aspx",
        "sebi": "https://www.sebi.gov.in/sebirss.xml",
        # You can easily add more sources here
        # "example_source": "https://example.com/rss"
    })

    # The interval, in seconds, at which the monitor should check the RSS feeds for new content.
    # 300 seconds = 5 minutes.
    check_interval: int = 300
