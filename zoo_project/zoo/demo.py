"""
Демонстрационный модуль для зоопарка.
"""
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import random
from typing import List, Optional

from rich.console import Console

from .zoo import Zoo
from .core import Bird, Mammal, Reptile
from .staff import ZooKeeper, Veterinarian, Guide
from .events import FeedingEvent, MedicalCheckEvent, TourEvent

console = Console()

def create_sample_zoo() -> Zoo:
    """Создать демонстрационный зоопарк с тестовыми данными."""
    zoo = Zoo("Демонстрационный зоопарк")
    
    # Создаем животных
    animals: List[Union[Bird, Mammal, Reptile]] = [
        # Птицы
        Bird(name="Кеша", age=2, wing_span=0.3, can_fly=True),
        Bird(name="Гоша", age=1, wing_span=0.5, can_fly=False),
        # Млекопитающие
        Mammal(name="Барсик", age=3, species="Кот", is_domestic=True, fur_type="короткая"),
        Mammal(name="Шарик", age=5, species="Собака", is_domestic=True, fur_type="пушистая"),
        Mammal(name="Симба", age=4, species="Лев", is_domestic=False, fur_type="густая"),
        # Рептилии
        Reptile(name="Гена", age=10, is_venomous=False),
        Reptile(name="Кузя", age=8, is_venomous=True),
    ]
    
    # Добавляем животных в зоопарк
    for animal in animals:
        zoo.add_animal(animal)
    
    # Создаем сотрудников
    staff = [
        ZooKeeper(name="Иван Петров", staff_id=1),
        Veterinarian(name="Анна Сидорова", staff_id=2),
        Guide(name="Мария Иванова", staff_id=3),
    ]
    
    # Добавляем сотрудников в зоопарк
    for person in staff:
        zoo.add_staff(person)
    
    # Создаем события
    now = datetime.now()
    events = [
        FeedingEvent(
            name="Утреннее кормление",
            start_time=now.replace(hour=9, minute=0, second=0, microsecond=0),
            location="Основной вольер",
            food_type="корм",
            animals=zoo.animals[:4],  # Первые 4 животных
            staff=zoo.get_staff_by_type(ZooKeeper)[:1],  # Первый смотритель
            description="Ежедневное утреннее кормление"
        ),
        MedicalCheckEvent(
            name="Плановый осмотр",
            start_time=now.replace(hour=11, minute=0, second=0, microsecond=0),
            location="Медпункт",
            animals=zoo.animals[::2],  # Каждое второе животное
            staff=zoo.get_staff_by_type(Veterinarian)[:1],  # Первый ветеринар
            description="Плановый медицинский осмотр"
        ),
        TourEvent(
            name="Экскурсия для школьников",
            start_time=now.replace(hour=14, minute=0, second=0, microsecond=0),
            location="Вход в зоопарк",
            staff=zoo.get_staff_by_type(Guide)[:1],  # Первый экскурсовод
            description="Экскурсия для школьников младших классов"
        ),
        FeedingEvent(
            name="Вечернее кормление",
            start_time=now.replace(hour=17, minute=0, second=0, microsecond=0),
            location="Основной вольер",
            food_type="корм",
            animals=zoo.animals[3:],  # Последние животные
            staff=zoo.get_staff_by_type(ZooKeeper)[:1],  # Первый смотритель
            description="Ежедневное вечернее кормление"
        ),
    ]
    
    # Добавляем события в зоопарк
    for event in events:
        zoo.schedule_event(event)
    
    return zoo

def print_zoo_summary(zoo: Zoo) -> None:
    """Вывести сводную информацию о зоопарке."""
    console.print(f"\n[bold]Зоопарк: {zoo.name}[/bold]")
    console.print(f"Всего животных: {len(zoo.animals)}")
    console.print(f"Всего сотрудников: {len(zoo.staff)}")
    console.print(f"Запланировано событий: {len(zoo.events)}")
    
    # Статистика по типам животных
    animal_types = {}
    for animal in zoo.animals:
        animal_type = animal.__class__.__name__
        animal_types[animal_type] = animal_types.get(animal_type, 0) + 1
    
    console.print("\n[underline]Животные:[/underline]")
    for animal_type, count in animal_types.items():
        console.print(f"- {animal_type}: {count}")
    
    # Статистика по сотрудникам
    staff_roles = {"ZooKeeper": 0, "Veterinarian": 0, "Guide": 0}
    for staff in zoo.staff:
        if isinstance(staff, ZooKeeper):
            staff_roles["ZooKeeper"] += 1
        elif isinstance(staff, Veterinarian):
            staff_roles["Veterinarian"] += 1
        elif isinstance(staff, Guide):
            staff_roles["Guide"] += 1
    
    console.print("\n[underline]Сотрудники:[/underline]")
    for role, count in staff_roles.items():
        if count > 0:
            console.print(f"- {role}: {count}")
    
    # Ближайшие события
    console.print("\n[underline]Ближайшие события:[/underline]")
    today_events = [e for e in zoo.events if e.start_time.date() == datetime.now().date()]
    if today_events:
        for event in sorted(today_events, key=lambda e: e.start_time):
            console.print(f"- {event.start_time.strftime('%H:%M')} {event.name} ({event.location})")
    else:
        console.print("На сегодня событий нет.")

async def run_demo() -> None:
    """Запустить демонстрацию работы зоопарка."""
    console.print("[bold blue]Демонстрация работы зоопарка[/bold blue]\n")
    
    # Создаем демонстрационный зоопарк
    zoo = create_sample_zoo()
    
    # Показываем сводную информацию
    print_zoo_summary(zoo)
    
    # Запускаем симуляцию дня
    console.print("\n[bold]Запуск симуляции дня...[/bold]")
    await zoo.run_day()
    
    # Демонстрация звуков животных
    console.print("\n[bold]Звуки животных:[/bold]")
    for animal in zoo.animals:
        console.print(f"{animal.name} ({animal.__class__.__name__}): {animal.make_sound()}")
    
    # Демонстрация сохранения/загрузки
    save_path = Path("demo_zoo.json")
    console.print(f"\n[bold]Сохранение зоопарка в {save_path}...[/bold]")
    zoo.save(save_path)
    
    console.print("\n[bold green]Демонстрация завершена![/bold green]")

if __name__ == "__main__":
    asyncio.run(run_demo())
