from django.contrib import admin
from rango.models import Category, Page, UserProfile


# Register your models here.


# Class to modify the Category interface
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


# Class to modify the Page interface
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


# Update the model admin registrations
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
