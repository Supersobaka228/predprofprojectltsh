from django.contrib import admin

from admin_main.models import BuyOrder, Notification


# Register your models here.
@admin.register(BuyOrder)
class BuyOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'items', 'summ', 'user_id', 'date')
    list_filter = ('id',)
    search_fields = ('summ', 'user_id')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass