from django.contrib import admin

from admin_main.models import BuyOrder, Notification


# Register your models here.
@admin.register(BuyOrder)
class BuyOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'items', 'summ', 'user_id', 'date')
    list_filter = ('id',)
    search_fields = ('summ', 'user_id')
    fields = ('items', 'user_id', 'summ', 'date', 'status')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient_type', 'recipient_user', 'title', 'created_at')
    list_filter = ('recipient_type', 'created_at')
    search_fields = ('title', 'body')
    fields = (
        'recipient_type',
        'recipient_user',
        'title',
        'body',
        'created_at',
    )
    readonly_fields = ('created_at',)
