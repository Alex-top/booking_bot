"""Точка входа — бот для записи к специалисту"""

import time
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

from config import config
from handlers.command_handler import CommandHandler
from handlers.booking_handler import BookingHandler
from handlers.keyboards import BookingKeyboards
from utils.logger import BotLogger

# Создаём логгер
logger = BotLogger.get_logger(__name__)


def send_message(vk, user_id: int, text: str) -> bool:
    """Отправляет простое текстовое сообщение"""
    try:
        vk.messages.send(
            user_id=user_id,
            message=text,
            random_id=get_random_id()
        )
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения {user_id}: {e}")
        return False


def send_message_with_keyboard(vk, user_id: int, text: str, keyboard) -> bool:
    """Отправляет сообщение с клавиатурой"""
    try:
        params = {
            "user_id": user_id,
            "message": text,
            "random_id": get_random_id()
        }
        if keyboard:
            params["keyboard"] = keyboard.get_keyboard()
        
        vk.messages.send(**params)
        return True
    except Exception as e:
        logger.error(f"Ошибка отправки с клавиатурой {user_id}: {e}")
        return False


def main():
    logger.info("🚀 Запуск бота для записи...")
    
    # Инициализация VK
    vk_session = VkApi(token=config.VK_TOKEN)
    vk = vk_session.get_api()
    
    # Инициализация обработчиков
    command_handler = CommandHandler(vk)
    booking_handler = BookingHandler(vk)
    
    # Основной цикл
    longpoll = VkBotLongPoll(vk_session, config.VK_GROUP_ID)
    
    logger.info("✅ Бот запущен и слушает сообщения...")
    
    try:
        for event in longpoll.listen():
            # Обработка новых сообщений
            if event.type == VkBotEventType.MESSAGE_NEW:
                message = event.object.message
                user_id = message["from_id"]
                text = message.get("text", "").strip()
                
                if not text:
                    continue
                
                logger.debug(f"Получено сообщение от {user_id}: {text}")
                
                # Команды /start, /help
                if text.startswith("/"):
                    response_text, keyboard = command_handler.handle(user_id, text)
                    if response_text:
                        send_message_with_keyboard(vk, user_id, response_text, keyboard)
                    continue
                
                # Команда /book (обрабатывается отдельно, так как запускает процесс записи)
                if text == "/book":
                    response_text, keyboard = booking_handler.handle_command(user_id, text)
                    send_message_with_keyboard(vk, user_id, response_text, keyboard)
                    continue
                
                # Команда /my_bookings
                if text == "/my_bookings":
                    response_text, keyboard = booking_handler.handle_command(user_id, text)
                    send_message_with_keyboard(vk, user_id, response_text, keyboard)
                    continue
                
                # Если пользователь в процессе записи — направляем в booking_handler
                state = booking_handler.booking_service.get_user_state(user_id)
                if state:
                    # Для простоты: если есть состояние, считаем что это продолжение диалога
                    # Но лучше обрабатывать через callback, а не через текст
                    response = "❓ Пожалуйста, используйте кнопки для навигации."
                    send_message(vk, user_id, response)
                else:
                    # Если не команда и не процесс записи — показываем меню
                    response_text = "👋 Я бот для записи. Используйте /start для меню."
                    send_message_with_keyboard(vk, user_id, response_text, BookingKeyboards.get_main_keyboard())
            
            # Обработка нажатий на кнопки (callback)
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                user_id = event.object.user_id
                payload = event.object.payload
                
                logger.debug(f"Получен callback от {user_id}: {payload}")
                
                # Отвечаем на callback (убираем "часики" на кнопке)
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=user_id,
                    peer_id=event.object.peer_id
                )
                
                # Обрабатываем callback через booking_handler
                response_text, keyboard = booking_handler.handle_callback(user_id, payload)
                
                if response_text:
                    if keyboard:
                        send_message_with_keyboard(vk, user_id, response_text, keyboard)
                    else:
                        send_message(vk, user_id, response_text)
    
    except KeyboardInterrupt:
        logger.info("🛑 Остановка бота...")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("👋 Бот остановлен")


if __name__ == "__main__":
    main()