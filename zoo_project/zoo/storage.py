"""
Module for handling data persistence for the zoo management system.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar, Union

from .core import Animal, Bird, Mammal, Reptile
from .events import EventType, ZooEvent, FeedingEvent, MedicalCheckEvent, TourEvent
from .staff import Staff, ZooKeeper, Veterinarian, Guide

T = TypeVar('T')

class ZooStorage:
    """Class for handling persistence of zoo data."""
    
    SCHEMA_VERSION = "1.0"
    
    def __init__(self, autosave_interval: int = 900):  # 15 minutes by default
        """Initialize the storage with autosave functionality.
        
        Args:
            autosave_interval: Interval in seconds between autosaves. Set to 0 to disable.
        """
        self.autosave_interval = autosave_interval
        self._autosave_task: Optional[asyncio.Task] = None
        self._shutdown = False
    
    async def start_autosave(self, zoo: 'Zoo', path: Path, 
                           fmt: Literal["json", "yaml", "pickle"] = "json") -> None:
        """Start the autosave background task.
        
        Args:
            zoo: The Zoo instance to save.
            path: Path to save to.
            fmt: Format to save in.
        """
        if self.autosave_interval <= 0:
            return
            
        self._shutdown = False
        
        async def autosave_loop():
            while not self._shutdown:
                try:
                    await asyncio.sleep(self.autosave_interval)
                    if not self._shutdown:
                        self.save(zoo, path, fmt)
                        print(f"Autosaved zoo data to {path} at {datetime.now()}")
                except Exception as e:
                    print(f"Error during autosave: {e}")
        
        self._autosave_task = asyncio.create_task(autosave_loop())
    
    def stop_autosave(self) -> None:
        """Stop the autosave background task."""
        if self._autosave_task:
            self._shutdown = True
            self._autosave_task.cancel()
            self._autosave_task = None
    
    @staticmethod
    def save(zoo: 'Zoo', path: Path, fmt: Literal["json", "yaml", "pickle"] = "json") -> None:
        """Save zoo data to a file.
        
        Args:
            zoo: The Zoo instance to save.
            path: Path to save to.
            fmt: Format to save in (json, yaml, or pickle).
        """
        data = {
            "schema_version": ZooStorage.SCHEMA_VERSION,
            "animals": [ZooStorage._serialize_animal(a) for a in zoo.animals],
            "staff": [ZooStorage._serialize_staff(s) for s in zoo.staff],
            "events": [ZooStorage._serialize_event(e) for e in zoo.events],
            "last_updated": datetime.now().isoformat()
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if fmt == "json":
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif fmt == "pickle":
            with open(path, 'wb') as f:
                pickle.dump(data, f)
        elif fmt == "yaml":
            try:
                import yaml
                with open(path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
            except ImportError:
                raise ImportError("PyYAML is required for YAML support. Install with 'pip install pyyaml'")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
    
    @staticmethod
    def load(path: Path) -> Dict[str, Any]:
        """Load zoo data from a file.
        
        Args:
            path: Path to load from.
            
        Returns:
            Dictionary containing the loaded data.
        """
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        fmt = path.suffix[1:].lower()
        
        if fmt == "json":
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif fmt == "pickle":
            with open(path, 'rb') as f:
                data = pickle.load(f)
        elif fmt in ["yaml", "yml"]:
            try:
                import yaml
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            except ImportError:
                raise ImportError("PyYAML is required for YAML support. Install with 'pip install pyyaml'")
        else:
            raise ValueError(f"Unsupported file format: {fmt}")
        
        # Verify schema version
        if data.get("schema_version") != ZooStorage.SCHEMA_VERSION:
            print(f"Warning: Schema version mismatch. Expected {ZooStorage.SCHEMA_VERSION}, "
                  f"got {data.get('schema_version')}")
        
        return data
    
    @staticmethod
    def _serialize_animal(animal: Animal) -> Dict[str, Any]:
        """Serialize an Animal instance to a dictionary."""
        data = {
            "type": animal.__class__.__name__,
            "name": animal.name,
            "age": animal.age,
            "species": animal.species
        }
        
        if isinstance(animal, Bird):
            data.update({
                "wing_span": animal.wing_span,
                "can_fly": animal.can_fly
            })
        elif isinstance(animal, Mammal):
            data.update({
                "is_domestic": animal.is_domestic,
                "fur_type": animal.fur_type
            })
        elif isinstance(animal, Reptile):
            data.update({
                "is_venomous": animal.is_venomous
            })
            
        return data
    
    @staticmethod
    def _deserialize_animal(data: Dict[str, Any]) -> Animal:
        """Deserialize a dictionary to an Animal instance."""
        cls_map = {
            "Bird": Bird,
            "Mammal": Mammal,
            "Reptile": Reptile
        }
        
        cls = cls_map[data["type"]]
        
        if cls is Bird:
            return cls(
                name=data["name"],
                age=data["age"],
                wing_span=data["wing_span"],
                can_fly=data["can_fly"]
            )
        elif cls is Mammal:
            return cls(
                name=data["name"],
                age=data["age"],
                species=data["species"],
                is_domestic=data["is_domestic"],
                fur_type=data["fur_type"]
            )
        elif cls is Reptile:
            return cls(
                name=data["name"],
                age=data["age"],
                is_venomous=data["is_venomous"]
            )
        else:
            raise ValueError(f"Unknown animal type: {data['type']}")
    
    @staticmethod
    def _serialize_staff(staff: Staff) -> Dict[str, Any]:
        """Serialize a Staff instance to a dictionary."""
        return {
            "type": staff.__class__.__name__,
            "name": staff.name,
            "staff_id": staff.staff_id,
            "hire_date": staff.hire_date.isoformat()
        }
    
    @staticmethod
    def _deserialize_staff(data: Dict[str, Any]) -> Staff:
        """Deserialize a dictionary to a Staff instance."""
        from datetime import date
        
        cls_map = {
            "ZooKeeper": ZooKeeper,
            "Veterinarian": Veterinarian,
            "Guide": Guide
        }
        
        cls = cls_map[data["type"]]
        hire_date = date.fromisoformat(data["hire_date"])
        
        # Create instance
        instance = cls(name=data["name"], staff_id=data["staff_id"])
        instance.hire_date = hire_date
        return instance
    
    @staticmethod
    def _serialize_event(event: ZooEvent) -> Dict[str, Any]:
        """Serialize a ZooEvent instance to a dictionary."""
        from datetime import datetime
        
        data = {
            "type": event.__class__.__name__,
            "name": event.name,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "duration_seconds": event.duration.total_seconds(),
            "location": event.location,
            "staff_ids": [s.staff_id for s in event.staff],
            "animal_names": [a.name for a in event.animals]
        }
        
        if isinstance(event, FeedingEvent):
            data["food_type"] = event.food_type
        elif isinstance(event, TourEvent):
            data.update({
                "max_visitors": event.max_visitors,
                "visitor_count": event.visitor_count
            })
            
        return data
    
    @staticmethod
    def _deserialize_event(data: Dict[str, Any], zoo: 'Zoo') -> ZooEvent:
        """Deserialize a dictionary to a ZooEvent instance."""
        from datetime import datetime, timedelta
        
        event_type = data["type"]
        start_time = datetime.fromisoformat(data["start_time"])
        duration = timedelta(seconds=data["duration_seconds"])
        
        # Find staff and animals by ID/name
        staff = [s for s in zoo.staff if s.staff_id in data["staff_ids"]]
        animals = [a for a in zoo.animals if a.name in data["animal_names"]]
        
        if event_type == "FeedingEvent":
            return FeedingEvent(
                name=data["name"],
                start_time=start_time,
                location=data["location"],
                food_type=data["food_type"],
                animals=animals,
                staff=staff,
                duration=duration,
                description=data["description"]
            )
        elif event_type == "MedicalCheckEvent":
            return MedicalCheckEvent(
                name=data["name"],
                start_time=start_time,
                location=data["location"],
                animals=animals,
                staff=staff,
                duration=duration,
                description=data["description"]
            )
        elif event_type == "TourEvent":
            event = TourEvent(
                name=data["name"],
                start_time=start_time,
                location=data["location"],
                staff=staff,
                duration=duration,
                description=data["description"],
                max_visitors=data.get("max_visitors", 20)
            )
            event.visitor_count = data.get("visitor_count", 0)
            return event
        else:
            return ZooEvent(
                event_type=EventType[data["event_type"]],
                name=data["name"],
                description=data["description"],
                start_time=start_time,
                duration=duration,
                location=data["location"],
                staff=staff,
                animals=animals
            )
