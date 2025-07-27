import os
import json
import asyncio
from typing import Optional
from aio_pika import connect_robust, Message
from aio_pika.exceptions import AMQPException
import logging

logger = logging.getLogger(__name__)

class EventPublisher:
    def __init__(self, rabbitmq_url: Optional[str] = None):
        # Đọc từ environment variable, fallback to service name
        self.rabbitmq_url = (
            rabbitmq_url or 
            os.getenv('RABBITMQ_URL') or 
            os.getenv('AMQP_URL') or 
            "amqp://guest:guest@rabbitmq:5672/"  #
        )
        self.connection = None
        self.channel = None
        logger.info(f"🔧 EventPublisher using RabbitMQ URL: {self.rabbitmq_url}")
        
    async def connect(self):
        """Kết nối đến RabbitMQ"""
        try:
            self.connection = await connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            logger.info("✅ Connected to RabbitMQ")
        except AMQPException as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            raise
    
    async def close(self):
        """Đóng kết nối"""
        if self.connection:
            await self.connection.close()
            logger.info("🔌 Disconnected from RabbitMQ")
    
    async def publish_article_created(self, event_data: dict):
        """Publish event khi có article mới"""
        try:
            if not self.channel:
                await self.connect()
            
            # Declare exchange và queue
            exchange = await self.channel.declare_exchange(
                "article_events", 
                type="topic",
                durable=True
            )
            
            # Publish message
            message = Message(
                json.dumps(event_data, ensure_ascii=False, default=str).encode('utf-8'),
                content_type="application/json",
                delivery_mode=2  # Persistent message
            )
            
            await exchange.publish(
                message,
                routing_key="article.created"
            )
            
            logger.info(f"📤 Published article_created event: {event_data['article_id']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to publish event: {e}")
            raise

# Singleton instance
event_publisher = EventPublisher()
