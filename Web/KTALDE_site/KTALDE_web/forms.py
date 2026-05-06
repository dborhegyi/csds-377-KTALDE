from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import Lampi, get_parked_user


class AddLampiForm(forms.Form):
    association_code = forms.CharField(label="Association Code", min_length=6,
                                       max_length=6)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super(AddLampiForm, self).clean()
        code = cleaned_data.get('association_code')
        if not code:
            return cleaned_data
        
        print("received form with code {}".format(code))
        
        # look up device with association code
        parked_user = get_parked_user()
        devices = Lampi.objects.filter(
            user=parked_user,
            association_code__startswith=code)
        
        if not devices:
            self.add_error('association_code',
                           ValidationError("Invalid Association Code",
                                           code='invalid'))
        else:
            cleaned_data['device'] = devices[0]
        
        return cleaned_data
