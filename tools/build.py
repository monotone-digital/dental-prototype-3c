"""Builds index.html and treatments/<slug>/index.html from shared templates.

Run from anywhere:  python tools/build.py
"""
import hashlib
import json
from html import escape
from pathlib import Path
from urllib.parse import quote

from content import CASES, CLINIC, DOCTORS, SITE, TREATMENTS

ROOT = Path(__file__).resolve().parent.parent
C = CLINIC
BY_SLUG = {t["slug"]: t for t in TREATMENTS}


def ver(rel):
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()[:8]


CSS_V, JS_V = ver("assets/css/style.css"), ver("assets/js/main.js")


def wa(text=None):
    url = f"https://wa.me/{C['wa']}"
    return url + ("?text=" + quote(text) if text else "")


def stars(n=5):
    return "".join('<svg class="ico fill"><use href="#i-star"/></svg>' for _ in range(n))


# ---------------------------------------------------------------- shared parts

SPRITE = """<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M7 17L17 7M8 7h9v9"/></symbol>
  <symbol id="i-arrow-r" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
  <symbol id="i-chev-l" viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></symbol>
  <symbol id="i-chev-r" viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></symbol>
  <symbol id="i-phone" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></symbol>
  <symbol id="i-pin" viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></symbol>
  <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></symbol>
  <symbol id="i-star" viewBox="0 0 24 24"><path d="M12 2.5l2.94 5.96 6.56.95-4.75 4.63 1.12 6.54L12 17.5l-5.87 3.08 1.12-6.54L2.5 9.41l6.56-.95L12 2.5z"/></symbol>
  <symbol id="i-check" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></symbol>
  <symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></symbol>
  <symbol id="i-scan" viewBox="0 0 24 24"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2M7 12h10"/></symbol>
  <symbol id="i-heart" viewBox="0 0 24 24"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></symbol>
  <symbol id="i-users" viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></symbol>
  <symbol id="i-calendar" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></symbol>
  <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
  <symbol id="i-menu" viewBox="0 0 24 24"><path d="M4 8h16M4 16h11"/></symbol>
  <symbol id="i-close" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></symbol>
  <symbol id="i-spark" viewBox="0 0 24 24"><path d="M12 2c.75 6.1 3.9 9.25 10 10-6.1.75-9.25 3.9-10 10-.75-6.1-3.9-9.25-10-10 6.1-.75 9.25-3.9 10-10z"/></symbol>
  <symbol id="i-quote" viewBox="0 0 24 24"><path d="M10 7H6a3 3 0 0 0-3 3v4h5v5H3M21 7h-4a3 3 0 0 0-3 3v4h5v5h-5" fill="none"/></symbol>
  <symbol id="i-tooth" viewBox="0 0 24 24"><path d="M8.5 3C6 3 4.5 4.8 4.5 7.6c0 2.4 1 4 1.5 6.4.5 2.6 1 4.9 2.4 4.9 1.5 0 1.7-2.4 2.2-4.2.3-1.2.8-1.7 1.4-1.7s1.1.5 1.4 1.7c.5 1.8.7 4.2 2.2 4.2 1.4 0 1.9-2.3 2.4-4.9.5-2.4 1.5-4 1.5-6.4C19.5 4.8 18 3 15.5 3c-1.7 0-2.5.8-3.5.8S10.2 3 8.5 3Z"/></symbol>
  <symbol id="i-smile" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/></symbol>
  <symbol id="i-alert" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><path d="M12 9v4M12 17h.01"/></symbol>
  <symbol id="i-mail" viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 7l-10 6L2 7"/></symbol>
  <symbol id="i-fb" viewBox="0 0 24 24"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></symbol>
  <symbol id="i-ig" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37zM17.5 6.5h.01"/></symbol>
  <symbol id="i-wa" viewBox="0 0 24 24"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.39-1.47-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.21 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.17-1.41-.07-.12-.27-.2-.57-.35zM12.05 21.8h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.43 9.88-9.88 9.88zm8.41-18.3A11.82 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.68 1.45h.01c6.55 0 11.89-5.34 11.89-11.89 0-3.18-1.24-6.16-3.48-8.41z"/></symbol>
</svg>"""


def head(title, desc, path, og_img="/assets/img/hero-a.jpg", extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc)}">
  <meta name="theme-color" content="#0d646d">
  <link rel="canonical" href="{SITE}{path}">
  <link rel="icon" type="image/png" sizes="64x64" href="/assets/img/favicon-64.png">
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{escape(C['full'])}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(desc)}">
  <meta property="og:url" content="{SITE}{path}">
  <meta property="og:image" content="{SITE}{og_img}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&family=Inter+Tight:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css?v={CSS_V}">
  <script>document.documentElement.classList.add('js');</script>
{extra}</head>"""


def brand(close=False):
    attr = " data-close" if close else ""
    return f"""<a href="/" class="brand" aria-label="{escape(C['full'])}, home"{attr}>
      <img class="brand-mark" src="/assets/img/logo-mark.png" alt="" width="46" height="46">
      <span class="brand-text"><span class="brand-name">Braces &amp; Faces</span><span class="brand-sub">Multi Specialty Dental Clinic</span></span>
    </a>"""


def nav(active):
    dd = "\n".join(
        f'          <a href="/treatments/{t["slug"]}/"><img src="/assets/img/t-{img_key(t)}.jpg" alt="" loading="lazy"><span><strong>{t["card"]}</strong><small>{t["dd"]}</small></span></a>'
        for t in TREATMENTS
    )
    msub = "\n".join(f'      <a href="/treatments/{t["slug"]}/" data-close>{t["card"]}</a>' for t in TREATMENTS)

    def cls(key):
        return ' class="active"' if key == active else ""

    return f"""<!-- ============ NAV ============ -->
