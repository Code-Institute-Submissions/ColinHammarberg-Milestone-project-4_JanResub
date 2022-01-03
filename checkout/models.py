import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django_countries.fields import CountryField
from products.models import Product
from profiles.models import UserAccount


charity = (
    ('Star_for_life', 'Star For Life'),
    ('Unicef', 'Unicef'),
    ('Red_Cross', 'Red Cross'),
    ('Oceana', 'Oceana'),
    ('Plastic_Ocean_Foundation', 'Plastic Ocean Foundation'),
)


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    user_account = models.ForeignKey(
        UserAccount, on_delete=models.SET_NULL, 
        null=True, related_name='orders')
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    country = CountryField(blank_label='Country', null=False, blank=False)
    postcode = models.CharField(max_length=20, null=False, blank=False)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address = models.CharField(max_length=80, null=False, blank=False)
    county = models.CharField(max_length=80, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, 
        null=False, default=0)
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, 
        null=False, default=0)
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, 
        null=False, default=0)
    charity = models.CharField(
        max_length=24, null=False, blank=False, choices=charity, 
        default='Star_For_life')

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def total_order(self):
        """
        Updating grand total.
        """
        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum']
        self.delivery_cost = self.order_total * settings.\
            STANDARD_DELIVERY_PERCENTAGE / 100
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, null=False, blank=False, 
        on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(
        Product, null=False, blank=False, 
        on_delete=models.CASCADE)
    product_size = models.CharField(max_length=2, null=True, blank=True)
    quantity = models.IntegerField(
        null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(
        max_digits=6, decimal_places=2, 
        null=False, blank=False, editable=False)
    has_sizes = models.BooleanField(default=False, null=True, blank=True)
    charity = models.CharField(
        max_length=24, choices=charity, 
        default='Star_For_life')

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'
    
        