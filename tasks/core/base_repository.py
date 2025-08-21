from typing import TypeVar, Generic, Type, Optional, List
from django.db import models
from django.db.models import QuerySet

T = TypeVar("T", bound=models.Model)

class BaseRepository(Generic[T]):
    """Base repository class for all repositories"""

    def __init__(self, model: Type[T]):
        self.model = model

    def create(self, **kwargs) -> T:
        """Create a new instance of the model"""
        return self.model.objects.create(**kwargs)
    
    def get_by_id(self, id: str) -> Optional[T]:
        """Get an instance by its ID"""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet[T]:
        """Get all instances of the model"""
        return self.model.objects.all()
    
    def update(self, instance: T, **kwargs) -> T:
        """Update an instance of the model"""
        for field, value in kwargs.items():
            setattr(instance, field, value)
        instance.save()
        return instance
    
    def delete(self, instance: T) -> bool:
        """Delete an instance of the model"""
        try:
            instance.delete()
            return True
        except Exception:
            return False
    
    def filter(self, **kwargs) -> QuerySet[T]:
        """Filter instances of the model"""
        return self.model.objects.filter(**kwargs)
    
    def exists(self, **kwargs) -> bool:
        """Check if any instance exists with the given criteria"""
        return self.model.objects.filter(**kwargs).exists()