<div class="nav" id="nav">
  <div class="nav-inner">
    {brand()}
    <nav class="nav-links" aria-label="Primary">
      <a href="/#home"{cls("home")}>Home</a>
      <div class="nav-dd">
        <a href="/#treatments"{cls("treatments")}>Treatments <svg class="ico"><use href="#i-chev-r"/></svg></a>
        <div class="dd-panel">
{dd}
          <a class="dd-all" href="/#treatments">View all treatments</a>
        </div>
      </div>
      <a href="/#about">About</a>
      <a href="/#gallery">Results</a>
      <a href="/#dentists">Dentists</a>
      <a href="/#contact">Contact</a>
    </nav>
    <a class="btn btn-light nav-cta no-rot" href="tel:{C['tel']}">Book a Call <span class="ic"><svg class="ico"><use href="#i-phone"/></svg></span></a>
    <button class="burger" id="burger" aria-label="Open menu"><svg class="ico"><use href="#i-menu"/></svg></button>
  </div>
</div>

<!-- Mobile menu -->
<div class="mmenu" id="mmenu" aria-hidden="true">
  <div class="mmenu-top">
    {brand(close=True)}
    <button class="mmenu-close" data-close aria-label="Close menu"><svg class="ico"><use href="#i-close"/></svg></button>
  </div>
  <nav>
    <a href="/#home" data-close>Home</a>
    <a href="/#treatments" data-close>Treatments</a>
    <div class="m-sub">
{msub}
    </div>
    <a href="/#about" data-close>About</a>
    <a href="/#gallery" data-close>Results</a>
    <a href="/#dentists" data-close>Dentists</a>
    <a href="/#contact" data-close>Contact</a>
  </nav>
  <div class="mmenu-foot">
    <span>{C['addr_short']}, Faisalabad · {C['hours']}</span>
    <a class="btn btn-light no-rot" href="tel:{C['tel']}">Call {C['phone']} <span class="ic"><svg class="ico"><use href="#i-phone"/></svg></span></a>
  </div>
</div>"""


def img_key(t):
    return {"orthodontics": "ortho", "dental-implants": "implants", "root-canal-treatment": "rootcanal",
            "cosmetic-dentistry": "cosmetic", "checkup-and-cleaning": "checkup", "crowns-and-bridges": "crowns",
            "kids-dentistry": "kids", "emergency-dental-care": "emergency"}[t["slug"]]


def quick():
    return f"""<!-- ============ QUICK INFO ============ -->
<section class="quick" aria-label="Clinic contact details">
  <div class="container quick-grid">
    <a class="q-item" href="tel:{C['tel']}" data-reveal>
      <span class="q-ic"><svg class="ico"><use href="#i-phone"/></svg></span>
      <span><small>Call for an appointment</small><strong>{C['phone']}</strong></span>
    </a>
    <a class="q-item" href="{C['maps']}" target="_blank" rel="noopener" data-reveal style="--d:100ms">
      <span class="q-ic"><svg class="ico"><use href="#i-pin"/></svg></span>
      <span><small>Visit the clinic</small><strong>{C['addr_short']}</strong></span>
    </a>
    <div class="q-item" data-reveal style="--d:200ms">
      <span class="q-ic"><svg class="ico"><use href="#i-clock"/></svg></span>
      <span><small>Opening hours</small><strong>{C['hours']}</strong></span>
    </div>
    <a class="btn btn-primary" href="/#contact" data-reveal style="--d:300ms">Book Appointment <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></a>
  </div>
</section>"""


def t_card(t, i, delay):
    d = f' style="--d:{delay}ms"' if delay else ""
    return f"""      <article class="t-card" data-reveal="card"{d}>
        <figure class="t-media"><img src="/assets/img/t-{img_key(t)}.jpg" alt="{t['img_alt']}" loading="lazy"></figure>
        <a class="t-cover" href="/treatments/{t['slug']}/" aria-label="{t['card']}" tabindex="-1"></a>
        <span class="t-num">{i:02d}</span>
        <div class="t-body"><h3>{t['card']}</h3><p>{t['card_desc']}</p></div>
        <a class="t-go" href="/treatments/{t['slug']}/" aria-label="Learn about {t['card']}"><svg class="ico"><use href="#i-arrow"/></svg></a>
      </article>"""


def ba_cards(keys):
    out = []
    for n, k in enumerate(keys):
        title, kind = CASES[k]
        out.append(f"""      <figure class="ba-card" data-reveal style="--d:{(n % 3) * 100}ms">
        <div class="ba-img"><img src="/assets/img/{k}.jpg" alt="Before and after: {title.replace('&amp;', 'and').lower()}, real patient at Braces &amp; Faces" loading="lazy"><span class="ba-tag before">Before</span><span class="ba-tag after">After</span></div>
        <figcaption class="ba-cap"><strong>{title}</strong><span>{kind}</span></figcaption>
      </figure>""")
    return "\n".join(out)


def cta():
    return f"""<!-- ============ CTA ============ -->
<section class="cta">
  <div class="container">
    <div class="cta-inner" data-reveal="scale">
      <div class="cta-copy">
        <h2 class="h2" data-split>Ready to transform <em>your smile?</em></h2>
        <p data-reveal="blur" style="--d:300ms">Schedule your consultation today. Call or WhatsApp us and we'll find a time that suits you, Monday to Saturday, 5 PM to 9 PM.</p>
        <div class="cta-actions" data-reveal style="--d:450ms">
          <a class="btn btn-light no-rot" href="tel:{C['tel']}">Call {C['phone']} <span class="ic"><svg class="ico"><use href="#i-phone"/></svg></span></a>
          <a class="btn btn-glass" href="{wa()}" target="_blank" rel="noopener"><svg class="ico fill"><use href="#i-wa"/></svg> Chat on WhatsApp</a>
        </div>
      </div>
      <figure class="cta-img"><img src="/assets/img/family.jpg" alt="Smiling family with healthy teeth" loading="lazy"></figure>
    </div>
  </div>
</section>"""


def faq(items, aside_title, aside_lead, doc="maria"):
    acc = []
    for n, (q, a) in enumerate(items):
        open_ = n == 0
        d = f' style="--d:{n * 80}ms"' if n else ""
        acc.append(f"""      <div class="acc-item{' open' if open_ else ''}" data-reveal{d}>
        <button class="acc-q" aria-expanded="{'true' if open_ else 'false'}">{q} <span class="pm"><svg class="ico"><use href="#i-plus"/></svg></span></button>
        <div class="acc-a"><div><p>{a}</p></div></div>
      </div>""")
    acc_html = "\n".join(acc)
    return f"""<!-- ============ FAQ ============ -->
