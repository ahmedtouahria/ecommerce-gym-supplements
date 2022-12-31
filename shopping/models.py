from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from .utils import generate_barcode, generate_random_code, generate_transform_id
import random
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField

# get image path for regi
# ster files



class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('staff', True)
        extra_fields.setdefault('admin', True)
        extra_fields.setdefault('active', True)
        if extra_fields.get('staff') is not True:
            raise ValueError(_('Superuser must have staff=True.'))
        if extra_fields.get('admin') is not True:
            raise ValueError(_('Superuser must have admin=True.'))
        return self.create_user(email, password, **extra_fields)


class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True,null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,14}$', message="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=14,null=True,blank=True,)
    name=models.CharField(max_length=50,null=True,blank=True)
    image = models.ImageField(upload_to='customers/')
    code = models.CharField(max_length=12)
    point = models.IntegerField(default=0)
    profits = models.FloatField(default=0)
    is_receveur = models.BooleanField(default=False)
    number_of_referalls = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    created_at = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.code == '':
            code = generate_random_code()
            self.code = code
        if self.name=="" or self.name is None:
            self.name=str(self.email).split("@")[0]
        super().save(*args, **kwargs)  # Call the real save() method

    def get_full_name(self):
        return self.name

    def get_phone(self):
        return self.phone

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_active(self):
        return self.active


''' Images for banner area '''


class ImageBanner(models.Model):
    image =models.FileField('image or video ',upload_to='banners')


class Category(models.Model):
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200,null=True)
    image = ResizedImageField(force_format="WEBP",quality=75,upload_to='category/', null=True)

    def __str__(self):
        return self.name
    def category_sub(self):
        return self.sub_cat

class CategorySub(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    name_ar = models.CharField(max_length=200, null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='sub_cat')
    image = models.FileField(upload_to='category_sub/', null=True)
    description = models.TextField(_("description"),default="")
    def __str__(self):
        return self.name

    def count_sould(self):
        count_products_category = Product.objects.filter(
            category=self).aggregate(count_products=models.Sum("count_sould"))
        return count_products_category
    def count_product(self):
        return Product.objects.filter(category=self).count()

class Product(models.Model):
    STATUS_CHOICES=(('promotion','promotion'),('nouvelle','nouvelle'))
    name = models.CharField(max_length=200, unique=True)
    name_ar = models.CharField(max_length=200,blank=True,null=True)
    slug = models.SlugField(blank=True, null=True)
    category = models.ForeignKey(
        "shopping.CategorySub", on_delete=models.PROTECT, null=True, blank=True)
    price_achat = models.FloatField(
        verbose_name="prix d'achat", null=True, blank=True)
    price = models.FloatField(
        verbose_name="prix de vent", null=True, blank=True)
    date_add = models.DateTimeField(auto_now_add=True,null=True)
    price_promo = models.FloatField(verbose_name="prix de promotion", null=True, blank=True)
    profit = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=300)
    description_ar = models.CharField(max_length=300,null=True)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=200, blank=True, null=True,choices=STATUS_CHOICES)
    image =models.ImageField(_("image"), upload_to="products",)
    available = models.BooleanField(default=True)
    barcode_num = models.CharField(max_length=13, null=True, blank=True)
    count_sould = models.PositiveIntegerField(default=0)
    etage = models.CharField(max_length=50, null=True)
    reference = models.CharField(max_length=50 , blank=True, null=True)
    num_views = models.IntegerField("les vues",default=0)
    class Meta:
        ordering = ['-id']
    # override for save methde
    def save(self, *args, **kwargs):
        if self.barcode_num is None or self.barcode_num=='':
            self.barcode_num = generate_barcode()
        if self.profit is None:
            self.profit = self.price - self.price_achat
        if self.slug == "" or self.slug is None:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def no_of_ratings(self):
        ratings = Rating.objects.filter(product=self)
        return ratings.count()
    def avg_rating(self):
        # sum of ratings stars  / len of rating hopw many ratings
        sum = 0
        # no of ratings happened to the product
        ratings = Rating.objects.filter(product=self)
        for x in ratings:
            sum += x.stars

        if ratings.count() > 0:
            return int(sum / ratings.count())
        else:
            return 0      # no of ratings happened to the meal

    def __str__(self):
        return self.name



class Size(models.Model):
    size = models.CharField(max_length=5)
    def __str__(self):
        return self.size
    
class Color(models.Model):
    color = models.CharField(max_length=25)
    def __str__(self):
        return str(self.color)
