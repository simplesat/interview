from django.contrib import admin


class ReadOnlyMixin:
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyModelAdmin(ReadOnlyMixin, admin.ModelAdmin):
    pass


class ReadOnlyTabularInline(ReadOnlyMixin, admin.TabularInline):
    extra = 0