<section class="section" id="faq">
  <div class="container faq-grid">
    <div class="faq-aside">
      <h2 class="h2" data-split><span class="eyebrow">FAQ <b>/</b></span> {aside_title}</h2>
      <p class="lead" data-reveal="blur">{aside_lead}</p>
      <div class="help-card" data-reveal>
        <img src="/assets/img/{DOCTORS[doc]['img']}" alt="">
        <div><strong>Still have a question?</strong><span>Call or WhatsApp <a href="tel:{C['tel']}">{C['phone']}</a></span></div>
      </div>
    </div>
    <div class="acc">
{acc_html}
    </div>
  </div>
</section>"""


def footer():
    tlinks = "\n".join(f'          <li><a href="/treatments/{t["slug"]}/">{t["card"]}</a></li>' for t in TREATMENTS)
    return f"""<!-- ============ FOOTER ============ -->
<footer class="footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-about">
        <a href="/" class="footer-logo" aria-label="{escape(C['full'])}, home"><img src="/assets/img/logo-full.png" alt="Braces &amp; Faces Multi Specialty Dental Clinic" width="700" height="387" loading="lazy"></a>
        <p>Modern dental and orthodontic care with a friendly, professional approach, in Madina Town, Faisalabad.</p>
        <div class="socials">
          <a href="{C['facebook']}" target="_blank" rel="noopener" aria-label="Facebook"><svg class="ico"><use href="#i-fb"/></svg></a>
          <a href="{C['instagram']}" target="_blank" rel="noopener" aria-label="Instagram"><svg class="ico"><use href="#i-ig"/></svg></a>
          <a href="{wa()}" target="_blank" rel="noopener" aria-label="WhatsApp"><svg class="ico fill"><use href="#i-wa"/></svg></a>
        </div>
      </div>
      <div>
        <h4>Treatments</h4>
        <ul>
{tlinks}
        </ul>
      </div>
      <div>
        <h4>Clinic</h4>
        <ul>
          <li><a href="/#about">About us</a></li>
          <li><a href="/#gallery">Smile results</a></li>
          <li><a href="/#clinic">Clinic tour</a></li>
          <li><a href="/#dentists">Our dentists</a></li>
          <li><a href="/#reviews">Patient reviews</a></li>
          <li><a href="/#contact">Book appointment</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul class="contact-list">
          <li><svg class="ico"><use href="#i-phone"/></svg><a href="tel:{C['tel']}">{C['phone']}</a></li>
          <li><svg class="ico fill" style="color:#25d366"><use href="#i-wa"/></svg><a href="{wa()}" target="_blank" rel="noopener">WhatsApp us</a></li>
          <li><svg class="ico"><use href="#i-mail"/></svg><a href="mailto:{C['email']}">{C['email']}</a></li>
          <li><svg class="ico"><use href="#i-pin"/></svg><a href="{C['maps']}" target="_blank" rel="noopener">{C['addr_full']}</a></li>
          <li><svg class="ico"><use href="#i-clock"/></svg><span>{C['hours']}<br>Sunday closed</span></li>
        </ul>
      </div>
    </div>
  </div>
  <div class="footer-word" id="footerWord" aria-hidden="true">Braces &amp; Faces</div>
  <div class="container footer-bottom">
    <span>© <span id="year">2026</span> {C['full'].replace('&', '&amp;')}. All rights reserved.</span>
    <span>Madina Town, Faisalabad, Punjab, Pakistan</span>
  </div>
</footer>

<a class="wa-float" id="waFloat" href="{wa()}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">
  <span class="tip">Chat with us</span>
  <svg class="ico fill"><use href="#i-wa"/></svg>
</a>

