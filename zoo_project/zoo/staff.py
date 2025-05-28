"""
Module containing the Staff class hierarchy for the zoo management system.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
import random
from typing import ClassVar, Optional

from .core import Animal


class Staff(ABC):
    """Abstract base class for all zoo staff members."""
    
    def __init__(self, name: str, staff_id: int):
        self.name = name
        self.staff_id = staff_id
        self.hire_date = datetime.now().date()
    
    @abstractmethod
    def role_description(self) -> str:
        """Return a description of the staff member's role."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', staff_id={self.staff_id})"


class ZooKeeper(Staff):
    """Staff member responsible for animal care and feeding."""
    
    def role_description(self) -> str:
        return "Responsible for feeding animals and cleaning their enclosures."
    
    def feed_animal(self, animal: Animal, food: str) -> str:
        """Feed an animal and return a status message."""
        animal.eat(food)
        return f"{self.name} fed {animal.name} the {animal.species} some {food}."
    
    def clean_cage(self, animal: Animal) -> str:
        """Clean an animal's enclosure and return a status message."""
        return f"{self.name} cleaned the enclosure of {animal.name} the {animal.species}."
    
    @classmethod
    def create_random(cls, staff_id: int) -> 'ZooKeeper':
        """Create a random zookeeper instance."""
        names = ["Alex", "Jamie", "Taylor", "Casey", "Riley"]
        return cls(name=random.choice(names), staff_id=staff_id)


class Veterinarian(Staff):
    """Staff member responsible for animal health."""
    
    def role_description(self) -> str:
        return "Responsible for the medical care of zoo animals."
    
    def heal_animal(self, animal: Animal, issue: str) -> str:
        """Treat an animal's health issue and return a status message."""
        return f"Dr. {self.name} treated {animal.name}'s {issue}."
    
    def vaccinate(self, animal: Animal) -> str:
        """Vaccinate an animal and return a status message."""
        return f"Dr. {self.name} vaccinated {animal.name} the {animal.species}."
    
    @classmethod
    def create_random(cls, staff_id: int) -> 'Veterinarian':
        """Create a random veterinarian instance."""
        names = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
        first_names = ["Sarah", "Michael", "Emily", "David", "Jennifer"]
        return cls(
            name=f"{random.choice(first_names)} {random.choice(names)}",
            staff_id=staff_id
        )


class Guide(Staff):
    """Staff member responsible for giving tours and educating visitors."""
    
    def role_description(self) -> str:
        return "Responsible for giving tours and educating visitors about the zoo."
    
    def give_tour(self, group: str) -> str:
        """Give a tour to a group and return a status message."""
        return f"{self.name} is giving a tour to the {group} group."
    
    def answer_question(self, question: str) -> str:
        """Answer a visitor's question and return a response."""
        responses = [
            "That's a great question!",
            "I'd be happy to explain that.",
            "Let me tell you more about that.",
            "That's one of our most common questions!"
        ]
        return f"{self.name}: {random.choice(responses)} {question.replace('?', '')}? Well, " + \
               f"{' '.join(['Interesting fact' for _ in range(random.randint(2, 5))])}."
    
    @classmethod
    def create_random(cls, staff_id: int) -> 'Guide':
        """Create a random guide instance."""
        first_names = ["Chris", "Jordan", "Morgan", "Drew", "Blair"]
        last_names = ["Taylor", "Martinez", "Garcia", "Lee", "Wilson"]
        return cls(
            name=f"{random.choice(first_names)} {random.choice(last_names)}",
            staff_id=staff_id
        )
