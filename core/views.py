import hashlib, hmac, json, uuid
import requests
import resend
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import escape
from django.views.decorators.http import require_POST
from .models import RATES, Declaration

PAYSTACK = "https://api.paystack.co/transaction"


def notify(subject, html):
    """Email the operator via Resend. Never breaks the request."""
    try:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({"from": settings.MAIL_FROM, "to": [settings.NOTIFY_EMAIL], "subject": subject, "html": html})
    except Exception:
        pass


class DeclarationForm(forms.ModelForm):
    class Meta:
        model = Declaration
        fields = ["category", "facility", "period_from", "period_to", "quantity", "notes"]
        widgets = {"period_from": forms.DateInput(attrs={"type": "date"}),
                   "period_to": forms.DateInput(attrs={"type": "date"}),
                   "notes": forms.Textarea(attrs={"rows": 2})}


def page(template):
    return lambda request: render(request, f"core/{template}.html")


def contact(request):
    if request.method == "POST":
        n, e, m = (escape(request.POST.get(k, "")) for k in ("name", "email", "message"))
        notify(f"Website enquiry from {n}", f"<p><b>{n}</b> ({e})</p><p>{m}</p>")
        messages.success(request, "Message sent. We will reply by email.")
        return redirect("contact")
    return render(request, "core/contact.html")


@require_POST
def subscribe(request):
    notify("Newsletter signup", f"<p>{escape(request.POST.get('email', ''))}</p>")
    messages.success(request, "Subscribed. Thank you.")
    return redirect(request.META.get("HTTP_REFERER", "/"))


@csrf_exempt
@require_POST
def paystack_webhook(request):
    sig = request.headers.get("x-paystack-signature", "")
    calc = hmac.new(settings.PAYSTACK_SECRET_KEY.encode(), request.body, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(sig, calc):
        return HttpResponse(status=400)
    ev = json.loads(request.body)
    if ev.get("event") == "charge.success":
        Declaration.objects.filter(paystack_ref=ev["data"]["reference"]).update(status="settled")
    return HttpResponse(status=200)


@login_required
def dashboard(request):
    form = DeclarationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        d = form.save(commit=False)
        d.user = request.user
        d.save()
        notify(f"New declaration {d.ref}", f"<p>{escape(request.user.email)} filed {d.ref}: {d.get_category_display()}, {d.quantity} t, levy ₦{d.levy}.</p>")
        messages.success(request, f"Declaration {d.ref} filed. Pay the levy to settle it.")
        return redirect("dashboard")
    qs = request.user.declarations.all()
    paid = qs.filter(status="settled").aggregate(s=Sum("levy"))["s"] or 0
    due = qs.filter(status="unpaid").aggregate(s=Sum("levy"))["s"] or 0
    return render(request, "core/dashboard.html", {"form": form, "items": qs, "count": qs.count(), "paid": paid, "due": due,
                                                   "rates": {k: r for k, _, _, r in RATES}})


@login_required
@require_POST
def pay(request, ref):
    d = get_object_or_404(Declaration, ref=ref, user=request.user, status="unpaid")
    r = requests.post(f"{PAYSTACK}/initialize", timeout=20,
                      headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"},
                      json={"email": request.user.email, "amount": int(d.levy * 100),
                            "reference": f"{d.ref}-{uuid.uuid4().hex[:6]}",
                            "callback_url": request.build_absolute_uri("/pay/callback/")}).json()
    if r.get("status"):
        d.paystack_ref = r["data"]["reference"]
        d.save(update_fields=["paystack_ref"])
        return redirect(r["data"]["authorization_url"])
    messages.error(request, "Could not start payment. Try again.")
    return redirect("dashboard")


@login_required
def pay_callback(request):
    ref = request.GET.get("reference", "")
    r = requests.get(f"{PAYSTACK}/verify/{ref}", timeout=20,
                     headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}).json()
    d = Declaration.objects.filter(paystack_ref=ref, user=request.user).first()
    if d and r.get("data", {}).get("status") == "success":
        d.status = "settled"
        d.save(update_fields=["status"])
        notify(f"Levy paid {d.ref}", f"<p>{escape(request.user.email)} paid ₦{d.levy} for {d.ref}.</p>")
        messages.success(request, f"{d.ref} settled. Thank you.")
    else:
        messages.error(request, "Payment not confirmed.")
    return redirect("dashboard")
