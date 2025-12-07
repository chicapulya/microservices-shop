import redis
import json
import requests
import os
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Redis клиент для межсервисного взаимодействия
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

class EventBus:
    """Простая система событий через Redis Pub/Sub"""

    @staticmethod
    def publish(event_type: str, data: Dict[str, Any]):
        """Публикация события"""

        try:
            event_data = {
                'type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }

            redis_client.publish('events', json.dumps(event_data))
            logger.info(f"Published event: {event_type}")
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")

    @staticmethod
    def subscribe(callback):
        """Подписка на события"""
        
        # 1. Получаем клиент PubSub от Redis
        pubsub = redis_client.pubsub() 
        # 2. Подписываемся на канал 'events'
        pubsub.subscribe('events') 
        
        # 3. Начинаем бесконечный цикл для прослушивания сообщений
        for message in pubsub.listen():
            # Проверяем, что это сообщение, а не служебная информация (например, об успешной подписке)
            if message['type'] == 'message': 
                try:
                    # Декодируем и парсим JSON-данные из сообщения
                    event_data = json.loads(message['data']) 
                    
                    # Вызываем функцию обратного вызова (callback) с данными события
                    callback(event_data)
                    
                except Exception as e:
                    logger.error(f"Failed to process event: {e}")

class ServiceCommunication:
    """Класс для HTTP взаимодействия между сервисами"""

    BASE_URLS = {
        'user-service': os.environ.get('USER_SERVICE_URL', 'http://localhost:8004'),
        'product-service': os.environ.get('PRODUCT_SERVICE_URL', 'http://localhost:8001'),
        'cart-service': os.environ.get('CART_SERVICE_URL', 'http://localhost:8002'),
        'order-service': os.environ.get('ORDER_SERVICE_URL', 'http://localhost:8003')
    }

    @classmethod
    def make_request(cls, service: str, endpoint: str, method: str = 'GET',
                     data: Optional[Dict] = None, headers: Optional[Dict] = None):
        """Выполнение HTTP запроса к другому сервису"""
        
        try:
            url = f"{cls.BASE_URLS[service]}{endpoint}"
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers or {},
                timeout=10
            )
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Service communication error: {service} - {e}")
            return None
        
def get_user_from_token(token: str) -> Optional[Dict]:
    """Получение информации о пользователе по токену"""
    headers = {'Authorization': f'Bearer {token}'}
    response = ServiceCommunication.make_request(
        'user-service', '/api/users/profile/', 'GET', headers=headers
    )

    if response and response.status_code == 200:
        return response.json()

    return None