"""Конечный автомат для процесса записи к специалисту"""

from typing import Tuple, Optional, Dict, Any
from datetime import datetime

from services.booking_service import booking_service
from handlers.keyboards import BookingKeyboards
from utils.logger import BotLogger
from services.booking_service import booking_service

logger = BotLogger.get_logger(__name__)


class BookingHandler:
    """Обработчик диалога записи (конечный автомат)"""
    
    def __init__(self, vk):
        self.vk = vk
        self.booking_service = booking_service
    
    def handle_callback(self, user_id: int, payload: Dict[str, Any]) -> Tuple[str, Optional[Any]]:
        """
        Обрабатывает нажатия на кнопки (callback).
        Возвращает (текст_ответа, клавиатура)
        """
        action = payload.get('action')
        logger.debug(f"BookingHandler callback: user={user_id}, action={action}")
        
        # Обработка навигации
        if action == 'back_to_main':
            self.booking_service.set_user_state(user_id, None)
            return self._get_welcome_message(), BookingKeyboards.get_main_keyboard()
        
        if action == 'back_to_dates':
            master_id = self.booking_service.get_temp_data(user_id, 'master_id')
            if master_id:
                self.booking_service.set_user_state(user_id, booking_service.STATE_SELECT_DATE)
                return self._show_dates(user_id, master_id)
            else:
                self.booking_service.set_user_state(user_id, None)
                return self._get_welcome_message(), BookingKeyboards.get_main_keyboard()
        
        # Обработка выбора услуги
        if action == 'select_service':
            service_id = payload.get('service_id')
            service = self.booking_service.get_service_by_id(service_id)
            if service:
                self.booking_service.set_temp_data(user_id, 'service_id', service_id)
                self.booking_service.set_user_state(user_id, booking_service.STATE_SELECT_MASTER)
                return self._show_masters(user_id)
            else:
                return "❌ Услуга не найдена. Попробуйте ещё раз.", BookingKeyboards.get_main_keyboard()
        
        # Обработка выбора мастера
        if action == 'select_master':
            master_id = payload.get('master_id')
            master = self.booking_service.get_master_by_id(master_id)
            if master:
                self.booking_service.set_temp_data(user_id, 'master_id', master_id)
                self.booking_service.set_user_state(user_id, self.booking_service.STATE_SELECT_DATE)
                return self._show_dates(user_id, master_id)
            else:
                return "❌ Мастер не найден. Попробуйте ещё раз.", BookingKeyboards.get_main_keyboard()
        
        # Обработка выбора даты
        if action == 'select_date':
            date_str = payload.get('date')
            master_id = self.booking_service.get_temp_data(user_id, 'master_id')
            if master_id and date_str:
                self.booking_service.set_temp_data(user_id, 'selected_date', date_str)
                self.booking_service.set_user_state(user_id, self.booking_service.STATE_SELECT_TIME)
                return self._show_time_slots(user_id, master_id, date_str)
            else:
                return "❌ Ошибка выбора даты. Попробуйте ещё раз.", BookingKeyboards.get_main_keyboard()
        
        # Обработка выбора времени
        if action == 'select_time':
            slot_id = payload.get('slot_id')
            if slot_id:
                self.booking_service.set_temp_data(user_id, 'selected_slot_id', slot_id)
                self.booking_service.set_user_state(user_id, self.booking_service.STATE_CONFIRM)
                return self._show_confirmation(user_id, slot_id)
            else:
                return "❌ Ошибка выбора времени. Попробуйте ещё раз.", BookingKeyboards.get_main_keyboard()
        
        # Обработка подтверждения записи
        if action == 'confirm_booking':
            slot_id = payload.get('slot_id')
            if slot_id:
                result = self.booking_service.create_booking(user_id, slot_id)
                if result:
                    message = (f"✅ Вы успешно записаны!\n\n"
                               f"{self.booking_service.format_booking_message(result)}\n\n"
                               f"📍 Приходите вовремя. Отменить запись можно командой /my_bookings")
                    return message, BookingKeyboards.get_main_keyboard()
                else:
                    return "❌ К сожалению, это время уже занято. Попробуйте выбрать другое.", BookingKeyboards.get_main_keyboard()
            else:
                return "❌ Ошибка подтверждения. Попробуйте ещё раз.", BookingKeyboards.get_main_keyboard()
        
        # Обработка отмены записи по ID (из /my_bookings)
        if action == 'cancel_booking_by_id':
            booking_id = payload.get('booking_id')
            if booking_id and self.booking_service.cancel_booking(user_id, booking_id):
                return "✅ Запись успешно отменена. Слот освобождён.", BookingKeyboards.get_main_keyboard()
            else:
                return "❌ Не удалось отменить запись. Возможно, она уже была отменена.", BookingKeyboards.get_main_keyboard()
        
        # Отмена процесса записи
        if action == 'cancel_booking':
            self.booking_service.set_user_state(user_id, None)
            return "❌ Запись отменена. Если передумаете — начните заново.", BookingKeyboards.get_main_keyboard()
        
        # Пустые слоты
        if action == 'no_slots':
            return "😔 На выбранную дату нет свободного времени. Попробуйте другую дату.", BookingKeyboards.get_dates_keyboard()
        
        return "❓ Неизвестная команда. Начните запись заново командой /book", BookingKeyboards.get_main_keyboard()
    
    def handle_command(self, user_id: int, command: str) -> Tuple[str, Optional[Any]]:
        """
        Обрабатывает команды: /book, /my_bookings
        """
        print(f"🔍 handle_command получил: {command}")

        if command == "/book":
            self.booking_service.set_user_state(user_id, self.booking_service.STATE_SELECT_SERVICE)
            return self._show_services(user_id)
        
        elif command == "/my_bookings":
            return self._show_user_bookings(user_id)
        
        else:
            return "❌ Неизвестная команда", None
    
    # ========== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ==========
    
    def _get_welcome_message(self) -> str:
        return """👋 Добро пожаловать в бот записи!

📌 *Доступные команды:*
/book — записаться к специалисту
/my_bookings — мои записи

💡 Выберите действие на клавиатуре ниже."""
    
    def _show_services(self, user_id: int) -> Tuple[str, Optional[Any]]:
        """Показать список услуг"""
        print("🔍 _show_services вызван")

        services = self.booking_service.get_all_services()

        print(f"🔍 Получено услуг: {len(services)}")
        
        if not services:
            return "😔 Услуги временно недоступны. Попробуйте позже.", None
        
        keyboard = BookingKeyboards.get_services_keyboard(services)
        return "📋 *Выберите услугу:*", keyboard
    
    def _show_masters(self, user_id: int) -> Tuple[str, Optional[Any]]:
        """Показать список мастеров"""
        masters = self.booking_service.get_all_masters()
        if not masters:
            return "😔 Мастера временно недоступны. Попробуйте позже.", None
        
        keyboard = BookingKeyboards.get_masters_keyboard(masters)
        return "💇 *Выберите мастера:*", keyboard
    
    def _show_dates(self, user_id: int, master_id: int) -> Tuple[str, Optional[Any]]:
        """Показать доступные даты для мастера"""
        dates = self.booking_service.get_available_dates(master_id, 7)
        
        if not dates:
            return "😔 На ближайшие дни нет свободных слотов. Попробуйте позже.", BookingKeyboards.get_main_keyboard()
        
        keyboard = BookingKeyboards.get_dates_keyboard(len(dates))
        return "📅 *Выберите дату:*", keyboard
    
    def _show_time_slots(self, user_id: int, master_id: int, date_str: str) -> Tuple[str, Optional[Any]]:
        """Показать свободные слоты на выбранную дату"""
        slots = self.booking_service.get_free_slots_by_date(master_id, date_str)
        
        if not slots:
            return "😔 На эту дату нет свободного времени. Выберите другую дату.", BookingKeyboards.get_dates_keyboard()
        
        keyboard = BookingKeyboards.get_time_slots_keyboard(slots)
        date_display = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d.%m.%Y')
        return f"🕐 *Выберите время на {date_display}:*", keyboard
    
    def _show_confirmation(self, user_id: int, slot_id: int) -> Tuple[str, Optional[Any]]:
        """Показать подтверждение записи"""
        slot = self.booking_service.get_slot_by_id(slot_id)
        if not slot or not slot['is_available']:
            return "😔 Это время уже занято. Попробуйте выбрать другое.", BookingKeyboards.get_main_keyboard()
        
        service_id = self.booking_service.get_temp_data(user_id, 'service_id')
        master_id = self.booking_service.get_temp_data(user_id, 'master_id')
        
        service = self.booking_service.get_service_by_id(service_id) if service_id else None
        master = self.booking_service.get_master_by_id(master_id) if master_id else None
        
        if not service or not master:
            return "❌ Ошибка: не выбрана услуга или мастер. Начните запись заново командой /book", BookingKeyboards.get_main_keyboard()
        
        # Парсим дату и время
        start_time = slot['start_time']
        if ' ' in start_time:
            date_part = start_time.split(' ')[0]
            time_part = start_time.split(' ')[1][:5]
            date_obj = datetime.strptime(date_part, '%Y-%m-%d')
            date_str = date_obj.strftime('%d.%m.%Y')
        else:
            date_str = start_time[:10]
            time_part = "?"
        
        message = (f"📝 *Подтвердите запись*\n\n"
                   f"💇 Услуга: {service['name']}\n"
                   f"💰 Цена: {service['price']} ₽\n"
                   f"👤 Мастер: {master['name']}\n"
                   f"📅 Дата: {date_str}\n"
                   f"🕐 Время: {time_part}\n\n"
                   f"✅ Нажмите «Подтвердить», чтобы завершить запись.")
        
        keyboard = BookingKeyboards.get_confirm_keyboard(
            service['name'], master['name'], date_str, time_part, service['price'], slot_id
        )
        
        return message, keyboard
    
    def _show_user_bookings(self, user_id: int) -> Tuple[str, Optional[Any]]:
        """Показать все записи пользователя"""
        bookings = self.booking_service.get_user_bookings(user_id)
        
        if not bookings:
            return "📭 У вас нет активных записей.\n\nЗаписаться можно командой /book", BookingKeyboards.get_main_keyboard()
        
        message = "📋 *Ваши записи:*\n\n"
        for i, booking in enumerate(bookings, 1):
            message += f"{i}. {self.booking_service.format_booking_message(booking)}\n\n"
        
        message += "❌ Чтобы отменить запись, нажмите на кнопку под списком."
        
        keyboard = BookingKeyboards.get_user_bookings_keyboard(bookings)
        return message, keyboard