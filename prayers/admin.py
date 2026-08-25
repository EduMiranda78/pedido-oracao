from django.contrib import admin

from .models import PrayerAudit, PrayerRequest


@admin.register(PrayerRequest)
class PrayerRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "requester_name",
        "requester_origin",
        "beneficiary_name",
        "status",
        "is_reserved",
        "created_by",
    )

    list_filter = (
        "status",
        "is_reserved",
        "created_at",
    )

    search_fields = (
        "requester_name",
        "requester_origin",
        "beneficiary_name",
        "prayer_text",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "closed_at",
    )


@admin.register(PrayerAudit)
class PrayerAuditAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "prayer_request",
        "action",
        "user",
        "created_at",
    )

    readonly_fields = (
        "prayer_request",
        "user",
        "action",
        "changes",
        "created_at",
    )
