import sqlite3
from config import config

def init_db():
    """Создаёт таблицы, если их нет"""
    with sqlite3.connect(config.DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # Услуги
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                duration INTEGER NOT NULL,
                price INTEGER NOT NULL
            )
        ''')
        
        # Мастера
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS masters (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
        
        # Слоты (доступное время)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS slots (
                id INTEGER PRIMARY KEY,
                master_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,  -- ISO format: 2025-06-05 10:00:00
                end_time TEXT NOT NULL,
                is_available INTEGER DEFAULT 1,
                FOREIGN KEY (master_id) REFERENCES masters(id),
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
        ''')
        
        # Записи клиентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                slot_id INTEGER NOT NULL,
                service_id INTEGER NOT NULL,
                master_id INTEGER NOT NULL,
                status TEXT DEFAULT 'confirmed',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (slot_id) REFERENCES slots(id)
            )
        ''')
        
        conn.commit()

# Заполняем тестовыми данными
def seed_test_data():
    """Добавляет услуги, мастеров и слоты для тестирования"""
    with sqlite3.connect(config.DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # Услуги
        cursor.execute("SELECT COUNT(*) FROM services")
        if cursor.fetchone()[0] == 0:
            services = [
                ("Стрижка", 30, 1000),
                ("Укладка", 45, 1500),
                ("Окрашивание", 90, 3000),
                ("Маникюр", 60, 800),
            ]
            cursor.executemany("INSERT INTO services (name, duration, price) VALUES (?, ?, ?)", services)
        
        # Мастера
        cursor.execute("SELECT COUNT(*) FROM masters")
        if cursor.fetchone()[0] == 0:
            masters = [
                ("Анна (топ-стилист)", "Опыт 8 лет, специалист по окрашиванию"),
                ("Елена (мастер)", "Опыт 5 лет, мужские и женские стрижки"),
            ]
            cursor.executemany("INSERT INTO masters (name, description) VALUES (?, ?)", masters)
        
        conn.commit()

if __name__ == "__main__":
    init_db()
    seed_test_data()
    print("✅ База данных создана и заполнена тестовыми данными")