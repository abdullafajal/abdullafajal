from django import forms

class ContactForm(forms.Form):
    """
    A form for users to send a message from the contact page.
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'})
    )
    subject = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject (optional)'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5})
    )
