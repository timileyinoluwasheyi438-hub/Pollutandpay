import uuid
from decimal import Decimal
from django.conf import settings
from django.db import models

# key, name, description, naira per tonne (edit here or move to a DB table later)
RATES = [
    ("hazardous", "Hazardous & chemical waste", "Corrosive, toxic, reactive or ignitable waste requiring controlled treatment.", 150000),
    ("ewaste", "Electronic waste", "End-of-life electrical and electronic equipment.", 120000),
    ("effluent", "Liquid effluent & sludge", "Treated and untreated effluent, sludge and oily water discharges.", 95000),
    ("industrial", "Industrial process waste", "Non-hazardous residues from manufacturing, mining and processing plants.", 80000),
    ("combustion", "Combustion & air emissions", "Ash, flue residues and combustion by-products from stacks and generators.", 70000),
    ("plastic", "Plastic & packaging waste", "Post-industrial plastics, films and packaging placed on the market.", 50000),
]
RATE_MAP = {k: Decimal(v) for k, _, _, v in RATES}


class Declaration(models.Model):
    UNPAID, SETTLED = "unpaid", "settled"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="declarations")
    ref = models.CharField(max_length=20, unique=True, editable=False)
    category = models.CharField(max_length=20, choices=[(k, n) for k, n, _, _ in RATES])
    facility = models.CharField(max_length=160)
    period_from = models.DateField()
    period_to = models.DateField()
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    notes = models.TextField(blank=True)
    levy = models.DecimalField(max_digits=14, decimal_places=2, editable=False, default=0)
    status = models.CharField(max_length=10, default=UNPAID)
    paystack_ref = models.CharField(max_length=80, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def save(self, *a, **kw):
        if not self.ref:
            self.ref = "PNP-" + uuid.uuid4().hex[:8].upper()
        self.levy = (self.quantity * RATE_MAP[self.category]).quantize(Decimal("0.01"))
        super().save(*a, **kw)

    def __str__(self):
        return self.ref
