import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def default_log_handler(log_data: dict):
    """
    Default async log handler that shows detailed server logs.
    Can be overridden by passing a custom handler to Stagehand's constructor.
    """
    if "type" in log_data:
        log_type = log_data["type"]
        data = log_data.get("data", {})
        
        if log_type == "system":
            logger.info(f"🔧 SYSTEM: {data}")
        elif log_type == "log":
            logger.info(f"📝 LOG: {data}")
        else:
            logger.info(f"ℹ️ OTHER [{log_type}]: {data}")
    else:
        # Fallback for any other format
        logger.info(f"🤖 RAW LOG: {log_data}") 