<script src="/assets/js/main.js?v={JS_V}"></script>
</body>
</html>
"""


def schema():
    data = {
        "@context": "https://schema.org",
        "@type": "Dentist",
        "name": C["full"],
        "url": SITE + "/",
        "image": SITE + "/assets/img/clinic-reception.jpg",
        "logo": SITE + "/assets/img/icon-512.png",
        "telephone": C["tel"],
        "email": C["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Main Susan Road, opposite Bukhari CNG, near Bismillah Foods, X-Block, Madina Town",
            "addressLocality": "Faisalabad",
            "addressRegion": "Punjab",
            "addressCountry": "PK",
        },
        "geo": {"@type": "GeoCoordinates", "latitude": C["lat"], "longitude": C["lng"]},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "opens": "17:00", "closes": "21:00",
        }],
        "sameAs": [C["facebook"], C["instagram"]],
    }
    return f'  <script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>\n'


# ---------------------------------------------------------------- homepage

def build_home():
    chips = "\n".join(
        f'      <a class="chip{" is-on" if i == 0 else ""}" href="/treatments/{t["slug"]}/">{t["card"]}</a>'
        for i, t in enumerate(TREATMENTS[:5])
    )
    cards = "\n".join(t_card(t, i + 1, [0, 90, 180, 270][i % 4]) for i, t in enumerate(TREATMENTS))
    options = "\n".join(
        f'            <option data-slug="{t["slug"]}">{escape(t["option"])}</option>' for t in TREATMENTS
    )
    m, a = DOCTORS["maria"], DOCTORS["ansar"]

    def doc_card(d, key, delay):
        tags = "".join(f"<span>{x}</span>" for x in d["tags"])
        pts = "\n".join(f'          <li><svg class="ico"><use href="#i-check"/></svg><span>{p}</span></li>' for p in d["points"])
        dl = f' style="--d:{delay}ms"' if delay else ""
        return f"""      <article class="doc" data-reveal="card"{dl}>
        <div class="doc-photo"><img src="/assets/img/{d['img']}" alt="{d['name']}, {d['role'].replace('&amp;', 'and')} at Braces &amp; Faces" loading="lazy"></div>
        <div class="doc-info">
          <h3>{d['name']}</h3>
          <span class="role">{d['role']} · {d['quals']}</span>
          <a class="go" href="/#contact" aria-label="Book with {d['name']}"><svg class="ico"><use href="#i-arrow"/></svg></a>
          <div class="tags">{tags}</div>
        </div>
        <ul class="doc-points">
{pts}
        </ul>
      </article>"""

    reviews = [
        ("av-2.jpg", "Ali Mustafa", "Braces", "Getting braces at Braces &amp; Faces was the best decision I made. The process was well explained, and my results are beyond amazing. Thank you for the confident smile!"),
        ("av-3.jpg", "Fatima Rehman", "Kids Dentistry", "My daughter used to fear dental visits, but thanks to the gentle team at Braces &amp; Faces, she now feels safe and happy every time we visit."),
        ("av-4.jpg", "Omar Khan", "Teeth Whitening", "The teeth whitening service at Braces &amp; Faces exceeded my expectations. Friendly staff, modern tools and stunning results. Highly recommended!"),
    ]
    rev_html = "\n".join(
        f"""      <figure class="r-card" data-reveal style="--d:{(n + 1) * 100}ms">
        <div class="r-top"><svg class="ico quote-ic"><use href="#i-quote"/></svg><span class="stars">{stars()}</span></div>
        <blockquote>"{txt}"</blockquote>
        <figcaption class="r-who"><img src="/assets/img/{img}" alt=""><span><strong>{name}</strong><span>{tr}</span></span></figcaption>
      </figure>"""
        for n, (img, name, tr, txt) in enumerate(reviews)
    )

    faqs = [
        ("What age is right for braces?", "Braces work at any age, and many of our patients are adults. For children, an orthodontic check around age 7 is ideal, because some jaw problems are easiest to guide while a child is still growing."),
        ("How long does orthodontic treatment take?", "Most cases take 12 to 24 months, depending on how much your teeth need to move. Dr. Maria will give you a realistic timeline at your consultation."),
        ("Do you offer clear aligners?", "Yes. Alongside fixed braces we offer clear aligners for suitable cases. Your orthodontist will recommend the option that works best for your bite."),
        ("Is dental treatment painful?", "Most treatments are virtually painless. We use modern local anaesthesia and gentle techniques, and we always check in with you during the procedure."),
        ("What are your clinic timings?", f"We're open Monday to Saturday, 5 PM to 9 PM, and closed on Sunday. Call or WhatsApp {C['phone']} to book a time that suits you."),
    ]

    html = head(
        "Braces & Faces | Orthodontist & Dental Clinic in Faisalabad",
        "Braces & Faces Multi Specialty Dental Clinic, Madina Town, Faisalabad. Braces, aligners, implants, root canal, whitening and kids dentistry. Call 0316-4936792.",
        "/", extra=schema(),
    ) + f"""
<body data-page="home">

{SPRITE}

{nav("home")}

<!-- ============ HERO ============ -->
<header class="hero" id="home">
  <div class="hero-slides" id="heroSlides">
    <div class="slide is-active"><img src="/assets/img/hero-a.jpg" alt="Smiling young woman with braces at Braces &amp; Faces dental clinic" fetchpriority="high"></div>
    <div class="slide"><img src="/assets/img/hero-b.jpg" alt="Orthodontist adjusting braces on a teenage patient" loading="lazy"></div>
    <div class="slide"><img src="/assets/img/hero-c.jpg" alt="Young woman holding a clear aligner next to her straight smile" loading="lazy"></div>
  </div>
  <div class="hero-shade"></div>

  <div class="hero-content" id="heroContent">
    <span class="pill-badge" data-reveal="blur" style="--d:150ms"><i class="dot"></i> Orthodontist &amp; dental care in Faisalabad</span>
    <h1 data-split style="--d:250ms">Confident smiles <span class="soft">for</span> every face.</h1>
    <p class="hero-text" data-reveal="blur" style="--d:700ms">Expert dental and orthodontic care with compassion, modern technology and treatment planned around you, led by a consultant orthodontist in Madina Town.</p>
    <div class="hero-actions" data-reveal style="--d:850ms">
      <a class="btn btn-light" href="#contact">Book an Appointment <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></a>
      <a class="btn btn-glass" href="tel:{C['tel']}"><svg class="ico"><use href="#i-phone"/></svg> {C['phone']}</a>
    </div>
  </div>

  <div class="hero-bottom">
    <div class="chips" data-reveal style="--d:1000ms">
{chips}
    </div>
    <div class="hero-side" data-reveal="right" style="--d:1100ms">
      <div class="slider-ui" aria-label="Hero slideshow controls">
        <button id="prevSlide" aria-label="Previous slide"><svg class="ico"><use href="#i-chev-l"/></svg></button>
        <span id="slideNum">01</span>
        <span class="track"><i id="slideBar"></i></span>
        <span>03</span>
        <button id="nextSlide" aria-label="Next slide"><svg class="ico"><use href="#i-chev-r"/></svg></button>
      </div>
      <a class="doc-card" href="#dentists">
        <img src="/assets/img/doc-maria.jpg" alt="Dr. Maria Tanveer">
        <div class="info">
          <strong>Dr. Maria Tanveer</strong>
          <span>Consultant Orthodontist · FCPS</span>
          <div class="meta"><span><b>11 yrs</b> experience</span><span class="stars"><svg class="ico fill"><use href="#i-star"/></svg> <b>{C['rating']}</b></span></div>
        </div>
      </a>
    </div>
  </div>
</header>

{quick()}

<!-- ============ TREATMENTS ============ -->
<section class="section" id="treatments">
  <div class="container">
    <div class="sec-head">
      <h2 class="h2" data-split><span class="eyebrow">Our Treatments <b>/</b></span> Specialist care for <em>every smile</em></h2>
      <div class="sec-head-side">
        <p class="lead" data-reveal="blur">From routine check-ups to braces, implants and cosmetic treatments, every plan is personalised, explained clearly and carried out with modern equipment in a calm, welcoming clinic.</p>
        <div class="proof" data-reveal style="--d:150ms">
          <div class="avatars">
            <img src="/assets/img/av-1.jpg" alt="">
            <img src="/assets/img/av-2.jpg" alt="">
            <img src="/assets/img/av-3.jpg" alt="">
          </div>
          <div>
            <strong>{C['rating']} on Google</strong>
            <small><span class="stars">{stars()}</span> {C['reviews']} patient reviews</small>
          </div>
        </div>
      </div>
    </div>

    <div class="t-grid">
{cards}
    </div>

    <div class="t-foot" data-reveal>
      <div>
        <p>Not sure which treatment you need? Book a consultation. We'll examine your teeth, explain your options and give you a clear plan before anything begins.</p>
        <div class="t-more"><span>Oral surgery</span><span>Wisdom teeth</span><span>Fillings &amp; restorations</span><span>RVG digital X-rays</span></div>
      </div>
      <a class="btn btn-primary" href="#contact" data-treat="General Check-up / Consultation">Book a Consultation <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></a>
    </div>
  </div>
