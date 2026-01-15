
from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('chandeliers', 'Chandeliers'),
        ('table lamps', 'Table Lamps'),
        ('floor lamps', 'Floor Lamps'),
        ('outdoor lamps', 'Outdoor Lamps'),
        ('pendant', 'Pendant'),
        ('wall lights', 'Wall Lights'),
    ]
    
    name = models.CharField(max_length=200)
    price = models.FloatField()
    material = models.CharField(max_length=200, blank=True, null=True)
    size = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    warranty = models.CharField(max_length=50, blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name
