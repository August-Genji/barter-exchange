from django import forms
from .models import ExchangeProposal, Ad


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'comment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['ad_sender'].queryset = Ad.objects.filter(user=user)
        self.fields['ad_sender'].label = "Ваше объявление"
        self.fields['comment'].label = "Комментарий к обмену"
