from . import content as c
from .models import RATES

def site(request):
    return {**{k: getattr(c, k) for k in dir(c) if k.isupper()},
            "RATES_LIST": [dict(name=n, desc=d, rate=r) for _, n, d, r in RATES]}