</section>

<!-- ============ ABOUT ============ -->
<section class="section about" id="about">
  <div class="container">
    <div class="about-grid">
      <div class="about-visual">
        <figure class="media about-img" data-reveal="img">
          <div class="px" data-parallax="0.09"><img src="/assets/img/about.jpg" alt="Dentist explaining a digital dental X-ray to a patient" loading="lazy"></div>
        </figure>
        <div class="float-card" data-reveal="left" style="--d:500ms">
          <span class="q-ic"><svg class="ico"><use href="#i-scan"/></svg></span>
          <span><strong>RVG digital X-rays</strong><span>Instant, high-resolution images with far less radiation</span></span>
        </div>
        <div class="float-chip" data-reveal="right" style="--d:650ms"><i class="dot"></i> Female orthodontist</div>
      </div>

      <div class="about-copy">
        <h2 class="h2" data-split><span class="eyebrow">About Braces &amp; Faces <b>/</b></span> Committed to your health, <em>one smile at a time</em></h2>
        <p class="lead" data-reveal="blur">Braces &amp; Faces is a multi specialty dental clinic in Madina Town, Faisalabad, led by government-authorised dental experts. We combine the latest techniques with a friendly, unhurried approach, so you always feel heard, comfortable and confident in your treatment.</p>
        <ul class="features">
          <li data-reveal style="--d:0ms"><span class="f-ic"><svg class="ico"><use href="#i-smile"/></svg></span><span><strong>Orthodontic specialist</strong><span>Braces and aligners planned by an FCPS orthodontist</span></span></li>
          <li data-reveal style="--d:100ms"><span class="f-ic"><svg class="ico"><use href="#i-scan"/></svg></span><span><strong>State-of-the-art equipment</strong><span>RVG imaging and modern treatment units</span></span></li>
          <li data-reveal style="--d:200ms"><span class="f-ic"><svg class="ico"><use href="#i-shield"/></svg></span><span><strong>Strict sterilisation</strong><span>Autoclave-sterilised instruments for every patient</span></span></li>
          <li data-reveal style="--d:300ms"><span class="f-ic"><svg class="ico"><use href="#i-users"/></svg></span><span><strong>Care for all ages</strong><span>From children's first visits to implants</span></span></li>
        </ul>
        <div class="about-actions" data-reveal>
          <a class="btn btn-primary" href="#contact">Book a Consultation <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></a>
          <a class="link-arrow" href="#dentists">Meet our dentists <svg class="ico"><use href="#i-arrow-r"/></svg></a>
        </div>
      </div>
    </div>

    <div class="stats">
      <div class="stat" data-reveal><div class="stat-num"><span data-count="4.9" data-decimals="1">0</span><span class="suf">★</span></div><div class="stat-label">Google rating</div></div>
      <div class="stat" data-reveal style="--d:100ms"><div class="stat-num"><span data-count="11">0</span><span class="suf">+</span></div><div class="stat-label">Years in dentistry</div></div>
      <div class="stat" data-reveal style="--d:200ms"><div class="stat-num"><span data-count="9">0</span><span class="suf">+</span></div><div class="stat-label">Years in orthodontics</div></div>
      <div class="stat" data-reveal style="--d:300ms"><div class="stat-num"><span data-count="12">0</span></div><div class="stat-label">Dental services</div></div>
    </div>
  </div>
</section>

<!-- ============ MARQUEE ============ -->
<div class="marquee" aria-hidden="true">
  <div class="marquee-track">
    <span class="marquee-item">Straight smiles <svg class="ico fill"><use href="#i-spark"/></svg></span>
    <span class="marquee-item outline">Healthy faces <svg class="ico fill"><use href="#i-spark"/></svg></span>
    <span class="marquee-item">Gentle hands <svg class="ico fill"><use href="#i-spark"/></svg></span>
    <span class="marquee-item outline">Modern care <svg class="ico fill"><use href="#i-spark"/></svg></span>
    <span class="marquee-item">Straight smiles <svg class="ico fill"><use href="#i-spark"/></svg></span>
    <span class="marquee-item outline">Healthy faces <svg class="ico fill"><use href="#i-spark"/></svg></span>
    <span class="marquee-item">Gentle hands <svg class="ico fill"><use href="#i-spark"/></svg></span>
    <span class="marquee-item outline">Modern care <svg class="ico fill"><use href="#i-spark"/></svg></span>
  </div>
</div>

<!-- ============ RESULTS ============ -->
<section class="section gallery-sec" id="gallery">
  <div class="container">
    <div class="sec-head">
      <h2 class="h2" data-split><span class="eyebrow">Real Results <b>/</b></span> Smile transformations <em>from our clinic</em></h2>
      <div class="sec-head-side">
        <p class="lead" data-reveal="blur">Every case below is a real Braces &amp; Faces patient. From crowded teeth to stained smiles, see the difference expert, personalised care can make.</p>
      </div>
    </div>
    <div class="ba-grid">
{ba_cards(["ba-1", "ba-2", "ba-3", "ba-4", "ba-5", "ba-6"])}
    </div>
    <p class="ba-note">Real patient photos from Braces &amp; Faces. Individual results vary from case to case.</p>
  </div>
</section>

