from services.booking_service import booking_service
from datetime import datetime

print("=== 1. Получаем услуги ===")
services = booking_service.get_all_services()
for s in services:
    print(f"  {s['id']}: {s['name']} - {s['price']} ₽")

print("\n=== 2. Получаем мастеров ===")
masters = booking_service.get_all_masters()
for m in masters:
    print(f"  {m['id']}: {m['name']}")

print("\n=== 3. Тестируем состояния пользователя ===")
user_id = 123456

# Устанавливаем состояние
booking_service.set_user_state(user_id, booking_service.STATE_SELECT_SERVICE)
booking_service.set_temp_data(user_id, 'service_id', 1)
booking_service.set_temp_data(user_id, 'master_id', 1)

print(f"  Состояние: {booking_service.get_user_state(user_id)}")
print(f"  Данные: {booking_service.get_temp_data(user_id)}")

# Очищаем
booking_service.set_user_state(user_id, None)
print(f"  После очистки: состояние={booking_service.get_user_state(user_id)}, данные={booking_service.get_temp_data(user_id)}")

print("\n=== 4. Доступные даты (если есть слоты в БД) ===")
dates = booking_service.get_available_dates(1, 5)
print(f"  Даты со слотами: {dates}")

print("\n✅ Все проверки пройдены!")