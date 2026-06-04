"""Обработчик команд для бота записи"""

from typing import Tuple, Optional, Any
from handlers.keyboards import BookingKeyboards


class CommandHandler:
    """Обработчик основных команд бота"""
    
    def __init__(self, vk):
        self.vk = vk
    
    def handle(self, user_id: int, command: str) -> Tuple[str, Optional[Any]]:
        """
        Обрабатывает команды и возвращает (текст_ответа, клавиатура)
        """
        command = command.lower().strip()
        
        if command == "/start":
            return self._get_start_message(), BookingKeyboards.get_main_keyboard()
        
        elif command == "/help":
            return self._get_help_message(), BookingKeyboards.get_main_keyboard()
        
        else:
            return None, None  # Неизвестная команда — не отвечаем
    
    def _get_start_message(self) -> str:
        return """👋 *Бот для записи к специалисту*

Я помогу вам записаться на услуги красоты.

📌 *Доступные команды:*
/book — записаться к специалисту
/my_bookings — посмотреть мои записи
/help — эта справка

💡 Выберите действие на клавиатуре ниже."""
    
    def _get_help_message(self) -> str:
        return """📖 *Справка*

🔹 *Записаться:* нажмите «📅 Записаться» или введите команду /book
🔹 *Мои записи:* нажмите «📋 Мои записи» или введите /my_bookings
🔹 *Отменить запись:* найдите запись в /my_bookings и нажмите кнопку «Отменить»

Если у вас возникли проблемы — напишите администратору."""