<!-- ============ PROCESS ============ -->
<section class="section process" id="process">
  <div class="container">
    <div class="process-head">
      <div>
        <h2 class="h2" data-split><span class="eyebrow">How it works <b>/</b></span> Your visit, <em>made simple</em> from first call to final smile</h2>
        <p class="lead" data-reveal="blur">No confusing jargon and no surprises. We explain every step, share costs upfront and fit evening appointments around your work and school day.</p>
        <div class="process-actions" data-reveal>
          <a class="btn btn-light" href="#contact">Book your visit <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></a>
          <a class="btn btn-glass" href="{wa()}" target="_blank" rel="noopener"><svg class="ico fill"><use href="#i-wa"/></svg> WhatsApp us</a>
        </div>
      </div>
      <figure class="media process-img" data-reveal="img">
        <div class="px" data-parallax="0.08"><img src="/assets/img/clinic-reception.jpg" alt="Reception desk at Braces &amp; Faces Multi Specialty Dental Clinic" loading="lazy"></div>
      </figure>
    </div>

    <div class="steps" id="steps">
      <div class="steps-line"><i id="stepsFill"></i></div>
      <div class="step" data-reveal><div class="step-num">01</div><h3>Book a call</h3><p>Call or WhatsApp us on {C['phone']} and pick an evening time that suits you.</p></div>
      <div class="step" data-reveal style="--d:120ms"><div class="step-num">02</div><h3>Consultation</h3><p>A thorough check-up with RVG digital X-rays, so we understand exactly what your smile needs.</p></div>
      <div class="step" data-reveal style="--d:240ms"><div class="step-num">03</div><h3>Your plan</h3><p>We explain your options in plain language, with clear costs and timelines before we start.</p></div>
      <div class="step" data-reveal style="--d:360ms"><div class="step-num">04</div><h3>Care &amp; aftercare</h3><p>Gentle treatment, followed by reviews and reminders to keep your smile healthy for life.</p></div>
    </div>
  </div>
</section>

<!-- ============ CLINIC TOUR ============ -->
<section class="section" id="clinic">
  <div class="container">
    <div class="sec-head">
      <h2 class="h2" data-split><span class="eyebrow">Inside the clinic <b>/</b></span> A calm, modern space <em>designed for you</em></h2>
      <div class="sec-head-side">
        <p class="lead" data-reveal="blur">Take a look around our Madina Town clinic, from the welcoming reception to our treatment room, sterilisation and digital imaging equipment.</p>
      </div>
    </div>
    <div class="tour">
      <figure class="big" data-reveal="img"><img src="/assets/img/clinic-reception.jpg" alt="Braces &amp; Faces reception desk" loading="lazy"><figcaption>Reception</figcaption></figure>
      <figure class="tall" data-reveal="img" style="--d:100ms"><img src="/assets/img/clinic-room.jpg" alt="Modern dental treatment room with dental chair" loading="lazy"><figcaption>Treatment room</figcaption></figure>
      <figure class="tall" data-reveal="img" style="--d:200ms"><img src="/assets/img/clinic-lounge.jpg" alt="Patient waiting area with certificates on the wall" loading="lazy"><figcaption>Waiting lounge</figcaption></figure>
      <figure data-reveal="img"><img src="/assets/img/clinic-sterilisation.jpg" alt="Autoclave used to sterilise dental instruments" loading="lazy"><figcaption>Sterilisation</figcaption></figure>
      <figure data-reveal="img" style="--d:100ms"><img src="/assets/img/clinic-xray.jpg" alt="Digital dental X-ray unit" loading="lazy"><figcaption>Digital X-ray</figcaption></figure>
      <figure data-reveal="img" style="--d:200ms"><img src="/assets/img/clinic-certificates.jpg" alt="Dentists' qualifications and certificates" loading="lazy"><figcaption>Qualifications</figcaption></figure>
      <figure data-reveal="img" style="--d:300ms"><img src="/assets/img/clinic-waiting.jpg" alt="Comfortable seating in the clinic waiting area" loading="lazy"><figcaption>Comfortable seating</figcaption></figure>
    </div>
  </div>
</section>

<!-- ============ DENTISTS ============ -->
<section class="section" id="dentists">
  <div class="container">
    <div class="sec-head">
      <h2 class="h2" data-split><span class="eyebrow">Our Dentists <b>/</b></span> Meet the experts behind <em>your smile</em></h2>
      <div class="sec-head-side">
        <p class="lead" data-reveal="blur">Government-authorised experts in dentistry, both serving at Allied Hospital Faisalabad and committed to outstanding care with the latest techniques and the highest standards.</p>
      </div>
    </div>
    <div class="docs docs-2">
{doc_card(m, "maria", 0)}
{doc_card(a, "ansar", 120)}
    </div>
  </div>
</section>

<!-- ============ REVIEWS ============ -->
<section class="section reviews" id="reviews">
  <div class="container">
    <div class="sec-head">
      <h2 class="h2" data-split><span class="eyebrow">Patient Stories <b>/</b></span> Smiles that <em>speak for us</em></h2>
      <div class="sec-head-side">
        <p class="lead" data-reveal="blur">From life-changing braces results to gentle care for nervous children, here's what our patients say about their experience.</p>
      </div>
    </div>
    <div class="r-grid">
      <div class="r-summary" data-reveal="scale">
        <div class="big"><span data-count="4.9" data-decimals="1">0</span></div>
        <div class="stars">{stars()}</div>
        <p>Average Google rating from {C['reviews']} patients who trusted us with their smiles.</p>
        <div class="avatars">
          <img src="/assets/img/av-1.jpg" alt="">
          <img src="/assets/img/av-2.jpg" alt="">
          <img src="/assets/img/av-3.jpg" alt="">
          <span class="more">{C['reviews']}</span>
        </div>
      </div>
{rev_html}
    </div>
  </div>
</section>

{cta()}

{faq(faqs, "Questions? <em>We're here</em> to help", "Everything you might want to know before your first visit. Can't find your answer? Just give us a call.")}

