from django.urls import path
from . import views as v

urlpatterns = [
    path("", v.page("home"), name="home"),
    path("about/", v.page("about"), name="about"),
    path("services/", v.page("services"), name="services"),
    path("sectors/", v.page("sectors"), name="sectors"),
    path("how-it-works/", v.page("how"), name="how"),
    path("rates/", v.page("rates"), name="rates"),
    path("contact/", v.contact, name="contact"),
    path("subscribe/", v.subscribe, name="subscribe"),
    path("dashboard/", v.dashboard, name="dashboard"),
    path("pay/callback/", v.pay_callback, name="pay_callback"),
    path("paystack/webhook/", v.paystack_webhook, name="paystack_webhook"),
    path("pay/<str:ref>/", v.pay, name="pay"),
]
