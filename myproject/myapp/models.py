# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class Make(models.Model):
    """The Make model."""
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False,blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True, blank=True)
    name = models.CharField(max_length=100, null=False, unique=True)

class Model(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False,blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True, blank=True)
    name = models.CharField(max_length=100, null=False, unique=True)
    make = models.ForeignKey(Make)

class VehicleInfo(models.Model):
    """The VehicleInfo model."""
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False,blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True, blank=True)
    vin = models.CharField(max_length=17, null=False, unique=True)
    make = models.ForeignKey(Make)
    model = models.ForeignKey(Model)
    year = models.IntegerField()

class UserInfo(User):
    """The UserInfo model."""
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False,blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True, blank=True)
    dealership = models.CharField(max_length=100, null=True)
    location = models.TextField(max_length=100, null=False, blank=True)

class SaleInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False,blank=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True, blank=True)
    price = models.FloatField()
    sale_date = models.DateTimeField(auto_now_add=True, auto_now=False,blank=True)
    vehicle = models.ForeignKey(VehicleInfo)
    buyer = models.ForeignKey(User, related_name='buyer')
    seller = models.ForeignKey(User, related_name='seller')

    class Meta:
    	unique_together = ('vehicle', 'buyer','seller',)