<!-- ============ CONTACT ============ -->
<section class="section contact" id="contact">
  <div class="container contact-wrap">
    <div class="book" data-reveal>
      <h2 class="h2" data-split><span class="eyebrow">Book a Visit <b>/</b></span> Let's plan your <em>new smile</em></h2>
      <p class="lead">Share a few details and we'll confirm your appointment on WhatsApp, or simply call us on {C['phone']}.</p>
      <form class="form" id="bookForm" novalidate>
        <div class="field"><label for="f-name">Full name</label><input id="f-name" name="name" type="text" placeholder="e.g. Ali Raza" required autocomplete="name"></div>
        <div class="field"><label for="f-phone">Phone number</label><input id="f-phone" name="phone" type="tel" placeholder="03xx xxxxxxx" required autocomplete="tel"></div>
        <div class="field"><label for="f-treat">Treatment</label>
          <select id="f-treat" name="treatment">
            <option>General Check-up / Consultation</option>
{options}
            <option>Oral Surgery / Wisdom Teeth</option>
            <option>Fillings &amp; Restorations</option>
          </select>
        </div>
        <div class="field"><label for="f-date">Preferred date</label><input id="f-date" name="date" type="date"></div>
        <div class="field full"><label for="f-msg">Anything we should know? <span style="font-weight:400;color:var(--muted)">(optional)</span></label><textarea id="f-msg" name="message" placeholder="Tell us about any pain, concerns or preferred timings"></textarea></div>
        <div class="form-ok" id="formOk"><svg class="ico"><use href="#i-check"/></svg> Opening WhatsApp with your booking details…</div>
        <div class="form-foot">
          <small>We'll reply on WhatsApp to confirm your time. Your details stay private.</small>
          <button class="btn btn-primary" type="submit">Request Appointment <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></button>
        </div>
      </form>
    </div>

    <div class="visit">
      <div class="map" data-reveal="scale" style="--d:100ms">
        <iframe title="Braces &amp; Faces location map" loading="lazy" referrerpolicy="no-referrer-when-downgrade" src="{C['embed']}"></iframe>
      </div>
      <div class="visit-cards">
        <div class="v-card" data-reveal style="--d:150ms">
          <span class="q-ic"><svg class="ico" style="color:var(--blue-600)"><use href="#i-pin"/></svg></span>
          <small>Address</small>
          <p>{C['addr_full']}</p>
          <a class="link-arrow" href="{C['maps']}" target="_blank" rel="noopener">Get directions <svg class="ico"><use href="#i-arrow-r"/></svg></a>
        </div>
        <div class="v-card blue" data-reveal style="--d:250ms">
          <span class="q-ic"><svg class="ico"><use href="#i-phone"/></svg></span>
          <small>Call or WhatsApp</small>
          <a class="big-phone" href="tel:{C['tel']}">{C['phone']}</a>
          <div class="row"><span>Mon – Sat</span><span>5 PM – 9 PM</span></div>
          <div class="row"><span>Sunday</span><span>Closed</span></div>
        </div>
      </div>
    </div>
  </div>
</section>

{footer()}"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")


# ---------------------------------------------------------------- treatment pages

