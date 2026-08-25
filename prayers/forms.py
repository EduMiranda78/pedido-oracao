from django import forms

from .models import PrayerRequest


class PrayerRequestForm(forms.ModelForm):
    class Meta:
        model = PrayerRequest
        fields = [
            "requester_name",
            "requester_origin",
            "beneficiary_name",
            "prayer_text",
            "status",
            "is_reserved",
        ]

        widgets = {
            "requester_name": forms.TextInput(
                attrs={
                    "placeholder": "Nome da pessoa que fez o pedido",
                    "autocomplete": "name",
                }
            ),
            "requester_origin": forms.TextInput(
                attrs={
                    "placeholder": "Cidade, estado ou país",
                    "autocomplete": "address-level2",
                }
            ),
            "beneficiary_name": forms.TextInput(
                attrs={
                    "placeholder": "Nome da pessoa pela qual devemos orar",
                }
            ),
            "prayer_text": forms.Textarea(
                attrs={
                    "placeholder": "Descreva o pedido de oração",
                    "rows": 7,
                }
            ),
            "status": forms.Select(),
            "is_reserved": forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["requester_origin"].required = True
