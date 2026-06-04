"""Бизнес-логика бота записи: поиск слотов, создание записей, работа с состояниями"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from storage.booking_repository import booking_repo


class BookingService:
    """Сервис для управления записью к специалисту"""
    
    # Состояния диалога
    STATE_SELECT_SERVICE = "select_service"
    STATE_SELECT_MASTER = "select_master"
    STATE_SELECT_DATE = "select_date"
    STATE_SELECT_TIME = "select_time"
    STATE_CONFIRM = "confirm"
    
    def __init__(self):
        self.user_states = {}  # user_id -> текущее состояние
        self.user_temp_data = {}  # user_id -> временные данные (выбранная услуга, мастер и т.д.)
    
    def get_user_state(self, user_id: int) -> Optional[str]:
        """Получить текущее состояние пользователя"""
        return self.user_states.get(user_id)
    
    def set_user_state(self, user_id: int, state: str):
        """Установить состояние пользователя"""
        if state is None:
            # Очищаем состояние
            if user_id in self.user_states:
                del self.user_states[user_id]
            if user_id in self.user_temp_data:
                del self.user_temp_data[user_id]
        else:
            self.user_states[user_id] = state
    
    def get_temp_data(self, user_id: int, key: str = None):
        """Получить временные данные пользователя"""
        data = self.user_temp_data.get(user_id, {})
        if key:
            return data.get(key)
        return data
    
    def set_temp_data(self, user_id: int, key: str, value: Any):
        """Сохранить временные данные пользователя"""
        if user_id not in self.user_temp_data:
            self.user_temp_data[user_id] = {}
        self.user_temp_data[user_id][key] = value
    
    def clear_temp_data(self, user_id: int):
        """Очистить временные данные"""
        if user_id in self.user_temp_data:
            del self.user_temp_data[user_id]
    
    # ========== БИЗНЕС-МЕТОДЫ ==========
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Получить все услуги"""
        return booking_repo.get_all_services()
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Получить услугу по ID"""
        return booking_repo.get_service_by_id(service_id)
    
    def get_all_masters(self) -> List[Dict[str, Any]]:
        """Получить всех мастеров"""
        return booking_repo.get_all_masters()
    
    def get_free_slots_by_date(self, master_id: int, date_str: str) -> List[Dict[str, Any]]:
        """Получить свободные слоты мастера на дату"""
        return booking_repo.get_free_slots_by_master_and_date(master_id, date_str)
    
    def get_available_dates(self, master_id: int, days_ahead: int = 7) -> List[str]:
        """
        Получить список дат, на которых есть хотя бы один свободный слот.
        Возвращает список строк в формате 'YYYY-MM-DD'
        """
        dates = []
        today = datetime.now()
        
        for i in range(days_ahead):
            date = today + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            slots = self.get_free_slots_by_date(master_id, date_str)
            if slots:
                dates.append(date_str)
        
        return dates
    
    def create_booking(self, user_id: int, slot_id: int) -> Optional[Dict[str, Any]]:
        """
        Создать запись.
        Возвращает информацию о созданной записи или None.
        """
        # Получаем информацию о слоте
        slot = booking_repo.get_slot_by_id(slot_id)
        if not slot or not slot['is_available']:
            return None
        
        # Получаем временные данные пользователя
        service_id = self.get_temp_data(user_id, 'service_id')
        master_id = self.get_temp_data(user_id, 'master_id')
        
        if not service_id or not master_id:
            return None
        
        # Блокируем слот и создаём запись в одной транзакции
        if booking_repo.lock_slot(slot_id):
            booking_id = booking_repo.create_booking(user_id, slot_id, service_id, master_id)
            
            # Очищаем состояние пользователя
            self.set_user_state(user_id, None)
            
            # Возвращаем информацию о записи
            service = self.get_service_by_id(service_id)
            master = booking_repo.get_master_by_id(master_id)
            
            return {
                'booking_id': booking_id,
                'service_name': service['name'] if service else '?',
                'master_name': master['name'] if master else '?',
                'start_time': slot['start_time'],
                'end_time': slot['end_time'],
                'price': service['price'] if service else 0
            }
        
        return None
    
    def get_user_bookings(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все активные записи пользователя"""
        return booking_repo.get_user_bookings(user_id)
    
    def cancel_booking(self, user_id: int, booking_id: int) -> bool:
        """Отменить запись"""
        return booking_repo.cancel_booking(booking_id, user_id)
    
    def format_booking_message(self, booking: Dict[str, Any]) -> str:
        """Форматирует запись для отображения пользователю"""
        start_time = booking['start_time']
        # Парсим дату и время
        if ' ' in start_time:
            date_part = start_time.split(' ')[0]
            time_part = start_time.split(' ')[1][:5]
            date_obj = datetime.strptime(date_part, '%Y-%m-%d')
            date_str = date_obj.strftime('%d.%m.%Y')
        else:
            date_str = start_time[:10]
            time_part = "?"
        
        return (f"📅 {date_str} в {time_part}\n"
                f"💇 {booking['service_name']}\n"
                f"👤 Мастер: {booking['master_name']}\n"
                f"💰 {booking.get('price', '?')} ₽")


# Создаём единственный экземпляр сервиса
booking_service = BookingService()