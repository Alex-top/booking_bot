from storage.booking_repository import booking_repo

print("=== УСЛУГИ ===")
services = booking_repo.get_all_services()
for s in services:
    print(f"{s['id']}: {s['name']} - {s['duration']} мин - {s['price']} руб")

print("\n=== МАСТЕРА ===")
masters = booking_repo.get_all_masters()
for m in masters:
    print(f"{m['id']}: {m['name']} - {m['description']}")

print("\n=== СВОБОДНЫЕ СЛОТЫ НА СЕГОДНЯ ===")
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
slots = booking_repo.get_free_slots_by_master_and_date(1, today)
for slot in slots:
    print(f"Слот {slot['id']}: {slot['start_time']} - {slot['end_time']}")