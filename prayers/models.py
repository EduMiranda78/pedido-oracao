from django.conf import settings
from django.db import models
from django.utils import timezone


class PrayerRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Novo"
        PRAYING = "praying", "Em oração"
        CLOSED = "closed", "Encerrado"

    requester_name = models.CharField(
        "Nome de quem pede",
        max_length=150,
    )

    requester_origin = models.CharField(
        "De onde é?",
        max_length=150,
        blank=True,
        default="",
        help_text="Cidade, estado ou país de quem fez o pedido.",
    )

    beneficiary_name = models.CharField(
        "Para quem devemos orar?",
        max_length=150,
    )

    prayer_text = models.TextField(
        "Pedido de oração",
    )

    status = models.CharField(
        "Status",
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True,
    )

    is_reserved = models.BooleanField(
        "Pedido reservado",
        default=False,
        db_index=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Cadastrado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prayer_requests",
    )

    created_at = models.DateTimeField(
        "Data do registro",
        auto_now_add=True,
        db_index=True,
    )

    updated_at = models.DateTimeField(
        "Última atualização",
        auto_now=True,
    )

    closed_at = models.DateTimeField(
        "Data de encerramento",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Pedido de oração"
        verbose_name_plural = "Pedidos de oração"

    def __str__(self):
        return f"Pedido #{self.pk} - {self.beneficiary_name}"

    def sync_closed_at(self):
        if self.status == self.Status.CLOSED:
            if not self.closed_at:
                self.closed_at = timezone.now()
        else:
            self.closed_at = None


class PrayerAudit(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Criado"
        UPDATED = "updated", "Alterado"

    prayer_request = models.ForeignKey(
        PrayerRequest,
        on_delete=models.CASCADE,
        related_name="audit_entries",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    action = models.CharField(
        max_length=20,
        choices=Action.choices,
    )

    changes = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.prayer_request_id} - {self.get_action_display()}"
