from django.db import models

# Create your models here.


class Users(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=50)
    status = models.IntegerField(default=1)
    class Meta:
        db_table='users'



class Department(models.Model):
    dept_name = models.CharField(max_length=255)
    status = models.IntegerField(default=1)
    created_datetime = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='department'


class Products(models.Model):
    productname = models.CharField(max_length=255)
    price = models.IntegerField(default=1)
    imagepath = models.ImageField(upload_to='uploads/product-image/')
    status = models.IntegerField(default=1)
    created_datetime = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='products'


class Students(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15)
    email = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    status = models.IntegerField(default=1)
    created_datetime = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table='students'

class Order_conf(models.Model):
    students = models.ForeignKey(Students,on_delete=models.CASCADE)
    total_amt = models.DecimalField(max_digits=10, decimal_places=2)
    gst_amt = models.DecimalField(max_digits=10, decimal_places=2)
    net_amt = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(default=1)
    created_datetime = models.DateTimeField(auto_now_add=True)
    modified_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        db_table="order_confirmation"


class Order_products(models.Model):
    order_confirmation = models.ForeignKey(Order_conf , on_delete=models.CASCADE)
    products=models.ForeignKey(Products,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.IntegerField(default=1)
    gst_per = models.IntegerField()
    gst_amt=models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_datetime=models.DateTimeField(auto_now=True)
    modified_datetime=models.DateTimeField(auto_now=True)

    class Meta:
        db_table="order_products"



    