class Variant(models.Model):
    product = models.ForeignKey("shopping.Product", on_delete=models.CASCADE, related_name="variant")
    size = models.ForeignKey("shopping.Size", on_delete=models.CASCADE)
    color = models.ForeignKey("shopping.Color", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price=models.FloatField(default=0)
    barcode_num = models.CharField(max_length=13, null=True, blank=True,unique=True)
    def __str__(self):
        return f"{self.product}-{self.color}-{self.size}"
    def save(self, *args, **kwargs):
        if self.barcode_num is None or self.barcode_num=='':
            self.barcode_num = generate_barcode()
        return super().save(*args, **kwargs)
class ProductImage(models.Model):
    product = models.ForeignKey("shopping.Product", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products')
    def __str__(self):
        return self.product.name

class ToastMessage(models.Model):
    title = models.CharField(max_length=50)
    product = models.ForeignKey("shopping.Product", verbose_name=(
        "produit"), on_delete=models.CASCADE)
    date_add = models.DateTimeField(("la date"), auto_now=True)

    def __str__(self):
        return self.product.name


class Affaire(models.Model):
    product = models.ForeignKey("shopping.Product", verbose_name=(
        "produit"), on_delete=models.CASCADE)
    date_end = models.DateTimeField(("la date TERMINE "), auto_now=False)
    def get_time(self):
        time_remaining = {"days": 0, "hours": 0, "minuts": 0, "seconds": 0}
        time_taking = self.date_end-timezone.now()
        time_in_seconds = time_taking.total_seconds()
        get_days = time_taking.days
        time_remaining["days"] = get_days
        time_remaining["hours"] = int(
            (int(time_in_seconds)-int(get_days)*86400)/3600)
        time_remaining["minuts"] = int(
            (int(time_in_seconds)-int(get_days)*86400 - time_remaining["hours"]*3600)/60)
        time_remaining["seconds"] = int((int(time_in_seconds)-int(
            get_days)*86400 - time_remaining["hours"]*3600 - time_remaining["minuts"]*60))
        return time_remaining
    def get_time(self):
        time_taking = self.date_end
        time_in_seconds = time_taking.timestamp()
        return time_in_seconds
    def test_affaire_existed(self):
        time_taking = self.date_end-timezone.now()
        time_in_seconds = time_taking.total_seconds()
        return True if time_in_seconds > 0 else False
    def __str__(self):
        return self.product.name


''' -------- PRODUCT LOGIC ----------- '''

''' -------- Order LOGIC ----------- '''


class Order(models.Model):
    STATUS = [
        ('Ordered', 'Commandé'),
        ('Processed', 'Traité'),
        ('Shipped', 'Expédié'),
        ('Delivered', 'Livré'),
    ]
    STATUS_AR = [
        ('Ordered', 'استقبال'),
        ('Processed', 'معالجة'),
        ('Shipped', 'يتم الشحن'),
        ('Delivered', 'تم الشحن'),
    ]
    customer = models.ForeignKey(
        "shopping.Customer", on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=20)
    recommended_by = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, related_name="recommended_by")
    status = models.CharField(
        max_length=100, choices=STATUS, default='Ordered')
    status_ar = models.CharField(
        max_length=100, choices=STATUS_AR, default='Ordered')
    confirmed = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    def get_date_french(self):
        months_french = ("Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre")
        return f" {self.date_ordered.day} {months_french[self.date_ordered.month-1]} {self.date_ordered.year} "
    def get_date_arabic(self):
        months_french = ("جانفي"," فيفري","مارس","أفريل","ماي","جوان","جويلية","أوت","سبتمبر","أكتوبر","نوفمبر","ديسمبر")
        return f" {self.date_ordered.day} {months_french[self.date_ordered.month-1]} {self.date_ordered.year} "
    def customer_number(self):
        return self.customer.phone

    def save(self, *args, **kwargs):
        if self.transaction_id == '':
            transaction_id = generate_transform_id()
            self.transaction_id = transaction_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer}-{self.id}"

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def getItems(self):
        order_items = OrderItem.object.filter(order=self)
        return order_items

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    @property
    def get_customer_phone(self):
        return ShippingAddress.objects.filter(order=self).last().phone

class Rating(models.Model):
    user = models.ForeignKey(
        "shopping.Customer", on_delete=models.CASCADE, related_name="rate")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)],null=True)
    content = models.TextField(null=True)
    def get_user_name(self):
        return self.user.name

    class Meta:
        '''1 user---> comment 1 comment '''
        unique_together = (('user', 'product'),)
        index_together = (('user', 'product'),)
    def __str__(self):
        return f"{self.user} rate {self.stars} to {self.product.name}"


class OrderItem(models.Model):
    product = models.ForeignKey("shopping.Product", on_delete=models.PROTECT, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    color = models.CharField(max_length=50, null=True)
    size = models.CharField(max_length=50, null=True)

    def __str__(self):
        return f"{self.order}"

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        "shopping.Customer", on_delete=models.SET_NULL, null=True)
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True,related_name='order')
    name = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=14, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    is_stopdesk = models.BooleanField(default=True, null=True)
    def __str__(self):
        return f'{self.order}'


class Favorite(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='favore')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now=True)

    class Meta:
        # to insure the user favore product one time
        unique_together = (('customer', 'product'),)
        index_together = (('customer', 'product'),)


class Conversion(models.Model):
    receveur = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='converte')
    money = models.FloatField()
class Section(models.Model):
    category=models.ForeignKey("shopping.CategorySub",on_delete=models.CASCADE)
    def products(self):
        return Product.objects.filter(category=self.category).order_by('-date_add')[:12]
    def __str__(self):
        return self.category.name
    