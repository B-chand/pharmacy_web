from django.contrib.auth.models import User
from .forms import RegisterForm
# ─── Registration ─────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, 'Account created successfully! Please sign in.')
        return redirect('login')
    return render(request, 'pharmacy/register.html', {'form': form})
"""
PharmaFlow Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, F
from django.urls import reverse
from django.utils import timezone

from .models import Medicine, Supplier, Customer, Purchase, Sale, ContactSubmission
from .forms import (
    LoginForm, MedicineForm, SupplierForm, CustomerForm,
    PurchaseForm, SaleForm, ContactForm
)


# ─── Auth ──────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f"Welcome back, {form.get_user().get_full_name() or form.get_user().username}!")
        return redirect(request.GET.get('next', 'home'))
    return render(request, 'pharmacy/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You've been signed out.")
    return redirect('login')


# ─── Dashboard / Home ──────────────────────────────────────────────────────────
@login_required
def home(request):
    today = timezone.now().date()
    ctx = {
        'total_medicines':  Medicine.objects.count(),
        'total_suppliers':  Supplier.objects.count(),
        'total_customers':  Customer.objects.count(),
        'total_sales':      Sale.objects.count(),
        'low_stock':        Medicine.objects.filter(stock__gt=0, stock__lte=20),
        'out_of_stock':     Medicine.objects.filter(stock=0),
        'expired':          Medicine.objects.filter(expiry_date__lt=today),
        'expiring_soon':    Medicine.objects.filter(
                                expiry_date__gte=today,
                                expiry_date__lte=today.replace(day=today.day)
                            ),
        'recent_sales':     Sale.objects.select_related('medicine', 'customer').order_by('-created')[:6],
        'recent_purchases': Purchase.objects.select_related('medicine', 'supplier').order_by('-created')[:6],
        'revenue_total':    Sale.objects.aggregate(t=Sum('total_price'))['t'] or 0,
        'purchase_total':   Purchase.objects.aggregate(t=Sum('total_price'))['t'] or 0,
    }
    return render(request, 'pharmacy/home.html', ctx)


# ─── Medicines ─────────────────────────────────────────────────────────────────
@login_required
def medicine_list(request):
    q        = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    status   = request.GET.get('status', '')
    qs       = Medicine.objects.select_related('supplier')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(category__icontains=q))
    if category:
        qs = qs.filter(category=category)
    today = timezone.now().date()
    if status == 'expired':
        qs = qs.filter(expiry_date__lt=today)
    elif status == 'low':
        qs = qs.filter(stock__gt=0, stock__lte=20)
    elif status == 'out':
        qs = qs.filter(stock=0)
    return render(request, 'pharmacy/medicine_list.html', {
        'medicines': qs,
        'q': q,
        'category': category,
        'status': status,
        'categories': Medicine.CATEGORY_CHOICES,
        'today': today,
    })


@login_required
def medicine_detail(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    return render(request, 'pharmacy/medicine_detail.html', {
        'med': med,
        'recent_sales': med.sales.select_related('customer').order_by('-sale_date')[:10],
        'recent_purchases': med.purchases.select_related('supplier').order_by('-purchase_date')[:10],
    })


@login_required
def medicine_add(request):
    form = MedicineForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        m = form.save()
        messages.success(request, f"'{m.name}' added to inventory.")
        return redirect('medicine_list')
    return render(request, 'pharmacy/medicine_form.html', {'form': form, 'title': 'Add Medicine', 'action': 'Add'})


@login_required
def medicine_edit(request, pk):
    med  = get_object_or_404(Medicine, pk=pk)
    form = MedicineForm(request.POST or None, instance=med)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"'{med.name}' updated.")
        return redirect('medicine_list')
    return render(request, 'pharmacy/medicine_form.html', {
        'form': form, 'title': f'Edit – {med.name}', 'action': 'Save Changes', 'med': med
    })


@login_required
def medicine_delete(request, pk):
    med = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        name = med.name
        med.delete()
        messages.success(request, f"'{name}' removed from inventory.")
        return redirect('medicine_list')
    return render(request, 'pharmacy/confirm_delete.html', {
        'object': med, 'type': 'Medicine', 'cancel_url': reverse('medicine_list')
    })


# ─── Suppliers ─────────────────────────────────────────────────────────────────
@login_required
def supplier_list(request):
    q  = request.GET.get('q', '').strip()
    qs = Supplier.objects.annotate(med_count=Count('medicines'))
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q))
    return render(request, 'pharmacy/supplier_list.html', {'suppliers': qs, 'q': q})


@login_required
def supplier_add(request):
    form = SupplierForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        s = form.save()
        messages.success(request, f"Supplier '{s.name}' added.")
        return redirect('supplier_list')
    return render(request, 'pharmacy/supplier_form.html', {'form': form, 'title': 'Add Supplier', 'action': 'Add'})


@login_required
def supplier_edit(request, pk):
    sup  = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=sup)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Supplier '{sup.name}' updated.")
        return redirect('supplier_list')
    return render(request, 'pharmacy/supplier_form.html', {
        'form': form, 'title': f'Edit – {sup.name}', 'action': 'Save Changes'
    })


@login_required
def supplier_delete(request, pk):
    sup = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = sup.name
        sup.delete()
        messages.success(request, f"Supplier '{name}' removed.")
        return redirect('supplier_list')
    return render(request, 'pharmacy/confirm_delete.html', {
        'object': sup, 'type': 'Supplier', 'cancel_url': reverse('supplier_list')
    })


# ─── Customers ─────────────────────────────────────────────────────────────────
@login_required
def customer_list(request):
    q  = request.GET.get('q', '').strip()
    qs = Customer.objects.annotate(sale_count=Count('sale'))
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(email__icontains=q) | Q(phone__icontains=q))
    return render(request, 'pharmacy/customer_list.html', {'customers': qs, 'q': q})


@login_required
def customer_add(request):
    form = CustomerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        c = form.save()
        messages.success(request, f"Customer '{c.name}' added.")
        return redirect('customer_list')
    return render(request, 'pharmacy/customer_form.html', {'form': form, 'title': 'Add Customer', 'action': 'Add'})


@login_required
def customer_edit(request, pk):
    cus  = get_object_or_404(Customer, pk=pk)
    form = CustomerForm(request.POST or None, instance=cus)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"Customer '{cus.name}' updated.")
        return redirect('customer_list')
    return render(request, 'pharmacy/customer_form.html', {
        'form': form, 'title': f'Edit – {cus.name}', 'action': 'Save Changes'
    })


@login_required
def customer_delete(request, pk):
    cus = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        name = cus.name
        cus.delete()
        messages.success(request, f"Customer '{name}' removed.")
        return redirect('customer_list')
    return render(request, 'pharmacy/confirm_delete.html', {
        'object': cus, 'type': 'Customer', 'cancel_url': reverse('customer_list')
    })


# ─── Purchases ─────────────────────────────────────────────────────────────────
@login_required
def purchase_list(request):
    qs = Purchase.objects.select_related('medicine', 'supplier').order_by('-purchase_date')
    return render(request, 'pharmacy/purchase_list.html', {
        'purchases': qs,
        'total': qs.aggregate(t=Sum('total_price'))['t'] or 0,
    })


@login_required
def purchase_add(request):
    form = PurchaseForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        p = form.save()
        messages.success(request, f"Purchase recorded: {p.quantity} × {p.medicine}")
        return redirect('purchase_list')
    return render(request, 'pharmacy/purchase_form.html', {'form': form, 'title': 'Record Purchase', 'action': 'Record'})


@login_required
def purchase_edit(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    form = PurchaseForm(request.POST or None, instance=purchase)
    if request.method == 'POST' and form.is_valid():
        updated_purchase = form.save()
        messages.success(request, f"Purchase updated: {updated_purchase.quantity} × {updated_purchase.medicine}")
        return redirect('purchase_list')
    return render(request, 'pharmacy/purchase_form.html', {
        'form': form,
        'title': f'Edit Purchase #{purchase.pk}',
        'action': 'Save Changes',
        'purchase': purchase,
    })


@login_required
def purchase_delete(request, pk):
    p = get_object_or_404(Purchase, pk=pk)
    if request.method == 'POST':
        # Reverse the stock addition
        Medicine.objects.filter(pk=p.medicine_id).update(stock=F('stock') - p.quantity)
        p.delete()
        messages.success(request, "Purchase record removed and stock adjusted.")
        return redirect('purchase_list')
    return render(request, 'pharmacy/confirm_delete.html', {
        'object': p, 'type': 'Purchase', 'cancel_url': reverse('purchase_list')
    })


# ─── Sales ─────────────────────────────────────────────────────────────────────
@login_required
def sale_list(request):
    qs = Sale.objects.select_related('medicine', 'customer').order_by('-sale_date')
    return render(request, 'pharmacy/sale_list.html', {
        'sales': qs,
        'total': qs.aggregate(t=Sum('total_price'))['t'] or 0,
    })


@login_required
def sale_add(request):
    form = SaleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        s = form.save()
        messages.success(request, f"Sale recorded: {s.quantity} × {s.medicine}")
        return redirect('sale_list')
    return render(request, 'pharmacy/sale_form.html', {'form': form, 'title': 'Record Sale', 'action': 'Record'})


@login_required
def sale_edit(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    form = SaleForm(request.POST or None, instance=sale)
    if request.method == 'POST' and form.is_valid():
        updated_sale = form.save()
        messages.success(request, f"Sale updated: {updated_sale.quantity} × {updated_sale.medicine}")
        return redirect('sale_list')
    return render(request, 'pharmacy/sale_form.html', {
        'form': form,
        'title': f'Edit Sale #{sale.pk}',
        'action': 'Save Changes',
        'sale': sale,
    })


@login_required
def sale_delete(request, pk):
    s = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        Medicine.objects.filter(pk=s.medicine_id).update(stock=F('stock') + s.quantity)
        s.delete()
        messages.success(request, "Sale record removed and stock restored.")
        return redirect('sale_list')
    return render(request, 'pharmacy/confirm_delete.html', {
        'object': s, 'type': 'Sale', 'cancel_url': reverse('sale_list')
    })


# ─── Contact ───────────────────────────────────────────────────────────────────
def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Your message has been received. We'll be in touch soon!")
        return redirect('contact')
    return render(request, 'pharmacy/contact.html', {'form': form})
