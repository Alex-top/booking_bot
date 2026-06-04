"""Репозиторий для работы с БД: услуги, мастера, слоты, записи"""

import sqlite3
from typing import List, Dict, Optional, Any
from datetime import datetime
from config import config


class BookingRepository:
    """Все операции с базой данных бота записи"""
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
    
    def _get_connection(self):
        """Возвращает соединение с БД"""
        return sqlite3.connect(self.db_path)
    
    # ========== УСЛУГИ ==========
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Получить список всех услуг"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, duration, price FROM services")
            rows = cursor.fetchall()
            return [{"id": row[0], "name": row[1], "duration": row[2], "price": row[3]} for row in rows]
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Получить услугу по ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, duration, price FROM services WHERE id = ?", (service_id,))
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "duration": row[2], "price": row[3]}
            return None
    
    # ========== МАСТЕРА ==========
    
    def get_all_masters(self) -> List[Dict[str, Any]]:
        """Получить список всех мастеров"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description FROM masters")
            rows = cursor.fetchall()
            return [{"id": row[0], "name": row[1], "description": row[2]} for row in rows]
    
    def get_master_by_id(self, master_id: int) -> Optional[Dict[str, Any]]:
        """Получить мастера по ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, description FROM masters WHERE id = ?", (master_id,))
            row = cursor.fetchone()
            if row:
                return {"id": row[0], "name": row[1], "description": row[2]}
            return None
    
    # ========== СЛОТЫ ==========
    
    def get_free_slots_by_master_and_date(self, master_id: int, date_str: str) -> List[Dict[str, Any]]:
        """
        Получить свободные слоты мастера на конкретную дату.
        date_str: '2025-06-05'
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, master_id, service_id, start_time, end_time, is_available
                FROM slots 
                WHERE master_id = ? 
                AND DATE(start_time) = ?
                AND is_available = 1
                ORDER BY start_time
            """, (master_id, date_str))
            rows = cursor.fetchall()
            return [{
                "id": row[0],
                "master_id": row[1],
                "service_id": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "is_available": row[5]
            } for row in rows]
    
    def get_slot_by_id(self, slot_id: int) -> Optional[Dict[str, Any]]:
        """Получить слот по ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, master_id, service_id, start_time, end_time, is_available
                FROM slots WHERE id = ?
            """, (slot_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "master_id": row[1],
                    "service_id": row[2],
                    "start_time": row[3],
                    "end_time": row[4],
                    "is_available": row[5]
                }
            return None
    
    def lock_slot(self, slot_id: int) -> bool:
        """Заблокировать слот (при создании записи)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE slots SET is_available = 0 WHERE id = ? AND is_available = 1", (slot_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ========== ЗАПИСИ ==========
    
    def create_booking(self, user_id: int, slot_id: int, service_id: int, master_id: int) -> int:
        """Создать новую запись. Возвращает ID записи"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookings (user_id, slot_id, service_id, master_id, status, created_at)
                VALUES (?, ?, ?, ?, 'confirmed', ?)
            """, (user_id, slot_id, service_id, master_id, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_bookings(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все активные записи пользователя"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.id, b.user_id, b.slot_id, b.service_id, b.master_id, b.status, b.created_at,
                       s.start_time, s.end_time,
                       serv.name as service_name,
                       m.name as master_name
                FROM bookings b
                JOIN slots s ON b.slot_id = s.id
                JOIN services serv ON b.service_id = serv.id
                JOIN masters m ON b.master_id = m.id
                WHERE b.user_id = ? AND b.status = 'confirmed'
                ORDER BY s.start_time
            """, (user_id,))
            rows = cursor.fetchall()
            return [{
                "id": row[0],
                "user_id": row[1],
                "slot_id": row[2],
                "service_id": row[3],
                "master_id": row[4],
                "status": row[5],
                "created_at": row[6],
                "start_time": row[7],
                "end_time": row[8],
                "service_name": row[9],
                "master_name": row[10]
            } for row in rows]
    
    def cancel_booking(self, booking_id: int, user_id: int) -> bool:
        """Отменить запись (только свою) и освободить слот"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Получаем slot_id перед отменой
            cursor.execute("SELECT slot_id FROM bookings WHERE id = ? AND user_id = ?", (booking_id, user_id))
            row = cursor.fetchone()
            if not row:
                return False
            slot_id = row[0]
            
            # Отменяем запись
            cursor.execute("UPDATE bookings SET status = 'cancelled' WHERE id = ? AND user_id = ?", (booking_id, user_id))
            # Освобождаем слот
            cursor.execute("UPDATE slots SET is_available = 1 WHERE id = ?", (slot_id,))
            conn.commit()
            return True


# Создаём единственный экземпляр репозитория
booking_repo = BookingRepository()