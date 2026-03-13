from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Medicine, Supplier, Customer, Purchase, Sale, ContactSubmission

# ── Shared widget helpers ─────────────────────────────────────────────────────
def ctrl(placeholder='', type_='text', extra=''):
    attrs = {'class': 'form-control', 'placeholder': placeholder}
    if type_ != 'text':
        attrs['type'] = type_
    return forms.TextInput(attrs=attrs)

def select():
    return forms.Select(attrs={'class': 'form-select'})

def textarea(rows=3, placeholder=''):
    return forms.Textarea(attrs={'class': 'form-control', 'rows': rows, 'placeholder': placeholder})


# ── Auth ──────────────────────────────────────────────────────────────────────
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Username',
        'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Password',
    }))


# ── Supplier ──────────────────────────────────────────────────────────────────
class SupplierForm(forms.ModelForm):
    class Meta:
        model  = Supplier
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company or person name'}),
            'phone':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 555 000 0000'}),
            'email':   forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contact@supplier.com'}),
            'address': textarea(3, 'Street, City, Country'),
        }


# ── Medicine ──────────────────────────────────────────────────────────────────
class MedicineForm(forms.ModelForm):
    class Meta:
        model  = Medicine
        fields = ['name', 'category', 'stock', 'price', 'expiry_date', 'supplier']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medicine name'}),
            'category':    select(),
            'stock':       forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'price':       forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier':    select(),
        }


# ── Customer ──────────────────────────────────────────────────────────────────
class CustomerForm(forms.ModelForm):
    class Meta:
        model  = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'phone':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 555 000 0000'}),
            'email':   forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'patient@email.com'}),
            'address': textarea(3, 'Street, City, Country'),
        }


# ── Purchase ──────────────────────────────────────────────────────────────────
class PurchaseForm(forms.ModelForm):
    class Meta:
        model  = Purchase
        fields = ['medicine', 'supplier', 'quantity', 'total_price', 'purchase_date', 'notes']
        widgets = {
            'medicine':      select(),
            'supplier':      select(),
            'quantity':      forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total_price':   forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes':         textarea(2, 'Optional notes…'),
        }


# ── Sale ──────────────────────────────────────────────────────────────────────
class SaleForm(forms.ModelForm):
    class Meta:
        model  = Sale
        fields = ['medicine', 'customer', 'quantity', 'total_price', 'sale_date', 'notes']
        widgets = {
            'medicine':   select(),
            'customer':   select(),
            'quantity':   forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total_price':forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'sale_date':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes':      textarea(2, 'Optional notes…'),
        }

    def clean(self):
        cleaned = super().clean()
        medicine = cleaned.get('medicine')
        quantity = cleaned.get('quantity')
        if medicine and quantity:
            available_stock = medicine.stock
            if self.instance.pk and self.instance.medicine_id == medicine.pk:
                available_stock += self.instance.quantity
            if quantity > available_stock:
                raise forms.ValidationError(
                    f"Insufficient stock. Only {available_stock} units of '{medicine.name}' available."
                )
        return cleaned


# ── Contact ───────────────────────────────────────────────────────────────────
class ContactForm(forms.ModelForm):
    class Meta:
        model  = ContactSubmission
        fields = ['name', 'email', 'message']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'email':   forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'message': textarea(5, 'Your message…'),
        }
