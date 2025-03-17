from django.contrib import admin
from .models import CountryRate, UserBalance, EarningRecord, PaymentTransaction, PaymentSetting

@admin.register(CountryRate)
class CountryRateAdmin(admin.ModelAdmin):
    list_display = ('country_code', 'country_name', 'rate_per_click')
    search_fields = ('country_code', 'country_name')
    ordering = ('country_name',)

@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'last_updated')
    search_fields = ('user__username', 'user__email')
    ordering = ('-amount',)

@admin.register(EarningRecord)
class EarningRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'url', 'country', 'amount', 'timestamp')
    list_filter = ('country', 'timestamp')
    search_fields = ('user__username', 'country', 'url__short_code')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'payment_method', 'timestamp')
    list_filter = ('status', 'payment_method', 'timestamp')
    search_fields = ('user__username', 'transaction_id')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    actions = ['mark_as_completed', 'mark_as_failed']

    def mark_as_completed(self, request, queryset):
        queryset.update(status=PaymentTransaction.COMPLETED)
    mark_as_completed.short_description = "Mark selected transactions as completed"

    def mark_as_failed(self, request, queryset):
        queryset.update(status=PaymentTransaction.FAILED)
    mark_as_failed.short_description = "Mark selected transactions as failed"

@admin.register(PaymentSetting)
class PaymentSettingAdmin(admin.ModelAdmin):
    list_display = ('min_withdrawal_amount', 'default_rate', 'is_payment_active')

    def has_add_permission(self, request):
        # Only allow one instance of payment settings
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)