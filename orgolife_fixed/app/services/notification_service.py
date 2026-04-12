"""
Notification service — manages system alerts and email triggers.
"""
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def create_notification(user_id: str, title: str, message: str, type: str = "info") -> dict:
    """
    Log a notification to the database and queue email (placeholder).
    """
    # In a real app, this would insert into a 'notifications' table.
    # For now, we will log it and provide a success response.
    # supabase = get_database()
    # supabase.table("notifications").insert({...}).execute()
    
    logger.info(f"NOTIFICATION for {user_id}: [{type.upper()}] {title} - {message}")
    
    # Placeholder for Email Service
    # await send_email_async(email, title, message)
    
    return {
        "status": "queued",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

async def notify_match_found(donor_user_id: str, receiver_user_id: str, organ: str):
    """Specific trigger for matches."""
    await create_notification(
        user_id=donor_user_id,
        title="LIFESAVER: Match Found!",
        message=f"A potential match for your {organ} registration has been identified. Our facility will contact you soon.",
        type="success"
    )
    await create_notification(
        user_id=receiver_user_id,
        title="HOPE: Match Identified!",
        message=f"A verified donor for {organ} has been matched with your profile. Please check your dashboard.",
        type="success"
    )
