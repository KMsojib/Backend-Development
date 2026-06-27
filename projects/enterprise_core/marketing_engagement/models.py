from django.db import models
from django.core.exceptions import ValidationError
class Campaign(models.Model):
    title = models.CharField(max_length=255)
    sent_count = models.IntegerField(default=0)
    open_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title

    def clean(self):
        if self.open_count > self.sent_count:
            raise ValidationError({
                'open_count': "The number of opens cannot exceed the number of sent items."
            })