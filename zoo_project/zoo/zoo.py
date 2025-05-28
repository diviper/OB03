"""
Main module for the Zoo management system.
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Type, TypeVar, Union

from .core import Animal, Bird, Mammal, Reptile, animal_sound
from .events import EventType, ZooEvent, FeedingEvent, MedicalCheckEvent, TourEvent
from .staff import Staff, ZooKeeper, Veterinarian, Guide
from .storage import ZooStorage

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('zoo.log')
    ]
)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Animal)

class Zoo:
    """
    Основной класс для управления зоопарком.
    Отвечает за управление животными, персоналом и событиями.
    """
    
    def __init__(self, name: str):
        """
        Инициализация зоопарка.
        
        Args:
            name: Название зоопарка
        """
        self.name = name
        self.animals: List[Animal] = []
        self.staff: List[Staff] = []
        self.events: List[ZooEvent] = []
        self.storage = ZooStorage()
        self._event_subscriptions: Dict[str, Set[Animal]] = {}
        self._setup_default_event_subscriptions()
    
    def _setup_default_event_subscriptions(self) -> None:
        """Настройка подписок на события по умолчанию."""
        self._event_subscriptions = {
            "feeding": set(),
            "medical_check": set(),
            "enrichment": set()
        }
    
    def add_animal(self, animal: Animal) -> None:
        """
        Добавление животного в зоопарк.
        
        Args:
            animal: Животное для добавления
        """
        if animal in self.animals:
            logger.warning(f"Животное {animal.name} уже есть в зоопарке")
            return
            
        self.animals.append(animal)
        logger.info(f"Добавлено животное: {animal.name} ({animal.species})")
        
        # Подписываем на соответствующие события
        self._event_subscriptions["feeding"].add(animal)
        self._event_subscriptions["medical_check"].add(animal)
    
    def add_staff(self, staff: Staff) -> None:
        """
        Добавление сотрудника в зоопарк.
        
        Args:
            staff: Сотрудник для добавления
        """
        if staff in self.staff:
            logger.warning(f"Сотрудник {staff.name} уже работает в зоопарке")
            return
            
        self.staff.append(staff)
        logger.info(f"Добавлен сотрудник: {staff.name} ({staff.__class__.__name__})")
    
    def schedule_event(self, event: ZooEvent) -> None:
        """
        Запланировать событие в зоопарке.
        
        Args:
            event: Событие для планирования
        """
        # Проверка на пересечение с другими событиями
        for existing_event in self.events:
            if self._events_overlap(existing_event, event):
                logger.warning(
                    f"Событие '{event.name}' пересекается с '{existing_event.name}' "
                    f"({existing_event.start_time}-{existing_event.end_time})"
                )
                break
        
        self.events.append(event)
        logger.info(f"Запланировано событие: {event.name} на {event.start_time}")
    
    @staticmethod
    def _events_overlap(event1: ZooEvent, event2: ZooEvent) -> bool:
        """Проверка на пересечение двух событий."""
        return (
            event1.start_time < event2.end_time and 
            event1.end_time > event2.start_time
        )
    
    def daily_report(self, report_date: Optional[date] = None) -> str:
        """
        Сгенерировать ежедневный отчет.
        
        Args:
            report_date: Дата отчета (по умолчанию сегодня)
            
        Returns:
            Строка с отчетом
        """
        report_date = report_date or date.today()
        
        # Фильтруем события по дате
        daily_events = [
            e for e in self.events 
            if e.start_time.date() == report_date
        ]
        
        # Сортируем события по времени начала
        daily_events.sort(key=lambda e: e.start_time)
        
        # Формируем отчет
        report = [
            f"Отчет зоопарка '{self.name}' за {report_date}",
            "=" * 50,
            f"Всего животных: {len(self.animals)}",
            f"Всего сотрудников: {len(self.staff)}",
            f"Запланировано событий: {len(daily_events)}",
            "",
            "Запланированные события:",
            "-" * 30
        ]
        
        if daily_events:
            for event in daily_events:
                report.append(f"{event.start_time.strftime('%H:%M')} - {event.name}")
                report.append(f"   Место: {event.location}")
                report.append(f"   Участники: {', '.join(s.name for s in event.staff)}")
                if event.animals:
                    report.append(f"   Животные: {', '.join(a.name for a in event.animals)}")
                report.append("")
        else:
            report.append("Событий не запланировано")
        
        # Добавляем сводку по животным
        report.extend(["", "Сводка по животным:", "-" * 30])
        
        animal_types = {}
        for animal in self.animals:
            animal_type = animal.__class__.__name__
            animal_types[animal_type] = animal_types.get(animal_type, 0) + 1
        
        for animal_type, count in animal_types.items():
            report.append(f"{animal_type}: {count}")
        
        return "\n".join(report)
    
    def notify_animals(self, event_type: str, **kwargs) -> None:
        """
        Уведомить животных о событии.
        
        Args:
            event_type: Тип события (например, 'feeding')
            **kwargs: Дополнительные параметры события
        """
        if event_type not in self._event_subscriptions:
            logger.warning(f"Неизвестный тип события: {event_type}")
            return
            
        for animal in self._event_subscriptions[event_type]:
            if event_type == "feeding" and "food" in kwargs:
                animal.eat(kwargs["food"])
            elif event_type == "medical_check":
                logger.info(f"{animal.name} проходит медицинский осмотр")
    
    def get_animals_by_type(self, animal_type: Type[T]) -> List[T]:
        """
        Получить список животных определенного типа.
        
        Args:
            animal_type: Класс животного (например, Bird, Mammal, Reptile)
            
        Returns:
            Список животных указанного типа
        """
        return [a for a in self.animals if isinstance(a, animal_type)]
    
    def get_staff_by_type(self, staff_type: Type[Staff]) -> List[Staff]:
        """
        Получить список сотрудников определенного типа.
        
        Args:
            staff_type: Класс сотрудника (например, ZooKeeper, Veterinarian, Guide)
            
        Returns:
            Список сотрудников указанного типа
        """
        return [s for s in self.staff if isinstance(s, staff_type)]
    
    def get_events_on_date(self, target_date: date) -> List[ZooEvent]:
        """
        Получить список событий на указанную дату.
        
        Args:
            target_date: Дата для поиска событий
            
        Returns:
            Список событий на указанную дату
        """
        return [
            e for e in self.events 
            if e.start_time.date() == target_date
        ]
    
    def save(self, path: Union[str, Path], fmt: str = "json") -> None:
        """
        Сохранить данные зоопарка в файл.
        
        Args:
            path: Путь к файлу для сохранения
            fmt: Формат файла (json, yaml, или pickle)
        """
        path = Path(path)
        self.storage.save(self, path, fmt)
        logger.info(f"Данные зоопарка сохранены в {path}")
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> 'Zoo':
        """
        Загрузить данные зоопарка из файла.
        
        Args:
            path: Путь к файлу для загрузки
            
        Returns:
            Экземпляр класса Zoo с загруженными данными
        """
        path = Path(path)
        storage = ZooStorage()
        data = storage.load(path)
        
        # Создаем экземпляр зоопарка
        zoo = cls("Загруженный зоопарк")
        
        # Восстанавливаем сотрудников
        for staff_data in data.get("staff", []):
            staff = storage._deserialize_staff(staff_data)
            zoo.add_staff(staff)
        
        # Восстанавливаем животных
        for animal_data in data.get("animals", []):
            animal = storage._deserialize_animal(animal_data)
            zoo.add_animal(animal)
        
        # Восстанавливаем события
        for event_data in data.get("events", []):
            try:
                event = storage._deserialize_event(event_data, zoo)
                zoo.schedule_event(event)
            except Exception as e:
                logger.error(f"Ошибка при загрузке события: {e}")
        
        logger.info(f"Данные зоопарка загружены из {path}")
        return zoo
    
    async def run_day(self, target_date: Optional[date] = None) -> None:
        """
        Запустить симуляцию дня в зоопарке.
        
        Args:
            target_date: Дата для симуляции (по умолчанию сегодня)
        """
        target_date = target_date or date.today()
        logger.info(f"Запуск симуляции дня {target_date}")
        
        # Получаем события на день
        daily_events = self.get_events_on_date(target_date)
        
        # Сортируем события по времени начала
        daily_events.sort(key=lambda e: e.start_time)
        
        # Обрабатываем каждое событие
        for event in daily_events:
            logger.info(f"Начало события: {event.name}")
            
            # В реальном приложении здесь была бы логика обработки события
            if isinstance(event, FeedingEvent):
                self.notify_animals("feeding", food=event.food_type)
            elif isinstance(event, MedicalCheckEvent):
                self.notify_animals("medical_check")
            
            # Имитация продолжительности события
            await asyncio.sleep(0.5)
            logger.info(f"Завершено событие: {event.name}")
        
        logger.info(f"Симуляция дня {target_date} завершена")
