from django.db import models
from django.urls import reverse
# Create your models here.
class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug=models.SlugField(max_length=100,unique=True)
    description=models.TextField(max_length=255, blank=True)
    cat_image=models.ImageField(upload_to='photos/categories', blank=True) # blank is true means it is optional

    # in admin panel, category plural will be displayed as categorys which is not correct. So, we are using verbose_name in Meta class
    class Meta:
        verbose_name='cateogory'
        verbose_name_plural='categories'

    def get_url(self):
        return reverse('products_by_category',args=[self.slug])
    def __str__(self):
        return self.category_name
