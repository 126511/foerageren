from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.db import models

STATUS = (
    (1, ("In afwachting")),
    (2, ("Goedgekeurd")),
    (3, ("Geannuleerd")),  
)

PERMISSION = (
    (1, ("Admin")),
    (2, ("Manager")),
    (3, ("Gebruiker")),
    (4, ("Verbannen")),
)

from versatileimagefield.fields import VersatileImageField

class Brand(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="Groepsnaam")
    members = models.ManyToManyField(User, through='Permission')
    is_official = models.BooleanField(default=False)
    description = models.TextField
    image = VersatileImageField('Afbeelding', upload_to='images/group/',null=True,blank=True)
    is_open = models.BooleanField(default=False, verbose_name="Ik wil dat iedereen zich bij mijn groep kan aansluiten")

    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    name = models.CharField(max_length=255,verbose_name="Naam")
    price = models.FloatField(default=.5,verbose_name="Prijs")
    stock = models.IntegerField(default=0)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} bij {self.group}"

    def save(self, *args, **kwargs):
        return super(Product, self).save(*args, **kwargs)  

class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user} has €{self.balance} for {self.group}"

class Prepaid(models.Model):
    buyer = models.ForeignKey(User, verbose_name = "Koper", on_delete=models.PROTECT)
    amount = models.FloatField(verbose_name = "Aantal euro's")
    added_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.processed == False and self.amount:

            self.processed = True
            b = Balance.objects.filter(user=self.buyer, group=self.group)
            if not b:
                new = Balance(user=self.buyer, balance=self.amount, group=self.group)
                new.save()
            else:
                b = b.first()
                b.balance = b.balance + self.amount
                b.save()
        return super(Prepaid, self).save(*args, **kwargs)    

    def delete(self):
        p = Balance.objects.get(user=self.buyer, group=self.group)
        p.balance = p.balance - self.amount
        p.save()        
        super(Prepaid, self).delete()

    def __str__(self):
        return f"{self.buyer} has bought €{self.amount} for {self.group}"

class Sale(models.Model):
    cashier = models.ForeignKey(User,related_name="cashier", on_delete=models.PROTECT)
    buyer = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.FloatField(null=True,blank=True)
    amount = models.FloatField()
    sum = models.FloatField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.price = self.product.price
        p, created = Balance.objects.get_or_create(user=self.buyer, group=self.group)
        p.balance = p.balance - (self.amount * self.price)
        p.save()
        s = self.product
        s.stock = s.stock - self.amount
        s.save()

        return super(Sale, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.buyer} bought {str(self.amount)} {self.product} at {self.added_at}"

    def delete(self):
        p = Profile.objects.get(user=self.buyer)
        p.balance = p.balance + (self.amount * self.price)
        p.save()
        s = Stock.objects.get(product=self.product)
        s.amount = s.amount + self.amount
        s.save()   
        super(Sale, self).delete()

    def product_sum(self):
        from django.db.models import Sum
        return Sale.objects.filter(buyer=self.buyer,added_at__lt=self.added_at).aggregate(Sum('amount'))

class Stock(models.Model):
    product = models.ForeignKey(Product,related_name="product_stock", on_delete=models.CASCADE)
    amount = models.FloatField(verbose_name = "Aantal")
    #price = models.FloatField(verbose_name = "Inkoopprijs per stuk")
    added_at = models.DateTimeField(auto_now_add=True)

class Badge(models.Model):
    name = models.CharField(max_length=200, default='' , verbose_name = "Titel")
    slug = models.CharField(max_length=200, default='' , verbose_name = "slug")
    message = models.TextField()
    product = models.ForeignKey(Product,verbose_name="Betreffend product", on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="Afbeelding")

    def __str__(self):
        return self.name

class User_badge(models.Model):
    added_at = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.badge.name

class Permission(models.Model):
    permission = models.IntegerField(choices=PERMISSION, default=3)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def verbose_permission(self):
        return f"{PERMISSION[self.permission - 1][-1]}"

    def __str__(self):
        return f"{self.user} is {PERMISSION[self.permission - 1][-1]} for {self.group}"

class Invite(models.Model):
    key = models.CharField(max_length=16, default="3nSsi3ncivi3v98b", unique=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.requested_by} invited for {self.group}"

class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS, default=1) 
    intro_completed = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True, null=True, blank=True) 
    slug = models.SlugField(max_length=255,blank=True)
    image = VersatileImageField( 'Image', upload_to='images/profile/',null=True,blank=True)
    last_update = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=200, default='' ,verbose_name = "Voornaam")
    last_name = models.CharField(max_length=200, default='',verbose_name = "Achternaam")  
    birth = models.DateField(verbose_name = "Geboortedatum", blank=True,null=True)
    tel = models.CharField(max_length=10, validators=[RegexValidator(regex='^((06){1}[1-9]{1}[0-9]{7})$', message='Het telefoonnummer moet 10 cijfers bevatten en beginnen met "06".', code='nomatch')], blank=True,verbose_name = "Mobiel Telefoonnummer (0612345678)")
    balance = models.FloatField(default=0)
    current_group = models.ForeignKey(Group, on_delete=models.PROTECT, blank=True, null=True)

    def get_absolute_url(self):
        return "/profiel/"+str(self.slug)+"/"

    def __str__(self):
        if self.first_name and self.last_name:
            return self.first_name +' '+ self.last_name[:1]
        elif self.first_name:
            return self.first_name
        else:
            return str(self.user)

def is_manager(self):
    profile = Profile.objects.get(user=self)
    p = Permission.objects.get(user=self, group=profile.current_group)
    if p.permission < 3:
        return True
    return False

def current_group(self):
    profile = Profile.objects.get(user=self)
    return profile.current_group

def balance(self):
    profile = Profile.objects.get(user=self)
    current_group = profile.current_group
    b = Balance.objects.filter(user=self, group=current_group)
    if not b:
        return 0
    return float(b.first().balance)

from django.contrib import auth
auth.models.User.add_to_class('is_manager', is_manager)
auth.models.User.add_to_class('current_group', current_group)
auth.models.User.add_to_class('balance', balance)