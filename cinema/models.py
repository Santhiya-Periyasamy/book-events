from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('movie', 'Movie'),
        ('concert', 'Concert'),
        ('theater', 'Theater Play'),
        ('comedy', 'Comedy Show'),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='movie')
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class Show(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    show_time = models.DateTimeField()
    total_seats = models.IntegerField(default=100)
    booked_seats = models.JSONField(default=list)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=150.00)
    
    def available_seats(self):
        return self.total_seats - len(self.booked_seats)

    def __str__(self):
        return f"{self.event.title} at {self.show_time}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    seats_booked = models.JSONField()
    seat_names = models.TextField()  
    total_price = models.DecimalField(max_digits=8, decimal_places=2,null=False)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.customer_name} - {self.seats_booked} seats"   
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)