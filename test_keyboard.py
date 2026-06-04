from handlers.keyboards import BookingKeyboards

# Просто проверяем, что клавиатуры создаются без ошибок
print("✅ Главная клавиатура:", BookingKeyboards.get_main_keyboard())
print("✅ Клавиатура услуг:", BookingKeyboards.get_services_keyboard([]))
print("✅ Клавиатура дат:", BookingKeyboards.get_dates_keyboard())
print("✅ Клавиатура подтверждения:", BookingKeyboards.get_confirm_keyboard("Стрижка", "Анна", "05.06", "10:00", 1000, 1))
print("✅ Все клавиатуры создаются успешно!")