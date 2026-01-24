from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BalanceTopUp


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Поля для отображения в списке
    list_display = ('email', 'first_name', 'last_name', 'role', 'grade', 'balance_cents', 'balance_rub_display', 'is_active', 'is_staff')
    list_filter = ('role', 'grade', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone', 'grade')
    ordering = ('grade', 'last_name', 'first_name')
    readonly_fields = ('date_joined', 'last_login', 'id', 'balance_rub_display')

    # Поля для просмотра/редактирования пользователя
    fieldsets = (
        (None, {'fields': ('email', 'password', 'id')}),
        (('Персональная информация'), {
            'fields': ('first_name', 'last_name', 'phone', 'grade')
        }),
        (('Роли и права'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (('Дополнительная информация'), {
            'fields': ('balance_cents', 'balance_rub_display', 'abonement', 'not_like')
        }),
        (('Важные даты'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Поля для создания пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone'),
        }),
    )

    # Настройка фильтра по горизонтали для групп и прав
    filter_horizontal = ('groups', 'user_permissions',)


    # Метод для отображения полного имени в админке
    def full_name(self, obj):
        return f"{obj.last_name} {obj.username}"

    full_name.short_description = ('Полное имя')
    full_name.admin_order_field = 'last_name'

    def balance_rub_display(self, obj):
        return obj.balance_rub_str

    balance_rub_display.short_description = 'Баланс (₽)'


@admin.register(BalanceTopUp)
class BalanceTopUpAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_cents', 'created_at', 'created_by', 'comment')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__username', 'comment')
    readonly_fields = ('created_at',)
