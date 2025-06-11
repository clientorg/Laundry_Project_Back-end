from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Order(models.Model):
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    status = models.CharField(max_length=50)
    data = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.order_id:
            last_order = Order.objects.order_by("-id").first()
            next_id = 1 if not last_order else last_order.id + 1
            self.order_id = f"ORD{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} by {self.user}"
