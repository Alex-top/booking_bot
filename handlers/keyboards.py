"""Создание клавиатур для бота записи"""

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from typing import List, Dict, Any
from datetime import datetime, timedelta


class BookingKeyboards:
    """Все клавиатуры для бота записи"""
    
    @staticmethod
    def get_main_keyboard() -> VkKeyboard:
        """
        Главная клавиатура с основными действиями.
        Показывается после /start
        """
        keyboard = VkKeyboard(one_time=False, inline=False)
        keyboard.add_button('📅 Записаться', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('📋 Мои записи', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('❓ Помощь', color=VkKeyboardColor.SECONDARY)
        return keyboard
    
    @staticmethod
    @staticmethod
    def get_services_keyboard(services: List[Dict[str, Any]]) -> VkKeyboard:
        """
        Инлайн-клавиатура для выбора услуги.
        Кнопки размещаем по 2 в строке.
        """
        keyboard = VkKeyboard(one_time=False, inline=True)
        
        for i, service in enumerate(services):
            keyboard.add_callback_button(
                label=f"{service['name']} — {service['price']} ₽",
                color=VkKeyboardColor.PRIMARY,
                payload={'action': 'select_service', 'service_id': service['id']}
            )
            # После каждых 2 кнопок — новая строка
            if (i + 1) % 2 == 0 and i + 1 < len(services):
                keyboard.add_line()
        
        keyboard.add_line()
        keyboard.add_callback_button(
            label='🔙 На главную',
            color=VkKeyboardColor.SECONDARY,
            payload={'action': 'back_to_main'}
        )
        
        return keyboard
    
    @staticmethod
    def get_masters_keyboard(masters: List[Dict[str, Any]]) -> VkKeyboard:
        """
        Инлайн-клавиатура для выбора мастера.
        """
        keyboard = VkKeyboard(one_time=False, inline=True)
        
        for master in masters:
            label = f"👤 {master['name']}"
            if master.get('description'):
                label += f" ({master['description'][:30]})"
            keyboard.add_callback_button(
                label=label,
                color=VkKeyboardColor.PRIMARY,
                payload={'action': 'select_master', 'master_id': master['id']}
            )
            keyboard.add_line()
        
        keyboard.add_callback_button(
            label='🔙 На главную',
            color=VkKeyboardColor.SECONDARY,
            payload={'action': 'back_to_main'}
        )
        
        return keyboard
    
    @staticmethod
    def get_dates_keyboard(days: int = 5) -> VkKeyboard:
        """
        Инлайн-клавиатура для выбора даты.
        Показывает дни на ближайшие `days` дней (максимум 5, чтобы уложиться в лимит строк).
        """
        keyboard = VkKeyboard(one_time=False, inline=True)
        
        today = datetime.now()
        
        # Добавляем кнопки с датами (по 2 в строке, чтобы уложиться в 3 строки)
        row_buttons = []
        max_days = min(days, 5)  # Не больше 5 дней
        
        for i in range(max_days):
            date = today + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            display_str = date.strftime('%d.%m (%a)')
            
            if i == 0:
                display_str = f"Сегодня ({display_str})"
            elif i == 1:
                display_str = f"Завтра ({display_str})"
            else:
                display_str = display_str
            
            keyboard.add_callback_button(
                label=display_str,
                color=VkKeyboardColor.PRIMARY,
                payload={'action': 'select_date', 'date': date_str}
            )
            # После каждых 2 кнопок — новая строка
            if (i + 1) % 2 == 0 and i + 1 < max_days:
                keyboard.add_line()
        
        keyboard.add_line()
        keyboard.add_callback_button(
            label='🔙 На главную',
            color=VkKeyboardColor.SECONDARY,
            payload={'action': 'back_to_main'}
        )
        
        return keyboard
    
    @staticmethod
    def get_time_slots_keyboard(slots: List[Dict[str, Any]]) -> VkKeyboard:
        """
        Инлайн-клавиатура для выбора времени из доступных слотов.
        Кнопки с временем размещаем по 3 в строке.
        """
        keyboard = VkKeyboard(one_time=False, inline=True)
        
        if not slots:
            keyboard.add_callback_button(
                label="❌ Нет свободного времени",
                color=VkKeyboardColor.SECONDARY,
                payload={'action': 'no_slots'}
            )
        else:
            for i, slot in enumerate(slots):
                start_time = slot['start_time']
                if ' ' in start_time:
                    time_str = start_time.split(' ')[1][:5]
                else:
                    time_str = start_time[:5]
                
                keyboard.add_callback_button(
                    label=f"🕐 {time_str}",
                    color=VkKeyboardColor.POSITIVE,
                    payload={'action': 'select_time', 'slot_id': slot['id']}
                )
                # После каждых 3 кнопок — новая строка
                if (i + 1) % 3 == 0 and i + 1 < len(slots):
                    keyboard.add_line()
        
        keyboard.add_line()
        keyboard.add_callback_button(
            label='🔙 Назад к датам',
            color=VkKeyboardColor.SECONDARY,
            payload={'action': 'back_to_dates'}
        )
        keyboard.add_callback_button(
            label='🔙 На главную',
            color=VkKeyboardColor.SECONDARY,
            payload={'action': 'back_to_main'}
        )
        
        return keyboard
    
    @staticmethod
    def get_confirm_keyboard(
        service_name: str,
        master_name: str,
        date_str: str,
        time_str: str,
        price: int,
        slot_id: int
    ) -> VkKeyboard:
        """
        Инлайн-клавиатура для подтверждения записи.
        """
        keyboard = VkKeyboard(one_time=False, inline=True)
        
        # Информационная кнопка (не нажимается)
        keyboard.add_callback_button(
            label=f"✅ Подтвердить запись",
            color=VkKeyboardColor.POSITIVE,
            payload={'action': 'confirm_booking', 'slot_id': slot_id}
        )
        keyboard.add_line()
        keyboard.add_callback_button(
            label='❌ Отменить',
            color=VkKeyboardColor.NEGATIVE,
            payload={'action': 'cancel_booking'}
        )
        
        return keyboard
    
    @staticmethod
    def get_user_bookings_keyboard(bookings: List[Dict[str, Any]]) -> VkKeyboard:
        """
        Инлайн-клавиатура для списка записей (отмена конкретной).
        Показывается вместе со списком.
        """
        keyboard = VkKeyboard(one_time=False, inline=True)
        
        for booking in bookings:
            # Извлекаем дату и время из start_time
            start_time = booking['start_time']
            if ' ' in start_time:
                date_part = start_time.split(' ')[0]
                time_part = start_time.split(' ')[1][:5]
                date_str = datetime.strptime(date_part, '%Y-%m-%d').strftime('%d.%m')
            else:
                date_str = start_time[:10]
                time_part = "?"
            
            keyboard.add_callback_button(
                label=f"❌ Отменить {date_str} {time_part} — {booking['service_name']}",
                color=VkKeyboardColor.NEGATIVE,
                payload={'action': 'cancel_booking_by_id', 'booking_id': booking['id']}
            )
            keyboard.add_line()
        
        keyboard.add_callback_button(
            label='🔙 На главную',
            color=VkKeyboardColor.SECONDARY,
            payload={'action': 'back_to_main'}
        )
        
        return keyboard
    
    @staticmethod
    def get_empty_keyboard() -> VkKeyboard:
        """Пустая клавиатура (убирает кнопки)"""
        return VkKeyboard(one_time=False, inline=False)