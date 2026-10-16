from django.contrib import admin
from .models import ExpenseCategory, Expense

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active", "organization", "created_at"]
    search_fields = ["name"]
    list_filter = ["is_active"]

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["expense_no", "category", "amount", "expense_date", "payment_mode", "organization"]
    search_fields = ["expense_no", "description"]
    list_filter = ["payment_mode", "category", "expense_date"]
