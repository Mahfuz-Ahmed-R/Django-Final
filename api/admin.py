from django.contrib import admin
from . import models

# Register your models here.
class ColorModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    list_display = ['name', 'slug']

class SizeModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    list_display = ['name', 'slug']

class CategoryModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    list_display = ['name', 'slug']

class SubCategoryModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
    list_display = ['name', 'slug']


admin.site.register(models.Color, ColorModelAdmin)
admin.site.register(models.Size, SizeModelAdmin)
admin.site.register(models.Category, CategoryModelAdmin)
admin.site.register(models.SubCategory, SubCategoryModelAdmin)
admin.site.register(models.Customer)
admin.site.register(models.InventoryModel)
admin.site.register(models.Product)
admin.site.register(models.Order)
admin.site.register(models.ReviewModel)
admin.site.register(models.OrderItem)
admin.site.register(models.ShippingAddress)
admin.site.register(models.WishListModel)
admin.site.register(models.MyOrdersModel)

