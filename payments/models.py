from django.db import models
from django.conf import settings
from teams.models import Team 
from authsystem.models import TimeStampedModel

class Payment(TimeStampedModel):
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    # ১. কোন টিমের জন্য পেমেন্ট হচ্ছে
    team = models.ForeignKey(
        Team, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    
    # ২. কোন মেম্বার/ইউজার পেমেন্টটি সম্পন্ন করছে (Paid By User ID & Name tracking)
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='payments_made'
    )

    # ৩. ট্রানজেকশন ট্র্যাকিং (SSLCommerz requirements)
    transaction_id = models.CharField(max_length=100, unique=True) # Tomar create kora unique ID
    val_id = models.CharField(max_length=100, null=True, blank=True) # SSLCommerz validation ID
    
    # ৪. টাকার পরিমাণ
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='BDT')
    
    # ৫. পেমেন্ট মেথড এবং প্রেরকের তথ্য (Sender Number Tracking)
    card_type = models.CharField(max_length=50, null=True, blank=True) # e.g., BKASH-Bkash, NAGAD-Nagad
    sender_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True, 
        help_text="Jei number theke payment kora hoyeche (e.g. 017XXXXXXXX)"
    )
    bank_tran_id = models.CharField(max_length=100, null=True, blank=True) # Gateway transaction ID
    
    # ৬. স্ট্যাটাস এবং সময়
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.team.name} - {self.amount} {self.currency} ({self.status})"
