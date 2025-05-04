from django.db import models
from django.core.validators import MinValueValidator
from HouseRentManagementApp.models import UserProfile

class House(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Booked', 'Booked'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="houses_owned")
    house_no = models.CharField(max_length=255, unique=True)
    room_size = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    pincode = models.IntegerField(validators=[MinValueValidator(100000)])
    state = models.CharField(max_length=255)
    image1 = models.ImageField(upload_to='house_images/')
    image2 = models.ImageField(upload_to='house_images/')
    image3 = models.ImageField(upload_to='house_images/', null=True, blank=True)
    image4 = models.ImageField(upload_to='house_images/', null=True, blank=True)
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Available")
    price = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.house_no} - {self.area} ({self.status})"


class BookingRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Booked', 'Booked'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="booking_requests")
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="bookings")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user.username} - {self.house.house_no} ({self.status})"


class HelpDeskModel(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="help_requests")
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="help_requests")
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="help_queries_received")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Help Request by {self.user.user.username} for {self.house.house_no}"


class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="received_messages")
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="house_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Message from {self.sender.user.username} to {self.receiver.user.username} about {self.house.house_no}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    booking = models.ForeignKey(BookingRequest, on_delete=models.CASCADE, related_name="payments")
    tenant = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="payments_made")
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="payments_received")
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2)  # 5% of amount
    amount_to_owner = models.DecimalField(max_digits=10, decimal_places=2)  # 95% of amount
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_month = models.CharField(max_length=20)  # e.g., "January 2023"
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment of ₹{self.amount} from {self.tenant.user.username} to {self.owner.user.username} for {self.booking.house.house_no}"
    
    def save(self, *args, **kwargs):
        # Calculate the platform fee (5%) and amount to owner (95%)
        if not self.platform_fee:
            self.platform_fee = self.amount * 0.05
            self.amount_to_owner = self.amount - self.platform_fee
        super().save(*args, **kwargs)
