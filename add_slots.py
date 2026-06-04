"""Добавляет тестовые слоты для отладки бота записи"""

import sqlite3
from datetime import datetime, timedelta
from config import config

def add_test_slots():
    """Добавляет слоты на ближайшие 7 дней для каждого мастера"""
    
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Удаляем старые слоты (если есть)
    cursor.execute("DELETE FROM slots")
    
    # Рабочие часы: с 10:00 до 18:00
    start_hour = 10
    end_hour = 18
    
    # Мастера (ID: 1 - Анна, 2 - Елена)
    masters = [1, 2]
    
    # Услуги (для каждого слота укажем service_id = 1, можно менять)
    service_id = 1
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    slots_added = 0
    
    for master_id in masters:
        for day_offset in range(7):  # 7 дней
            current_date = today + timedelta(days=day_offset)
            
            # Пропускаем воскресенье (6 = воскресенье в Python)
            if current_date.weekday() == 6:
                continue
            
            # Создаём слоты каждый час
            for hour in range(start_hour, end_hour):
                start_time = current_date.replace(hour=hour, minute=0, second=0)
                end_time = current_date.replace(hour=hour + 1, minute=0, second=0)
                
                # Пропускаем уже прошедшие слоты
                if start_time < datetime.now():
                    continue
                
                cursor.execute("""
                    INSERT INTO slots (master_id, service_id, start_time, end_time, is_available)
                    VALUES (?, ?, ?, ?, 1)
                """, (master_id, service_id, start_time.isoformat(), end_time.isoformat()))
                slots_added += 1
    
    conn.commit()
    conn.close()
    
    print(f"✅ Добавлено {slots_added} тестовых слотов на ближайшие дни")
    print("📅 Слоты созданы с 10:00 до 18:00, без воскресенья")

if __name__ == "__main__":
    add_test_slots()