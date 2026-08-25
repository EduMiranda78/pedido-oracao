from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("prayers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="prayerrequest",
            name="requester_origin",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Cidade, estado ou país de quem fez o pedido.",
                max_length=150,
                verbose_name="De onde é?",
            ),
        ),
    ]
