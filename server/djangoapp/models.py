"""Relational catalogue managed from Django's administration site."""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class CarModel(models.Model):
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[('SUV','SUV'),('Sedan','Sedan'),('Wagon','Wagon'),('Truck','Truck'),('Coupe','Coupe'),('Other','Other')])
    year = models.PositiveIntegerField(validators=[MinValueValidator(2015), MaxValueValidator(2023)])
    def __str__(self):
        return f'{self.car_make.name} {self.name} ({self.year})'
    class Meta:
        ordering = ['car_make__name', 'name']
        constraints = [models.UniqueConstraint(fields=['car_make','name','year'], name='unique_car_model_year')]
