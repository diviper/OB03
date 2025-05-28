"""
Command Line Interface for Zoo Management System.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .zoo import Zoo
from .core import Animal, Bird, Mammal, Reptile
from .staff import ZooKeeper, Veterinarian, Guide, Staff
from .events import FeedingEvent, MedicalCheckEvent, TourEvent, EventType

app = typer.Typer(add_completion=False)
console = Console()

# Global zoo instance
zoo: Optional[Zoo] = None

# File to store zoo data
DEFAULT_DATA_FILE = Path("zoo_data.json")

def ensure_zoo_loaded() -> Zoo:
    """Ensure zoo instance is loaded or create a new one."""
    global zoo
    if zoo is None:
        if DEFAULT_DATA_FILE.exists():
            zoo = Zoo.load(DEFAULT_DATA_FILE)
            console.print(f"[green]Загружен существующий зоопарк из {DEFAULT_DATA_FILE}[/green]")
        else:
            zoo = Zoo("Мой зоопарк")
            console.print("[yellow]Создан новый зоопарк[/yellow]")
    return zoo

def save_zoo() -> None:
    """Save zoo data to file."""
    if zoo:
        zoo.save(DEFAULT_DATA_FILE)
        console.print(f"[green]Данные зоопарка сохранены в {DEFAULT_DATA_FILE}[/green]")

@app.command()
def init(name: str = "Мой зоопарк") -> None:
    """Инициализировать новый зоопарк."""
    global zoo
    zoo = Zoo(name)
    save_zoo()
    console.print(f"[green]Создан новый зоопарк: {name}[/green]")

@app.command()
def add_animal(
    animal_type: str = typer.Argument(..., help="Тип животного (bird/mammal/reptile)"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Имя животного"),
    age: Optional[int] = typer.Option(None, "--age", "-a", help="Возраст животного"),
) -> None:
    """Добавить новое животное в зоопарк."""
    zoo = ensure_zoo_loaded()
    
    animal: Optional[Animal] = None
    
    if animal_type.lower() == "bird":
        wing_span = typer.prompt("Размах крыльев (м)", type=float)
        can_fly = typer.confirm("Может летать?", default=True)
        name = name or typer.prompt("Имя птицы", default="Птичка")
        age = age or typer.prompt("Возраст", type=int, default=1)
        animal = Bird(name=name, age=age, wing_span=wing_span, can_fly=can_fly)
    
    elif animal_type.lower() == "mammal":
        species = typer.prompt("Вид млекопитающего", default="Собака")
        is_domestic = typer.confirm("Домашнее животное?", default=True)
        fur_type = typer.prompt("Тип шерсти", default="короткая")
        name = name or typer.prompt("Имя", default=species)
        age = age or typer.prompt("Возраст", type=int, default=1)
        animal = Mammal(
            name=name,
            age=age,
            species=species,
            is_domestic=is_domestic,
            fur_type=fur_type
        )
    
    elif animal_type.lower() == "reptile":
        is_venomous = typer.confirm("Ядовитое?", default=False)
        name = name or typer.prompt("Имя рептилии", default="Рептилия")
        age = age or typer.prompt("Возраст", type=int, default=1)
        animal = Reptile(name=name, age=age, is_venomous=is_venomous)
    
    if animal:
        zoo.add_animal(animal)
        save_zoo()
        console.print(f"[green]Добавлено животное: {animal}[/green]")
    else:
        console.print("[red]Неизвестный тип животного. Используйте bird, mammal или reptile.[/red]")

@app.command()
def add_staff(
    staff_type: str = typer.Argument(..., help="Тип сотрудника (keeper/vet/guide)"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Имя сотрудника"),
) -> None:
    """Добавить нового сотрудника в зоопарк."""
    zoo = ensure_zoo_loaded()
    
    staff: Optional[Staff] = None
    staff_id = max([s.staff_id for s in zoo.staff], default=0) + 1
    
    if staff_type.lower() in ["keeper", "zookeeper", "смотритель"]:
        name = name or typer.prompt("Имя смотрителя", default=f"Смотритель_{staff_id}")
        staff = ZooKeeper(name=name, staff_id=staff_id)
    
    elif staff_type.lower() in ["vet", "veterinarian", "ветеринар"]:
        name = name or typer.prompt("Имя ветеринара", default=f"Ветеринар_{staff_id}")
        staff = Veterinarian(name=name, staff_id=staff_id)
    
    elif staff_type.lower() in ["guide", "экскурсовод"]:
        name = name or typer.prompt("Имя экскурсовода", default=f"Экскурсовод_{staff_id}")
        staff = Guide(name=name, staff_id=staff_id)
    
    if staff:
        zoo.add_staff(staff)
        save_zoo()
        console.print(f"[green]Добавлен сотрудник: {staff}[/green]")
    else:
        console.print(
            "[red]Неизвестный тип сотрудника. "
            "Используйте keeper, vet или guide.[/red]"
        )

@app.command()
def list_animals() -> None:
    """Показать список всех животных в зоопарке."""
    zoo = ensure_zoo_loaded()
    
    if not zoo.animals:
        console.print("[yellow]В зоопарке пока нет животных.[/yellow]")
        return
    
    table = Table(title="Животные в зоопарке")
    table.add_column("Тип", style="cyan")
    table.add_column("Имя", style="green")
    table.add_column("Возраст", justify="right")
    table.add_column("Описание")
    
    for animal in zoo.animals:
        description = ""
        if isinstance(animal, Bird):
            description = f"Размах крыльев: {animal.wing_span}м, " \
                        f"{'Летает' if animal.can_fly else 'Не летает'}"
        elif isinstance(animal, Mammal):
            description = f"Вид: {animal.species}, " \
                        f"Шерсть: {animal.fur_type}, " \
                        f"{'Домашнее' if animal.is_domestic else 'Дикое'}"
        elif isinstance(animal, Reptile):
            description = f"{'Ядовитое' if animal.is_venomous else 'Не ядовитое'}"
        
        table.add_row(
            animal.__class__.__name__,
            animal.name,
            str(animal.age),
            description
        )
    
    console.print(table)

@app.command()
def list_staff() -> None:
    """Показать список всех сотрудников зоопарка."""
    zoo = ensure_zoo_loaded()
    
    if not zoo.staff:
        console.print("[yellow]В зоопарке пока нет сотрудников.[/yellow]")
        return
    
    table = Table(title="Сотрудники зоопарка")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Имя", style="green")
    table.add_column("Должность")
    table.add_column("Описание")
    
    for staff in zoo.staff:
        role = ""
        if isinstance(staff, ZooKeeper):
            role = "Смотритель"
            description = "Ухаживает за животными"
        elif isinstance(staff, Veterinarian):
            role = "Ветеринар"
            description = "Лечит животных"
        elif isinstance(staff, Guide):
            role = "Экскурсовод"
            description = "Проводит экскурсии"
        else:
            role = "Сотрудник"
            description = ""
        
        table.add_row(
            str(staff.staff_id),
            staff.name,
            role,
            description
        )
    
    console.print(table)

@app.command()
def schedule_event(
    event_type: str = typer.Argument(..., help="Тип события (feeding/medical/tour)"),
    time: str = typer.Argument(..., help="Время начала (ЧЧ:ММ)"),
    location: str = typer.Argument(..., help="Место проведения"),
) -> None:
    """Запланировать новое событие в зоопарке."""n    zoo = ensure_zoo_loaded()
    
    try:
        # Парсим время
        event_time = datetime.strptime(time, "%H:%M").time()
        # Устанавливаем дату на сегодня
        event_datetime = datetime.combine(date.today(), event_time)
    except ValueError:
        console.print("[red]Неверный формат времени. Используйте ЧЧ:ММ[/red]")
        return
    
    event: Optional[ZooEvent] = None
    
    if event_type.lower() in ["feeding", "кормление"]:
        if not zoo.animals:
            console.print("[red]Нет животных для кормления.[/red]")
            return
            
        animal_names = [a.name for a in zoo.animals]
        selected = typer.prompt(
            f"Выберите животных для кормления ({', '.join(animal_names)}):",
            default=",".join(animal_names[:1])
        )
        animals_to_feed = [a for a in zoo.animals if a.name in [n.strip() for n in selected.split(",")]]
        
        if not animals_to_feed:
            console.print("[red]Не выбраны животные для кормления.[/red]")
            return
            
        food = typer.prompt("Чем кормить?", default="кормом")
        
        # Находим смотрителей
        keepers = [s for s in zoo.staff if isinstance(s, ZooKeeper)]
        if not keepers:
            console.print("[yellow]Внимание: нет смотрителей в зоопарке.[/yellow]")
            staff = []
        else:
            staff = [keepers[0]]  # Берем первого смотрителя
        
        event = FeedingEvent(
            name=f"Кормление {', '.join(a.name for a in animals_to_feed)}",
            start_time=event_datetime,
            location=location,
            food_type=food,
            animals=animals_to_feed,
            staff=staff,
            description=f"Кормление животных {food}"
        )
    
    elif event_type.lower() in ["medical", "медосмотр"]:
        if not zoo.animals:
            console.print("[red]Нет животных для осмотра.[/red]")
            return
            
        animal_names = [a.name for a in zoo.animals]
        selected = typer.prompt(
            f"Выберите животных для осмотра ({', '.join(animal_names)}):",
            default=",".join(animal_names[:1])
        )
        animals_to_check = [a for a in zoo.animals if a.name in [n.strip() for n in selected.split(",")]]
        
        if not animals_to_check:
            console.print("[red]Не выбраны животные для осмотра.[/red]")
            return
            
        # Находим ветеринаров
        vets = [s for s in zoo.staff if isinstance(s, Veterinarian)]
        if not vets:
            console.print("[yellow]Внимание: нет ветеринаров в зоопарке.[/yellow]")
            staff = []
        else:
            staff = [vets[0]]  # Берем первого ветеринара
        
        event = MedicalCheckEvent(
            name=f"Медосмотр {', '.join(a.name for a in animals_to_check)}",
            start_time=event_datetime,
            location=location,
            animals=animals_to_check,
            staff=staff,
            description="Плановый медицинский осмотр"
        )
    
    elif event_type.lower() in ["tour", "экскурсия"]:
        tour_name = typer.prompt("Название экскурсии", default="Обзорная экскурсия")
        
        # Находим экскурсоводов
        guides = [s for s in zoo.staff if isinstance(s, Guide)]
        if not guides:
            console.print("[yellow]Внимание: нет экскурсоводов в зоопарке.[/yellow]")
            staff = []
        else:
            staff = [guides[0]]  # Берем первого экскурсовода
        
        event = TourEvent(
            name=tour_name,
            start_time=event_datetime,
            location=location,
            staff=staff,
            description="Экскурсия по зоопарку"
        )
    
    if event:
        zoo.schedule_event(event)
        save_zoo()
        console.print(f"[green]Запланировано событие: {event.name}[/green]")
    else:
        console.print(
            "[red]Неизвестный тип события. "
            "Используйте feeding, medical или tour.[/red]"
        )

@app.command()
def daily_report(report_date: str = typer.Argument(None)) -> None:
    """Показать отчет за указанную дату (по умолчанию сегодня)."""
    zoo = ensure_zoo_loaded()
    
    target_date = date.today()
    if report_date:
        try:
            target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
        except ValueError:
            console.print("[red]Неверный формат даты. Используйте ГГГГ-ММ-ДД[/red]")
            return
    
    report = zoo.daily_report(target_date)
    console.print(f"\n[bold]Отчет зоопарка за {target_date}[/bold]\n")
    console.print(report)

@app.command()
async def run_day(target_date: str = typer.Argument(None)) -> None:
    """Запустить симуляцию дня (по умолчанию сегодня)."""
    zoo = ensure_zoo_loaded()
    
    target = date.today()
    if target_date:
        try:
            target = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            console.print("[red]Неверный формат даты. Используйте ГГГГ-ММ-ДД[/red]")
            return
    
    console.print(f"[bold]Запуск симуляции дня {target}[/bold]\n")
    
    # Показываем отчет за день
    report = zoo.daily_report(target)
    console.print(report)
    
    # Запускаем симуляцию
    await zoo.run_day(target)
    
    # Сохраняем изменения
    save_zoo()
    console.print("\n[green]Симуляция дня завершена.[/green]")

@app.command()
def demo() -> None:
    """Запустить демонстрационный сценарий."""
    from .demo import run_demo
    run_demo()

if __name__ == "__main__":
    app()
