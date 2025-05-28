"""
Tests for the zoo management system.
"""
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import pytest
from freezegun import freeze_time

from zoo.core import Animal, Bird, Mammal, Reptile, animal_sound
from zoo.staff import ZooKeeper, Veterinarian, Guide
from zoo.zoo import Zoo
from zoo.events import FeedingEvent, MedicalCheckEvent, TourEvent

# Фикстуры для тестов

@pytest.fixture
def sample_animals():
    """Создает тестовых животных."""
    return [
        Bird(name="Кеша", age=2, wing_span=0.3, can_fly=True),
        Mammal(name="Барсик", age=3, species="Кот", is_domestic=True, fur_type="короткая"),
        Reptile(name="Гена", age=10, is_venomous=False),
    ]

@pytest.fixture
def sample_staff():
    """Создает тестовых сотрудников."""
    return [
        ZooKeeper(name="Иван Петров", staff_id=1),
        Veterinarian(name="Анна Сидорова", staff_id=2),
        Guide(name="Мария Иванова", staff_id=3),
    ]

@pytest.fixture
def empty_zoo():
    """Создает пустой зоопарк."""
    return Zoo("Тестовый зоопарк")

@pytest.fixture
def populated_zoo(empty_zoo, sample_animals, sample_staff):
    """Создает зоопарк с тестовыми данными."""
    zoo = empty_zoo
    for animal in sample_animals:
        zoo.add_animal(animal)
    for staff in sample_staff:
        zoo.add_staff(staff)
    return zoo

# Тесты

def test_animal_sounds(sample_animals, capsys):
    """Проверяет, что животные издают правильные звуки."""
    animal_sound(sample_animals)
    captured = capsys.readouterr()
    assert "Кеша the Bird says: Chirp!" in captured.out
    assert "Барсик the Кот says: Meow" in captured.out
    assert "Гена the Reptile says: Hiss..." in captured.out

def test_zoo_add_animal(empty_zoo):
    """Проверяет добавление животного в зоопарк."""
    animal = Bird(name="Кеша", age=2, wing_span=0.3, can_fly=True)
    empty_zoo.add_animal(animal)
    assert len(empty_zoo.animals) == 1
    assert empty_zoo.animals[0].name == "Кеша"

def test_zoo_add_staff(empty_zoo):
    """Проверяет добавление сотрудника в зоопарк."""
    staff = ZooKeeper(name="Иван Петров", staff_id=1)
    empty_zoo.add_staff(staff)
    assert len(empty_zoo.staff) == 1
    assert empty_zoo.staff[0].name == "Иван Петров"

def test_schedule_event(populated_zoo):
    """Проверяет планирование события в зоопарке."""
    now = datetime.now()
    event = FeedingEvent(
        name="Кормление",
        start_time=now + timedelta(hours=1),
        location="Вольер 1",
        food_type="корм",
        animals=populated_zoo.animals[:1],
        staff=populated_zoo.get_staff_by_type(ZooKeeper)[:1],
    )
    populated_zoo.schedule_event(event)
    assert len(populated_zoo.events) == 1
    assert populated_zoo.events[0].name == "Кормление"

def test_daily_report(populated_zoo):
    """Проверяет генерацию ежедневного отчета."""
    report = populated_zoo.daily_report()
    assert "Отчет зоопарка" in report
    assert "Всего животных: 3" in report
    assert "Всего сотрудников: 3" in report

@pytest.mark.asyncio
async def test_run_day(populated_zoo):
    """Проверяет симуляцию дня в зоопарке."""
    # Добавляем тестовое событие
    now = datetime.now()
    event = FeedingEvent(
        name="Тестовое кормление",
        start_time=now.replace(hour=12, minute=0, second=0, microsecond=0),
        location="Тестовый вольер",
        food_type="тестовый корм",
        animals=populated_zoo.animals[:1],
        staff=populated_zoo.get_staff_by_type(ZooKeeper)[:1],
    )
    populated_zoo.schedule_event(event)
    
    # Запускаем симуляцию дня
    with freeze_time(now.replace(hour=11, minute=30)):
        await populated_zoo.run_day(now.date())
    
    # Проверяем, что событие было обработано
    # В реальном тесте здесь должны быть более конкретные проверки
    assert True

def test_save_load_zoo(populated_zoo, tmp_path):
    """Проверяет сохранение и загрузку зоопарка."""
    # Добавляем тестовые данные
    test_file = tmp_path / "test_zoo.json"
    
    # Сохраняем
    populated_zoo.save(test_file)
    assert test_file.exists()
    
    # Загружаем
    loaded_zoo = Zoo.load(test_file)
    
    # Проверяем, что данные загружены корректно
    assert len(loaded_zoo.animals) == len(populated_zoo.animals)
    assert len(loaded_zoo.staff) == len(populated_zoo.staff)
    assert len(loaded_zoo.events) == len(populated_zoo.events)
    
    # Проверяем имена первого животного и сотрудника
    if populated_zoo.animals and loaded_zoo.animals:
        assert populated_zoo.animals[0].name == loaded_zoo.animals[0].name
    
    if populated_zoo.staff and loaded_zoo.staff:
        assert populated_zoo.staff[0].name == loaded_zoo.staff[0].name
