from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

class VenueSpace(models.Model):
    name = models.CharField(max_length=100)
    maximum_capacity = models.IntegerField()

class Reservation(models.Model):
    venue_space = models.ForeignKey(VenueSpace, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def clean(self):
        overlapping = Reservation.objects.filter(
            venue_space=self.venue_space
        ).filter(
            Q(start_time__lt=self.end_time) & Q(end_time__gt=self.start_time)
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("This venue space is already reserved for the requested time frame.")