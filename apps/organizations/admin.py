from django.contrib import admin
from .models import Organization, Branch


# Register your models here.
class BranchInline(admin.TabularInline):
    model = Organization
    fk_name = "parent"
    extra = 1
    verbose_name = "Branch"
    verbose_name_plural = "Branches"
    fields = ("name", "description")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "branch_count", "created_at", "updated_at")
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = [BranchInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(parent__isnull=False)

    def branch_count(self, obj):
        return obj.branches.count()

    branch_count.short_description = "Branches"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj or obj.parent is None:
            if "parent" in form.base_fields:
                form.base_fields.pop("parent")
        return form
    
    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by:
            obj.created_by = request.user
            obj.updated_by = request.user
        elif change:
            obj.updated_by = request.user

        super().save_model(request, obj, form, change)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent", "created_at", "updated_at")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("parent",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(parent__isnull=True)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "parent" in form.base_fields:
            form.base_fields["parent"].required = True
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Organization.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
