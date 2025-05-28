"""
Core module containing the Animal class hierarchy and related functionality.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
import random
from typing import ClassVar, Self, Sequence

# Mens est zoo idearum; vide ut leones creativitatis non devorent cuniculos disciplinae.

class Animal(ABC):
    """Abstract base class for all animals in the zoo."""
    
    def __init__(self, name: str, age: int, species: str):
        self.name = name
        self.age = age
        self.species = species
    
    @abstractmethod
    def make_sound(self) -> str:
        """Return the sound the animal makes."""
        pass
    
    def eat(self, food: str) -> None:
        """Simulate the animal eating food."""
        print(f"{self.name} the {self.species} is eating {food}.")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', age={self.age}, species='{self.species}')"
    
    @classmethod
    @abstractmethod
    def create_random(cls) -> Self:
        """Create a random instance of the animal."""
        pass


class Bird(Animal):
    """Class representing a bird in the zoo."""
    
    def __init__(self, name: str, age: int, wing_span: float, can_fly: bool = True):
        super().__init__(name, age, "Bird")
        self.wing_span = wing_span
        self.can_fly = can_fly
    
    def make_sound(self) -> str:
        return "Chirp!"
    
    @classmethod
    def create_random(cls) -> Self:
        names = ["Tweety", "Polly", "Rio", "Zazu", "Iago"]
        return cls(
            name=random.choice(names),
            age=random.randint(1, 15),
            wing_span=random.uniform(0.1, 2.5),
            can_fly=random.choice([True, False])
        )
    
    def __repr__(self) -> str:
        return f"Bird(name='{self.name}', age={self.age}, wing_span={self.wing_span}, can_fly={self.can_fly})"


class Mammal(Animal):
    """Class representing a mammal in the zoo."""
    
    SOUNDS: ClassVar[dict[str, str]] = {
        "cat": "Meow",
        "dog": "Woof",
        "lion": "Roar",
        "tiger": "Growl",
        "bear": "Grrr"
    }
    
    def __init__(self, name: str, age: int, species: str, is_domestic: bool, fur_type: str):
        super().__init__(name, age, species)
        self.is_domestic = is_domestic
        self.fur_type = fur_type
    
    def make_sound(self) -> str:
        return self.SOUNDS.get(self.species.lower(), "Grrr")
    
    @classmethod
    def create_random(cls) -> Self:
        species = random.choice(list(cls.SOUNDS.keys()))
        names = {
            "cat": ["Whiskers", "Mittens", "Tiger"],
            "dog": ["Buddy", "Max", "Bella"],
            "lion": ["Simba", "Nala", "Mufasa"],
            "tiger": ["Rajah", "Shere Khan", "Diego"],
            "bear": ["Baloo", "Winnie", "Yogi"]
        }
        return cls(
            name=random.choice(names[species]),
            age=random.randint(1, 20),
            species=species.capitalize(),
            is_domestic=random.choice([True, False]),
            fur_type=random.choice(["short", "medium", "long"])
        )
    
    def __repr__(self) -> str:
        return f"Mammal(name='{self.name}', age={self.age}, species='{self.species}', is_domestic={self.is_domestic}, fur_type='{self.fur_type}')"


class Reptile(Animal):
    """Class representing a reptile in the zoo."""
    
    def __init__(self, name: str, age: int, is_venomous: bool):
        super().__init__(name, age, "Reptile")
        self.is_venomous = is_venomous
    
    def make_sound(self) -> str:
        return "Hiss..."
    
    @classmethod
    def create_random(cls) -> Self:
        names = ["Slither", "Fang", "Viper", "Rex", "Spike"]
        return cls(
            name=random.choice(names),
            age=random.randint(1, 30),
            is_venomous=random.choice([True, False])
        )
    
    def __repr__(self) -> str:
        return f"Reptile(name='{self.name}', age={self.age}, is_venomous={self.is_venomous})"


def animal_sound(animals: Sequence[Animal]) -> None:
    """Make each animal in the sequence produce its sound."""
    for animal in animals:
        print(f"{animal.name} the {animal.species} says: {animal.make_sound()}")
