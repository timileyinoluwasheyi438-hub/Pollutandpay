from django.contrib.staticfiles import finders
from django.templatetags.static import static
from . import content as c
from .biz import BIZ
from .models import RATES


def _biz_img(slug):
    for ext in ("jpg", "jpeg", "png", "webp"):
        path = f"core/img/biz/{slug}.{ext}"
        if finders.find(path):
            try:
                return static(path)
            except ValueError:  # file not collected yet
                return ""
    return ""


def site(request):
    return {**{k: getattr(c, k) for k in dir(c) if k.isupper()},
            "RATES_LIST": [dict(name=n, desc=d, rate=r) for _, n, d, r in RATES],
            "BIZ_LIST": [dict(name=n, desc=d, color=col, img=_biz_img(s)) for n, d, s, col in BIZ]}