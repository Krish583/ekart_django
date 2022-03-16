from django.contrib import admin
from .models import Product,Variation
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable=('is_active',) # to edit the filed in the main UI
    list_filter=('product', 'variation_category', 'variation_value', 'is_active')


admin.site.register(Product,ProductAdmin) # if you dont write this admin.sire command, this product module wont appear in the admin module
admin.site.register(Variation,VariationAdmin)
