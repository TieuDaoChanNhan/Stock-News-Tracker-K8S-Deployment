import os
import json
import asyncio
from typing import Dict, Any, Optional
from aio_pika import connect_robust, IncomingMessage
from aio_pika.exceptions import AMQPException
import logging

from app.database import SessionLocal
from app.services.watchlist_service import check_and_process_article_notification

logger = logging.getLogger(__name__)

class EventConsumer:
    def __init__(self, rabbitmq_url: Optional[str] = None):
        # Đọc từ environment variable, fallback to service name
        self.rabbitmq_url = (
            rabbitmq_url or 
            os.getenv('RABBITMQ_URL') or 
            os.getenv('AMQP_URL') or 
            "amqp://guest:guest@rabbitmq:5672/"  
        )
        self.connection = None
        self.channel = None
        logger.info(f"🔧 EventConsumer using RabbitMQ URL: {self.rabbitmq_url}")
        
    async def connect(self):
        """Kết nối đến RabbitMQ"""
        try:
            self.connection = await connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            
            # Declare exchange và queue
            exchange = await self.channel.declare_exchange(
                "article_events", 
                type="topic",
                durable=True
            )
            
            # Queue cho notification service
            queue = await self.channel.declare_queue(
                "notification_queue",
                durable=True
            )
            
            # Bind queue với routing key
            await queue.bind(exchange, "article.created")
            
            logger.info("✅ Connected to RabbitMQ for event consuming")
            return queue
            
        except AMQPException as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise
    
    async def process_article_created_event(self, message: IncomingMessage):
        """Xử lý event article_created"""
        try:
            # Parse message
            event_data = json.loads(message.body.decode('utf-8'))
            
            logger.info(f"📥 Received article_created event: {event_data['article_id']}")
            
            # Validate event
            if event_data.get("event_type") != "article_created":
                logger.warning(f"⚠️ Unknown event type: {event_data.get('event_type')}")
                return
            
            # Process notification
            await check_and_process_article_notification(event_data)
            
            logger.info(f"✅ Processed article_created event: {event_data['article_id']}")
            
        except Exception as e:
            logger.error(f"❌ Error processing article_created event: {e}")
            raise
    
    async def start_consuming(self):
        """Bắt đầu consume events"""
        try:
            queue = await self.connect()
            
            # Set up message processing
            await queue.consume(self.process_article_created_event)
            
            logger.info("🔄 Started consuming events...")
            
            # Keep running
            try:
                await asyncio.Future()  # Run forever
            except KeyboardInterrupt:
                logger.info("⏹️ Stopping event consumer...")
                
        except Exception as e:
            logger.error(f"❌ Error in event consumer: {e}")
            raise
    
    async def close(self):
        """Đóng kết nối"""
        if self.connection:
            await self.connection.close()
            logger.info("🔌 Disconnected from RabbitMQ")

# Singleton instance
event_consumer = EventConsumer()