def build_treatment(idx, t):
    k = img_key(t)
    path = f"/treatments/{t['slug']}/"
    facts = "\n".join(
        f'      <div class="fact"><small>{lab}</small><strong>{val}</strong></div>' for lab, val in t["facts"]
    )
    ov = "\n".join(f'        <p class="lead" data-reveal="blur">{p}</p>' for p in t["ov"])
    checks = "\n".join(
        f'          <li><span class="ck"><svg class="ico"><use href="#i-check"/></svg></span>{c}</li>' for c in t["checks"]
    )
    signs = "\n".join(
        f"""      <div class="sign" data-reveal style="--d:{n * 100}ms">
        <span class="f-ic"><svg class="ico"><use href="#{ic}"/></svg></span>
        <h3>{h}</h3>
        <p>{p}</p>
      </div>"""
        for n, (ic, h, p) in enumerate(t["signs"])
    )
    steps = "\n".join(
        '      <div class="step" data-reveal' + (f' style="--d:{n * 120}ms"' if n else '') + f'><div class="step-num">{n + 1:02d}</div><h3>{h}</h3><p>{p}</p></div>'
        for n, (h, p) in enumerate(t["steps"])
    )

    results = ""
    if t["results"]:
        results = f"""
<!-- ============ RESULTS ============ -->
<section class="section gallery-sec" id="results">
  <div class="container">
    <div class="sec-head">
      <h2 class="h2" data-split><span class="eyebrow">Real Results <b>/</b></span> Real patients, <em>real smiles</em></h2>
      <div class="sec-head-side">
        <p class="lead" data-reveal="blur">These before and after photos are from patients treated at Braces &amp; Faces.</p>
        <a class="link-arrow" href="/#gallery" data-reveal>See more results <svg class="ico"><use href="#i-arrow-r"/></svg></a>
      </div>
    </div>
    <div class="ba-grid">
{ba_cards(t["results"])}
    </div>
    <p class="ba-note">Real patient photos from Braces &amp; Faces. Individual results vary from case to case.</p>
  </div>
</section>
"""

    docs = []
    for key in t["doctors"]:
        d = DOCTORS[key]
        pts = "\n".join(f'        <li><svg class="ico"><use href="#i-check"/></svg><span>{p}</span></li>' for p in d["points"])
        docs.append(f"""    <div class="lead-doc">
      <div class="doc-photo" data-reveal="card"><img src="/assets/img/{d['img']}" alt="{d['name']}" loading="lazy"></div>
      <div data-reveal>
        <span class="eyebrow">{d['role']} <b>/</b></span>
        <h3>{d['name']}</h3>
        <span class="doc-quals">{d['quals']}</span>
        <ul class="doc-points">
{pts}
        </ul>
        <a class="btn btn-primary" href="/?t={t['slug']}#contact">Book with {d['short']} <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></a>
      </div>
    </div>""")
    doc_title = "Your dentists" if len(docs) > 1 else ("Your orthodontist" if t["doctors"] == ["maria"] else "Your dentist")

    related = [TREATMENTS[(idx + j) % len(TREATMENTS)] for j in range(1, 5)]
    rel_cards = "\n".join(t_card(r, TREATMENTS.index(r) + 1, [0, 90, 180, 270][n]) for n, r in enumerate(related))

    crumbs_ld = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Treatments", "item": SITE + "/#treatments"},
            {"@type": "ListItem", "position": 3, "name": t["plain"], "item": SITE + path},
        ],
    })
    wa_text = f"Assalam-o-Alaikum! I'd like to ask about {t['plain']} at Braces & Faces."

    html = head(
        f"{t['plain']} in Faisalabad | Braces & Faces",
        t["meta"], path, og_img=f"/assets/img/w-{k}.jpg",
        extra=f'  <script type="application/ld+json">{crumbs_ld}</script>\n',
    ) + f"""
<body data-page="treatment">

{SPRITE}

{nav("treatments")}

<!-- ============ PAGE HERO ============ -->
<header class="hero page-hero" id="home">
  <div class="hero-slides" id="heroSlides">
    <div class="slide is-active"><img src="/assets/img/w-{k}.jpg" alt="{t['wide_alt']}" fetchpriority="high"></div>
  </div>
  <div class="hero-shade"></div>

  <div class="hero-content" id="heroContent">
    <nav class="pill-badge crumbs" aria-label="Breadcrumb" data-reveal="blur" style="--d:150ms"><i class="dot"></i> <a href="/">Home</a><span class="sep">/</span><a href="/#treatments">Treatments</a><span class="sep">/</span><span>{t['card']}</span></nav>
    <h1 data-split style="--d:250ms">{t['h1']}</h1>
    <p class="hero-text" data-reveal="blur" style="--d:700ms">{t['intro']}</p>
    <div class="hero-actions" data-reveal style="--d:850ms">
      <a class="btn btn-light" href="/?t={t['slug']}#contact">Book {t['card']} <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></a>
      <a class="btn btn-glass" href="{wa(wa_text)}" target="_blank" rel="noopener"><svg class="ico fill"><use href="#i-wa"/></svg> Ask on WhatsApp</a>
    </div>
  </div>

  <div class="hero-bottom">
    <div class="hero-facts" data-reveal style="--d:1000ms">
{facts}
    </div>
  </div>
</header>

{quick()}

<!-- ============ OVERVIEW ============ -->
<section class="section" id="overview">
  <div class="container ov-grid">
    <figure class="media ov-img" data-reveal="img">
      <div class="px" data-parallax="0.08"><img src="/assets/img/t-{k}.jpg" alt="{t['img_alt']}" loading="lazy"></div>
    </figure>
    <div class="ov-copy">
      <h2 class="h2" data-split><span class="eyebrow">{t['card']} <b>/</b></span> {t['ov_title']}</h2>
{ov}
      <ul class="checks" data-reveal>
{checks}
      </ul>
      <div class="about-actions" data-reveal>
        <a class="btn btn-primary" href="/?t={t['slug']}#contact">Book a Consultation <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></a>
        <a class="link-arrow" href="tel:{C['tel']}">Call {C['phone']} <svg class="ico"><use href="#i-arrow-r"/></svg></a>
      </div>
    </div>
  </div>
</section>

<!-- ============ IS IT FOR YOU ============ -->
<section class="section signs" id="signs">
  <div class="container">
    <div class="sec-head">
      <h2 class="h2" data-split><span class="eyebrow">Is it right for you? <b>/</b></span> Signs you may <em>need this</em></h2>
      <div class="sec-head-side">
        <p class="lead" data-reveal="blur">Not sure? Book a consultation and we'll examine your teeth and explain every option honestly, with no pressure to go ahead.</p>
      </div>
    </div>
    <div class="sign-grid">
{signs}
    </div>
  </div>
</section>

<!-- ============ PROCESS ============ -->
<section class="section process" id="process" style="margin-top: clamp(20px, 3vw, 32px);">
  <div class="container">
    <div class="process-head">
      <div>
        <h2 class="h2" data-split><span class="eyebrow">Step by step <b>/</b></span> What to expect <em>at every visit</em></h2>
        <p class="lead" data-reveal="blur">We explain each stage before we begin, share costs upfront and make sure you're comfortable throughout.</p>
        <div class="process-actions" data-reveal>
          <a class="btn btn-light" href="/?t={t['slug']}#contact">Book your visit <span class="ic"><svg class="ico"><use href="#i-arrow"/></svg></span></a>
          <a class="btn btn-glass" href="{wa(wa_text)}" target="_blank" rel="noopener"><svg class="ico fill"><use href="#i-wa"/></svg> WhatsApp us</a>
        </div>
      </div>
      <figure class="media process-img" data-reveal="img">
        <div class="px" data-parallax="0.08"><img src="/assets/img/clinic-room.jpg" alt="Treatment room at Braces &amp; Faces dental clinic" loading="lazy"></div>
      </figure>
    </div>

    <div class="steps" id="steps">
      <div class="steps-line"><i id="stepsFill"></i></div>
{steps}
    </div>
  </div>
</section>
{results}
<!-- ============ DENTIST ============ -->
<section class="section" id="dentist">
  <div class="container">
    <div class="sec-head">
      <h2 class="h2" data-split><span class="eyebrow">{doc_title} <b>/</b></span> Experienced, <em>caring hands</em></h2>
      <div class="sec-head-side">
        <p class="lead" data-reveal="blur">Your treatment is planned and carried out by qualified, government-authorised dentists who also serve at Allied Hospital Faisalabad.</p>
      </div>
    </div>
{chr(10).join(docs)}
  </div>
</section>

{faq(t["faqs"], f"{t['card']}, <em>answered</em>", "Common questions about this treatment. If yours isn't here, call or WhatsApp us and we'll be happy to help.", doc=t["doctors"][0])}

<!-- ============ RELATED ============ -->
<section class="section related" style="padding-top: 0;">
  <div class="container">
    <div class="sec-head">
      <h2 class="h2" data-split><span class="eyebrow">More treatments <b>/</b></span> Explore <em>other services</em></h2>
      <div class="sec-head-side">
        <a class="link-arrow" href="/#treatments" data-reveal>View all treatments <svg class="ico"><use href="#i-arrow-r"/></svg></a>
      </div>
    </div>
    <div class="t-grid">
{rel_cards}
    </div>
  </div>
</section>

{cta()}

{footer()}"""
    out = ROOT / "treatments" / t["slug"] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def build_extras():
    urls = ["/"] + [f"/treatments/{t['slug']}/" for t in TREATMENTS]
    sm = "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n',
        encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


if __name__ == "__main__":
    build_home()
    for i, t in enumerate(TREATMENTS):
        build_treatment(i, t)
    build_extras()
    print("built", 1 + len(TREATMENTS), "pages")
