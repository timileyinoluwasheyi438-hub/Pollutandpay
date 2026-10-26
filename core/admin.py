from django.contrib import admin
from .models import Declaration

@admin.register(Declaration)
class DeclarationAdmin(admin.ModelAdmin):
    list_display = ("ref", "user", "category", "quantity", "levy", "status", "created")
    list_filter = ("status", "category")
    search_fields = ("ref", "user__email", "facility")
