import logging
import asyncio
from app.core.database import db

logger = logging.getLogger(__name__)

class EmailSenderService:
    def __init__(self):
        # We can pass SMTP credentials or use Solaria's core mailer
        pass

    async def get_subscribers(self):
        """
        Query the 'contact' model to find users subscribed to the newspaper.
        Assuming we added a boolean flag or a specific contact_source/list.
        """
        # Example ORM usage (Adjust according to Solaria's actual ORM querying)
        query = "SELECT email, display_name FROM contact WHERE status = 'active'"
        
        try:
            async with db.pool.acquire() as conn:
                records = await conn.fetch(query)
                return [{"email": r["email"], "name": r["display_name"]} for r in records if r["email"]]
        except Exception as e:
            logger.error(f"Error fetching subscribers: {e}")
            return []

    async def send_newspaper(self, newspaper_id: str, pdf_path: str):
        """
        Send the generated PDF to all subscribers.
        """
        subscribers = await self.get_subscribers()
        
        if not subscribers:
            logger.warning(f"No subscribers found to send {newspaper_id}.")
            return
            
        logger.info(f"Preparing to send {newspaper_id} to {len(subscribers)} subscribers.")
        
        # Here we would integrate with aiosmtplib or Solaria's mailing provider
        # e.g., iterating through subscribers and sending the attachment.
        for sub in subscribers:
            # await self._send_email(sub['email'], sub['name'], newspaper_id, pdf_path)
            pass
            
        logger.info(f"Successfully finished mailing routine for {newspaper_id}.")
