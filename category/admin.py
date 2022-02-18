from django.contrib import admin
from .models import Category
# Register your models here.
# if we want the model appear inside the admin panel, register the model here



class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

admin.site.register(Category, CategoryAdmin)
