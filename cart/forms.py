from django import forms
from  accounts.models import Address

class CheckoutForm(forms.Form):
    # Choice field for existing addresses, populated dynamically
    saved_address = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Use a new address",
        widget=forms.RadioSelect
    )

    # Fields for new address entry (shown if user chooses new address)
    full_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)
    address_line_1 = forms.CharField(max_length=255, required=False)
    address_line_2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=100, required=False)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate saved_address queryset with user's addresses
        self.fields['saved_address'].queryset = Address.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        saved_address = cleaned_data.get('saved_address')

        # If no saved address selected, ensure new address fields are filled
        if not saved_address:
            required_fields = ['full_name', 'phone', 'address_line_1','address_line_2', 'city', 'state', 'postal_code', 'country']
            missing = [field for field in required_fields if not cleaned_data.get(field)]
            if missing:
                raise forms.ValidationError(f"Please fill all required fields for new address: {', '.join(missing)}")
        return cleaned_data
