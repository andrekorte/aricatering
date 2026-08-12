#!/usr/bin/env python3
"""Scaffold the Ari Thai Catering static site.

Writes plain HTML to the repo root. The generated HTML is committed and is
the thing that gets deployed — this script exists so the shared header,
footer and menu grid stay identical across pages while the site is being
built out. Re-run it after editing the content blocks below:

    python3 tools/build.py

Business name / domain live in site.config.json; use tools/rebrand.py to
change them across the whole site in one go.
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "site.config.json")))

NAME = CFG["business_name"]
SHORT = CFG["short_name"]
DOMAIN = CFG["domain"]
PHONE = CFG["phone"]
PHONE_HREF = CFG["phone_href"]
EMAIL = CFG["email"]
ADDRESS = CFG["address"]
FORM_ENDPOINT = CFG["form_endpoint"]

YEAR = CFG["copyright_year"]

# --------------------------------------------------------------------------
# Inline icons (no icon font, no external requests)
# --------------------------------------------------------------------------

ICON = {
    "check": '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M4 10.5l4 4 8-9" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "phone": '<svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M4.6 2.2a1.5 1.5 0 0 1 2 .5l1.3 2.1a1.5 1.5 0 0 1-.2 1.8l-.9.9a10.6 10.6 0 0 0 4.7 4.7l.9-.9a1.5 1.5 0 0 1 1.8-.2l2.1 1.3a1.5 1.5 0 0 1 .5 2l-.7 1.4a2 2 0 0 1-2.2 1A15.6 15.6 0 0 1 2.4 5.5a2 2 0 0 1 1-2.2l1.2-.6Z"/></svg>',
    "mail": '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden="true"><rect x="2" y="4" width="16" height="12" rx="2" stroke="currentColor" stroke-width="1.7"/><path d="M3 5.5l7 5 7-5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    "pin": '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M10 18s6-5.1 6-9.4A6 6 0 0 0 4 8.6C4 12.9 10 18 10 18Z" stroke="currentColor" stroke-width="1.7"/><circle cx="10" cy="8.5" r="2.2" stroke="currentColor" stroke-width="1.7"/></svg>',
    "clock": '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="7.5" stroke="currentColor" stroke-width="1.7"/><path d="M10 5.8V10l2.8 2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    "leaf": '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M16.5 3.5C9 3 4 6 4 11.5c0 2 .8 3.4.8 3.4S7 10 12 8c0 0-4.2 2.6-6 8.5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "doc": '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M5 2.5h6l4 4v11H5v-15Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M11 2.5v4h4M7.5 11h5M7.5 13.8h5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
    "truck": '<svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M1.8 5h9v8h-9V5Zm9 3h3.2l2.2 2.4V13h-5.4" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><circle cx="5.4" cy="15" r="1.6" stroke="currentColor" stroke-width="1.7"/><circle cx="13.6" cy="15" r="1.6" stroke="currentColor" stroke-width="1.7"/></svg>',
    "chef": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 20h12M6 16.5h12v2H6v-2Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M6.5 16.5c-2 0-3.5-1.6-3.5-3.6 0-1.7 1.2-3.2 2.9-3.5A4 4 0 0 1 12 6a4 4 0 0 1 6.1 3.4c1.7.3 2.9 1.8 2.9 3.5 0 2-1.5 3.6-3.5 3.6" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
    "users": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="9" cy="8" r="3.2" stroke="currentColor" stroke-width="1.8"/><path d="M3 19c0-3 2.7-5 6-5s6 2 6 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M16 5.5a3.2 3.2 0 0 1 0 6M17 14.5c2.4.5 4 2.2 4 4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
    "flame": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 2.5s5.5 4.2 5.5 9.2a5.5 5.5 0 0 1-11 0c0-2 1-3.6 1-3.6s.6 1.6 1.9 2c0-3.4 2.6-5.6 2.6-7.6Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>',
    "calendar": '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2.5" stroke="currentColor" stroke-width="1.8"/><path d="M3 10h18M8 3v4M16 3v4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
}

TICK = '<li>' + ICON["check"] + ' <span>%s</span></li>'


def ticks(items, cls="tick-list"):
    return '<ul class="%s">%s</ul>' % (cls, "".join(TICK % i for i in items))


# --------------------------------------------------------------------------
# Shared chrome
# --------------------------------------------------------------------------

NAV_ITEMS = [
    ("/", "Home"),
    ("/packages/", "Packages &amp; pricing"),
    ("/menu/", "Catering menu"),
    ("/about/", "About Ari"),
]


def header(active):
    links = []
    for href, label in NAV_ITEMS:
        cur = ' aria-current="page"' if href == active else ""
        links.append('<a href="%s"%s>%s</a>' % (href, cur, label))
    return """<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="/">
      <img src="/assets/img/brand/ari-logo.png" alt="" width="46" height="46">
      <span class="brand__text">
        <span class="brand__name">{SHORT}</span>
        <span class="brand__tag">Catering &middot; Brisbane</span>
      </span>
    </a>
    <nav class="nav" id="primary-nav" aria-label="Main">
      {LINKS}
      <a class="btn btn--primary btn--sm" href="/enquiry/">Get a quote</a>
    </nav>
    <div class="header-cta">
      <a class="header-phone" href="tel:{PHONE_HREF}">{PHONE_ICON}<span>{PHONE}</span></a>
      <a class="btn btn--primary btn--sm" href="/enquiry/">Get a quote</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-nav" aria-label="Menu">
        <svg class="icon-open" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        <svg class="icon-close" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      </button>
    </div>
  </div>
</header>""".replace("{LINKS}", "\n      ".join(links)) \
             .replace("{SHORT}", SHORT) \
             .replace("{PHONE_ICON}", ICON["phone"]) \
             .replace("{PHONE_HREF}", PHONE_HREF) \
             .replace("{PHONE}", PHONE)


FOOTER = """<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="/">
          <img src="/assets/img/brand/ari-logo.png" alt="" width="46" height="46">
          <span class="brand__text">
            <span class="brand__name">{SHORT}</span>
            <span class="brand__tag">Catering &middot; Brisbane</span>
          </span>
        </a>
        <p>Real Thai street food for Brisbane offices &mdash; cooked fresh, delivered hot, ready to serve.</p>
      </div>
      <div>
        <h3>Catering</h3>
        <ul class="footer-links">
          <li><a href="/packages/">Packages &amp; pricing</a></li>
          <li><a href="/menu/">Catering menu</a></li>
          <li><a href="/enquiry/">Get a quote</a></li>
          <li><a href="/about/">About Ari</a></li>
        </ul>
      </div>
      <div>
        <h3>Talk to us</h3>
        <ul class="footer-links">
          <li><a href="tel:{PHONE_HREF}">{PHONE}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>{ADDRESS}</li>
          <li>Enquiries answered within one business day</li>
        </ul>
      </div>
      <div>
        <h3>Our restaurant</h3>
        <p>Ari &ndash; Thai Street Food is open seven days in Brisbane City.</p>
        <ul class="footer-links">
          <li><a href="https://ari-thaistreetfood.com/">ari-thaistreetfood.com</a></li>
          <li>Mon&ndash;Fri 9.00am&ndash;8.00pm</li>
          <li>Sat&ndash;Sun 10.00am&ndash;6.00pm</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p class="mb-0">&copy; {YEAR} {NAME}. All rights reserved.</p>
      <ul>
        <li><a href="/privacy-policy/">Privacy policy</a></li>
        <li><a href="/terms-conditions/">Terms &amp; conditions</a></li>
      </ul>
    </div>
  </div>
</footer>

<div class="mobile-cta">
  <a class="btn btn--ghost" href="tel:{PHONE_HREF}">Call us</a>
  <a class="btn btn--primary" href="/enquiry/">Get a quote</a>
</div>

<script src="/assets/js/site.js" defer></script>""" \
    .replace("{SHORT}", SHORT).replace("{NAME}", NAME).replace("{YEAR}", str(YEAR)) \
    .replace("{PHONE_HREF}", PHONE_HREF).replace("{PHONE}", PHONE) \
    .replace("{EMAIL}", EMAIL).replace("{ADDRESS}", ADDRESS)


SCHEMA = json.dumps({
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": NAME,
    "description": "Thai street food catering for offices, meetings and staff events across Brisbane.",
    "url": "https://%s/" % DOMAIN,
    "telephone": PHONE,
    "email": EMAIL,
    "image": "https://%s/assets/img/brand/pad-kra-pow-hero.jpg" % DOMAIN,
    "servesCuisine": "Thai",
    "priceRange": "$$",
    "areaServed": {"@type": "City", "name": "Brisbane"},
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "6/158 Adelaide St",
        "addressLocality": "Brisbane City",
        "addressRegion": "QLD",
        "postalCode": "4000",
        "addressCountry": "AU",
    },
}, indent=2)


def page(path, title, description, body, active, og_image="/assets/img/brand/pad-kra-pow-hero.jpg", schema=False):
    canonical = "https://%s%s" % (DOMAIN, path if path.endswith("/") else path)
    head_schema = '\n<script type="application/ld+json">\n%s\n</script>' % SCHEMA if schema else ""
    html = """<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="{DESC}">
<link rel="canonical" href="{CANON}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{CANON}">
<meta property="og:image" content="https://{DOMAIN}{OG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#05070b">
<link rel="icon" href="/assets/img/brand/ari-logo.png">
<link rel="apple-touch-icon" href="/assets/img/brand/ari-logo.png">
<link rel="preload" href="/assets/fonts/roboto-kfo7cnqeu92fr1me7ksn66agldtyluama3kubgee.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/fonts.css">
<link rel="stylesheet" href="/assets/css/site.css">{SCHEMA}
</head>
<body>
{HEADER}
<main id="main">
{BODY}
</main>
{FOOTER}
</body>
</html>
"""
    return (html
            .replace("{TITLE}", title)
            .replace("{DESC}", description)
            .replace("{CANON}", canonical)
            .replace("{DOMAIN}", DOMAIN)
            .replace("{OG}", og_image)
            .replace("{NAME}", NAME)
            .replace("{SCHEMA}", head_schema)
            .replace("{HEADER}", header(active))
            .replace("{BODY}", body)
            .replace("{FOOTER}", FOOTER))


def write(path, html):
    full = os.path.join(ROOT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("  %-38s %6.1f KB" % (path, len(html) / 1024))


# --------------------------------------------------------------------------
# Shared content blocks
# --------------------------------------------------------------------------

REVIEWS = [
    ("Amazing service, friendly staff and food with quality and good quantity. Don&rsquo;t miss this if you&rsquo;re visiting Brisbane.", "Tamima Shiptu"),
    ("Absolutely amazing dining experience. The staff were so lovely and friendly. They couldn&rsquo;t do enough to make our experience more perfect.", "Imme Visser"),
    ("Delicious traditional Thai food (one of our favourite cuisines) and friendly hospitality; it makes all the difference when the service is welcoming.", "Andrew Mulholland"),
    ("Absolutely the best Thai food we&rsquo;ve had, so authentic. The staff were fantastic, so friendly and engaging. Definitely recommend and will be back.", "Julie Smith"),
]


def reviews_block():
    cards = []
    for quote, who in REVIEWS:
        cards.append("""      <figure class="review">
        <div class="review__stars" aria-label="5 out of 5 stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <blockquote>&ldquo;%s&rdquo;</blockquote>
        <figcaption class="review__who">%s<span class="review__src"><br>Google review &middot; Ari &ndash; Thai Street Food</span></figcaption>
      </figure>""" % (quote, who))
    return """<section class="section section--ink">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">What people say</span>
      <h2>The same kitchen Brisbane already rates</h2>
      <p class="lede">Our catering comes out of the Ari &ndash; Thai Street Food kitchen on Adelaide St. These are reviews from our restaurant guests.</p>
    </div>
    <div class="reviews">
%s
    </div>
  </div>
</section>""" % "\n".join(cards)


CTA_BAND = """<section class="section cta-band">
  <div class="container">
    <span class="eyebrow">Feed the team</span>
    <h2>Tell us the date and the headcount</h2>
    <p class="lede">Send us your brief and we&rsquo;ll come back with a menu and a fixed, all-inclusive quote within one business day. No obligation.</p>
    <div class="btn-row">
      <a class="btn btn--primary" href="/enquiry/">Get a quote</a>
      <a class="btn btn--ghost" href="tel:{PHONE_HREF}">Call {PHONE}</a>
    </div>
    <p class="cta-band__note">Minimum 10 guests &middot; 24 hours&rsquo; notice &middot; Delivering across Brisbane CBD and inner suburbs</p>
  </div>
</section>""".replace("{PHONE_HREF}", PHONE_HREF).replace("{PHONE}", PHONE)


PACKAGES = [
    {
        "name": "Street Lunch",
        "for": "Everyday team lunches and working meetings",
        "price": "24",
        "min": "Minimum 10 guests &middot; drop-off",
        "featured": False,
        "includes": [
            "<strong>2 mains</strong> from the catering menu",
            "Steamed jasmine rice",
            "Fresh Thai side salad",
            "Vegan and gluten-free versions at no extra cost",
            "Serving tongs, plates, napkins and cutlery",
            "Delivered hot and ready to serve",
        ],
    },
    {
        "name": "Ari Banquet",
        "for": "Client lunches, board meetings and team celebrations",
        "price": "34",
        "min": "Minimum 15 guests &middot; drop-off with setup",
        "featured": True,
        "includes": [
            "<strong>3 mains</strong> from the catering menu",
            "<strong>Entr&eacute;e platter</strong> &mdash; Moo Ping pork skewers, spring rolls and Thai fish cakes",
            "Chef&rsquo;s curry of the day",
            "Steamed jasmine rice and fresh Thai side salad",
            "Mango sticky rice to finish",
            "Chafing dishes to keep everything hot",
            "We set the buffet up on arrival",
        ],
    },
    {
        "name": "Street Feast",
        "for": "Conferences, launches and end-of-year events",
        "price": "46",
        "min": "Minimum 20 guests &middot; staffed service",
        "featured": False,
        "includes": [
            "<strong>4 mains</strong> plus a signature noodle dish",
            "<strong>2 entr&eacute;e platters</strong> and a Thai snack grazing board",
            "Chef&rsquo;s curry of the day",
            "Steamed jasmine rice and fresh Thai side salad",
            "Mango sticky rice to finish",
            "Ari&rsquo;s Thai iced tea station &mdash; Thai milk tea, lemon tea and O-Liang",
            "Full setup, staffed service and pack-down",
        ],
    },
]


def package_cards(cta="/enquiry/", cta_label="Get a quote"):
    out = []
    for p in PACKAGES:
        flag = '<span class="pkg__flag">Most popular</span>' if p["featured"] else ""
        cls = "pkg pkg--featured" if p["featured"] else "pkg"
        btn = "btn--dark" if p["featured"] else "btn--ghost on-light"
        items = "".join(
            '<li>%s <span>%s</span></li>' % (ICON["check"], i) for i in p["includes"]
        )
        out.append("""      <article class="{CLS}">
        {FLAG}
        <h3 class="pkg__name">{PNAME}</h3>
        <p class="pkg__for">{PFOR}</p>
        <p class="pkg__price"><span class="pkg__from">From</span><span class="pkg__amount">${PRICE}</span><span class="pkg__unit">per person</span></p>
        <p class="pkg__min">{PMIN}</p>
        <ul class="pkg__list">{ITEMS}</ul>
        <a class="btn {BTN} btn--block" href="{CTA}">{CTA_LABEL}</a>
      </article>""".replace("{CLS}", cls).replace("{FLAG}", flag)
                   .replace("{PNAME}", p["name"]).replace("{PFOR}", p["for"])
                   .replace("{PRICE}", p["price"]).replace("{PMIN}", p["min"])
                   .replace("{ITEMS}", items).replace("{BTN}", btn)
                   .replace("{CTA}", cta).replace("{CTA_LABEL}", cta_label))
    return '<div class="pkg-grid">\n%s\n    </div>' % "\n".join(out)


# --------------------------------------------------------------------------
# Catering menu, built from the restaurant's menu data
# --------------------------------------------------------------------------

MENU = json.load(open(os.path.join(ROOT, "assets", "menu-data.json")))
BY_SLUG = {c["slug"]: c for c in MENU["categories"]}

GALLERY = json.load(open(os.path.join(ROOT, "assets", "gallery-data.json")))


def gallery_section():
    tiles = "\n".join(
        '      <li class="gallery__item"><img src="/assets/img/gallery/%s" alt="Ari rice bowl, cooked to order and ready for delivery" '
        'width="%d" height="%d" loading="lazy" decoding="async"></li>'
        % (g["file"], g["w"], g["h"]) for g in GALLERY)
    return """<section class="section section--cream">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Signature rice bowls</span>
      <h2>This is what shows up at your desk</h2>
      <p class="lede" style="margin-inline:auto">Cooked to order in our Adelaide St kitchen, not held under a heat lamp. A few of the bowls that go out the door every day.</p>
    </div>
    <ul class="gallery">
%s
    </ul>
  </div>
</section>""" % tiles

# Which restaurant categories become catering menu sections, and how they are
# framed for a corporate buyer. Retail prices are deliberately not shown:
# catering is sold per person, by package.
MENU_SECTIONS = [
    ("mains", "Mains &amp; stir-fries", ["ala-carte"],
     "Wok-tossed to order. Choose your mains by package &mdash; two for Street Lunch, three for Banquet, four for Street Feast.", None),
    ("entrees", "Entr&eacute;es &amp; skewers", ["entree"],
     "Served on platters for the table. Included in the Banquet and Street Feast packages, or add to any order.",
     ["Moo Ping &ndash; Pork Skewers", "Chicken Dim Sim (1 pc)", "Sour Pork (1 pc)", "Chicken Wing Zap"]),
    ("vegan", "Vegan mains", ["vegan"],
     "Every package can be built fully vegan &mdash; no surcharge, no separate order.", None),
    ("gluten-free", "Gluten-free mains", ["gluten-free"],
     "Prepared with gluten-free sauces and labelled separately on delivery.", None),
    ("snacks", "Thai snacks &amp; sweets", ["thai-snacks", "dessert"],
     "Grazing boards for all-day events and afternoon breaks, plus mango sticky rice to finish. Available as add-ons.",
     ["Durian"]),
    ("drinks", "Ari&rsquo;s Thai drinks", ["aris-drinks"],
     "Our iced tea station, brewed the Bangkok way. Add to any package.", None),
]

SKIP_ITEMS = {"Cup of Ice", "Jasmine Rice", "Sticky Rice"}

VEG_TAG = {"vegan": ("V", "tag--v"), "gluten-free": ("GF", "tag--gf")}
HOT = re.compile(r"spicy|chil[li]?|kra pow|ka praw|tom yum|kee mao|zap|jaew", re.I)


def dish_tile(item, slug):
    tags = []
    if slug in VEG_TAG:
        label, cls = VEG_TAG[slug]
        tags.append('<span class="tag %s">%s</span>' % (cls, label))
    if HOT.search(item["name"]):
        tags.append('<span class="tag tag--hot">Spicy</span>')

    name = item["name"]
    # Package menus don't need the (Vegan)/(GF) suffix — the section says it.
    name = re.sub(r"\s*\((?:Vegan|GF)\)$", "", name)

    if item.get("id"):
        media = ('<div class="dish__img"><img src="/assets/img/dishes/%s.jpg" alt="%s" '
                 'width="574" height="574" loading="lazy" decoding="async"></div>'
                 % (item["id"], name.replace('"', "&quot;")))
    else:
        media = ('<div class="dish__img" style="display:grid;place-items:center;'
                 'background:#05070b;color:#f2c519;font-family:var(--font-head);'
                 'font-weight:700;font-size:1.6rem" aria-hidden="true">ARI</div>')

    return """        <li class="dish">
          %s
          <div class="dish__body">
            <span class="dish__name">%s</span>
            <span class="dish__tags">%s</span>
          </div>
        </li>""" % (media, name, "".join(tags))


def menu_sections():
    nav, blocks = [], []
    for anchor, title, slugs, note, exclude in MENU_SECTIONS:
        missing = [s for s in slugs if s not in BY_SLUG]
        if missing:
            raise KeyError("unknown menu-data slug(s) %s in section %r - known: %s"
                           % (missing, anchor, sorted(BY_SLUG)))
        items = []
        for slug in slugs:
            items += [i for i in BY_SLUG[slug]["items"] if i["name"] not in SKIP_ITEMS]
        if exclude:
            items = [i for i in items if i["name"] not in exclude]
        nav.append('<a href="#%s">%s</a>' % (anchor, title))
        tiles = "\n".join(dish_tile(i, slugs[0]) for i in items)
        blocks.append("""    <section class="menu-cat" id="%s">
      <div class="menu-cat__head">
        <h2>%s</h2>
        <p class="menu-cat__note">%d dishes</p>
      </div>
      <p class="lede" style="margin-bottom:1.5rem">%s</p>
      <ul class="dishes">
%s
      </ul>
    </section>""" % (anchor, title, len(items), note, tiles))
    return '<nav class="menu-nav" aria-label="Menu sections">%s</nav>' % "".join(nav), "\n".join(blocks)


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

def build_home():
    usecases = [
        ("Office &amp; working lunches", "Hot mains, rice and salad delivered to the floor. Ready to serve the minute it lands.", "/assets/img/dishes/A2SZJ3QZ7KC3M.jpg"),
        ("Board &amp; client meetings", "Something better than sandwiches when it matters. Plated up or served buffet-style.", "/assets/img/brand/menu-hero.jpg"),
        ("Staff celebrations", "End-of-year, birthdays, farewells. A full Thai banquet that gets people out of their chairs.", "/assets/img/brand/entree-tile.jpg"),
        ("Conferences &amp; all-day events", "Rolling catering across a full day, with grazing boards and Thai iced tea between sessions.", "/assets/img/brand/stir-fry-tile.jpg"),
    ]
    cards = "\n".join(
        """      <a class="usecase" href="/packages/" style="background-image:url('%s')">
        <div class="usecase__body">
          <h3>%s</h3>
          <p>%s</p>
        </div>
      </a>""" % (img, title, copy) for title, copy, img in usecases)

    body = """<section class="hero" style="background-image:url('/assets/img/brand/pad-kra-pow-hero.jpg')">
  <div class="container">
    <div class="hero__inner">
      <span class="eyebrow">Corporate &amp; office catering &middot; Brisbane</span>
      <h1>Real Thai street food, <span class="accent">delivered to your office.</span></h1>
      <p class="hero__lede">Ari brings Brisbane&rsquo;s favourite Thai street food to your desks, boardrooms and staff events &mdash; cooked fresh, delivered hot, ready to serve. Packages from $24 per person.</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="/enquiry/">Get a quote</a>
        <a class="btn btn--ghost" href="/packages/">See packages &amp; pricing</a>
      </div>
      <ul class="hero__points">
        <li>{CHECK} Delivered hot across Brisbane CBD and inner suburbs</li>
        <li>{CHECK} Vegan and gluten-free options in every package, no surcharge</li>
        <li>{CHECK} Menu and fixed quote back within one business day</li>
      </ul>
    </div>
  </div>
</section>

<section class="trust">
  <div class="container trust__inner">
    <div class="trust__item">{CHEF} Cooked fresh in our Adelaide St kitchen</div>
    <div class="trust__item">{LEAF} Vegan &amp; gluten-free as standard</div>
    <div class="trust__item">{CLOCK} 24 hours&rsquo; notice, minimum 10 guests</div>
    <div class="trust__item">{DOC} Tax invoice and PO friendly</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">What we cater</span>
      <h2>Built for the way offices actually eat</h2>
      <p class="lede">Everything is designed to travel well and hold heat &mdash; so what arrives at 12.15 still tastes like it came straight off the wok.</p>
    </div>
    <div class="grid grid--4">
{CARDS}
    </div>
  </div>
</section>

<section class="section section--cream">
  <div class="container">
    <div class="section-head section-head--center">
      <span class="eyebrow">Packages &amp; pricing</span>
      <h2>Straightforward pricing, per person</h2>
      <p class="lede">One price per head covers the food, the serving gear and delivery into Brisbane CBD. No hidden extras on the invoice.</p>
    </div>
    {PACKAGES}
    <p class="text-center" style="margin-top:2rem">
      <a class="btn btn--dark" href="/packages/">See what&rsquo;s in each package</a>
    </p>
  </div>
</section>

<section class="section section--ink">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">How it works</span>
      <h2>Three steps, one business day</h2>
    </div>
    <ol class="steps">
      <li>
        <h3>Send us the brief</h3>
        <p>Date, headcount, delivery address and any dietary requirements. Two minutes on the quote form.</p>
      </li>
      <li>
        <h3>We send a menu and a fixed quote</h3>
        <p>Back within one business day with a menu built around your group and an all-inclusive price. Adjust it as much as you like.</p>
      </li>
      <li>
        <h3>We deliver hot and set up</h3>
        <p>We arrive ahead of your start time, set the buffet, label the dietary dishes and get out of your way.</p>
      </li>
    </ol>
  </div>
</section>

<section class="section">
  <div class="container split">
    <div class="split__media">
      <img src="/assets/img/dishes/CMR66B7SJJ77T.jpg" alt="Vegan Pad Ka Praw with rice" width="574" height="574" loading="lazy">
    </div>
    <div>
      <span class="eyebrow">Dietary requirements</span>
      <h2>Nobody eats a sad side salad</h2>
      <p>Thai food is genuinely good at this. Our vegan and gluten-free dishes are the same dishes &mdash; same wok, same flavour &mdash; not an afterthought plated separately.</p>
      {DIET}
      <a class="btn btn--dark" href="/menu/">Browse the catering menu</a>
    </div>
  </div>
</section>

{GALLERY}

{REVIEWS}

{CTA}""" \
        .replace("{CARDS}", cards) \
        .replace("{PACKAGES}", package_cards()) \
        .replace("{GALLERY}", gallery_section()) \
        .replace("{REVIEWS}", reviews_block()) \
        .replace("{CTA}", CTA_BAND) \
        .replace("{DIET}", ticks([
            "10 vegan mains and 12 gluten-free mains to choose from",
            "No surcharge for dietary versions of a dish",
            "Every dietary dish is labelled and served separately on delivery",
            "Tell us the numbers and we portion for them &mdash; no one misses out",
        ])) \
        .replace("{CHECK}", ICON["check"]) \
        .replace("{CHEF}", ICON["chef"]) \
        .replace("{LEAF}", ICON["leaf"]) \
        .replace("{CLOCK}", ICON["clock"]) \
        .replace("{DOC}", ICON["doc"])

    write("/index.html", page(
        "/", "Thai Catering Brisbane | Office &amp; Corporate Catering | " + NAME,
        "Thai street food catering for Brisbane offices, meetings and staff events. Packages from $24 per person, vegan and gluten-free included, delivered hot and ready to serve.",
        body, "/", schema=True))


def build_packages():
    addons = [
        ("Entr&eacute;e platter &mdash; Moo Ping skewers, spring rolls, Thai fish cakes", "$9 per person"),
        ("Thai snack grazing board &mdash; crispy pork crackers, jerky, Nam Prik dips", "$11 per person"),
        ("Mango sticky rice", "$7 per person"),
        ("Ari&rsquo;s Thai iced tea station &mdash; milk tea, lemon tea, O-Liang", "$6 per person"),
        ("Extra main added to any package", "$8 per person"),
        ("Extra steamed jasmine rice", "$3 per person"),
        ("Staffed service &mdash; one server, up to 3 hours", "$220 per server"),
        ("Delivery beyond Brisbane CBD and inner suburbs", "Quoted per event"),
    ]
    addon_html = "\n".join(
        '      <li><span class="addons__name">%s</span><span class="addons__price">%s</span></li>' % (n, p)
        for n, p in addons)

    faqs = [
        ("How much notice do you need?",
         "<p>24 hours for the Street Lunch package, and 48 hours for Banquet and Street Feast so we can prep the entr&eacute;es and desserts. If you&rsquo;re in a bind, call us &mdash; we can often make same-day work for smaller groups.</p>"),
        ("What is the minimum order?",
         "<p>10 guests for Street Lunch, 15 for Ari Banquet and 20 for Street Feast. Below 10 people you&rsquo;re usually better off ordering direct from the restaurant &mdash; happy to point you there.</p>"),
        ("Do you deliver outside the CBD?",
         "<p>Delivery into Brisbane CBD and the inner suburbs is included in the per-person price. Further out we&rsquo;ll quote the delivery separately &mdash; just put the address on the enquiry form.</p>"),
        ("How do you handle allergies?",
         "<p>Tell us on the enquiry form and we&rsquo;ll build the menu around it. Dietary dishes are cooked separately and labelled clearly on delivery. Please note our kitchen handles nuts, shellfish, gluten, soy and sesame, so we can&rsquo;t guarantee a dish is free of traces.</p>"),
        ("Can we get an invoice for the finance team?",
         "<p>Yes. We invoice with an ABN and can quote against a purchase order number. Add the PO number to the notes field and it will appear on the invoice.</p>"),
        ("What if our numbers change?",
         "<p>Final numbers are due 48 hours before delivery. Small increases after that are usually fine &mdash; call and we&rsquo;ll do what we can.</p>"),
    ]
    faq_html = "\n".join(
        """      <details>
        <summary>%s</summary>
        <div class="faq__body">%s</div>
      </details>""" % (q, a) for q, a in faqs)

    body = """<section class="hero hero--page" style="background-image:url('/assets/img/brand/menu-hero.jpg')">
  <div class="container">
    <div class="hero__inner">
      <span class="eyebrow">Packages &amp; pricing</span>
      <h1>One price per head. <span class="accent">Everything included.</span></h1>
      <p class="hero__lede">Food, serving equipment and delivery into Brisbane CBD are all in the per-person price. Pick a package, then we&rsquo;ll build the menu around your group.</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="/enquiry/">Get a quote</a>
        <a class="btn btn--ghost" href="/menu/">See the catering menu</a>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {PACKAGES}
    <p class="text-center" style="margin-top:2rem;color:var(--muted);font-size:0.92rem">
      Prices are per person, include GST, and cover delivery into Brisbane CBD and inner suburbs.
    </p>
  </div>
</section>

<section class="section section--cream section--tight">
  <div class="container">
    <div class="split split--top">
      <div>
        <span class="eyebrow">In every package</span>
        <h2>What you always get</h2>
        {INCLUDED}
      </div>
      <div>
        <span class="eyebrow">Optional extras</span>
        <h2>Add-ons</h2>
        <ul class="addons">
{ADDONS}
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="section section--ink">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">How it works</span>
      <h2>From brief to buffet</h2>
    </div>
    <ol class="steps">
      <li><h3>Send us the brief</h3><p>Date, headcount, address and dietary requirements.</p></li>
      <li><h3>We send a menu and a fixed quote</h3><p>Within one business day. Change as much as you like before you confirm.</p></li>
      <li><h3>We deliver hot and set up</h3><p>Ahead of your start time, buffet set, dietary dishes labelled.</p></li>
    </ol>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">Good to know</span>
      <h2>Questions we get asked</h2>
    </div>
    <div class="faq">
{FAQS}
    </div>
  </div>
</section>

{CTA}""" \
        .replace("{PACKAGES}", package_cards()) \
        .replace("{ADDONS}", addon_html) \
        .replace("{FAQS}", faq_html) \
        .replace("{CTA}", CTA_BAND) \
        .replace("{INCLUDED}", ticks([
            "Delivery into Brisbane CBD and inner suburbs",
            "Chafing dishes or insulated carriers so food arrives hot",
            "Serving tongs and spoons for every dish",
            "Plates, bowls, napkins and cutlery",
            "Vegan and gluten-free dishes at no surcharge, labelled separately",
            "Menu cards listing every dish and its dietary tags",
            "One tax invoice, PO number included if you need it",
        ]))

    write("/packages/index.html", page(
        "/packages/", "Catering Packages &amp; Pricing | " + NAME,
        "Thai catering packages for Brisbane offices from $24 per person. See what is included in Street Lunch, Ari Banquet and Street Feast, plus add-ons and delivery.",
        body, "/packages/", og_image="/assets/img/brand/menu-hero.jpg"))


def build_menu():
    nav, blocks = menu_sections()
    body = """<section class="hero hero--page" style="background-image:url('/assets/img/brand/stir-fry-tile.jpg')">
  <div class="container">
    <div class="hero__inner">
      <span class="eyebrow">Catering menu</span>
      <h1>Pick your dishes. <span class="accent">We&rsquo;ll do the rest.</span></h1>
      <p class="hero__lede">The full range we cater from &mdash; the same dishes we cook at the restaurant, portioned for a room. Dishes are chosen by package rather than priced individually.</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="/enquiry/">Get a quote</a>
        <a class="btn btn--ghost" href="/packages/">See packages &amp; pricing</a>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {NAV}
{BLOCKS}
    <p style="color:var(--muted);font-size:0.92rem;max-width:62ch">
      Menu subject to seasonal availability. Our kitchen handles nuts, shellfish, gluten, soy and sesame &mdash;
      tell us about allergies on the <a href="/enquiry/" style="color:var(--red);font-weight:700">enquiry form</a> and we&rsquo;ll work around them,
      but we can&rsquo;t guarantee a dish is free of traces.
    </p>
  </div>
</section>

{CTA}""".replace("{NAV}", nav).replace("{BLOCKS}", blocks).replace("{CTA}", CTA_BAND)

    write("/menu/index.html", page(
        "/menu/", "Thai Catering Menu | " + NAME,
        "The full Ari catering menu: Thai mains and stir-fries, entrees and skewers, vegan and gluten-free dishes, grazing boards and Thai iced teas for Brisbane offices and events.",
        body, "/menu/", og_image="/assets/img/brand/stir-fry-tile.jpg"))


def build_about():
    body = """<section class="hero hero--page" style="background-image:url('/assets/img/brand/entree-tile.jpg')">
  <div class="container">
    <div class="hero__inner">
      <span class="eyebrow">About</span>
      <h1>From Thailand, <span class="accent">with love.</span></h1>
      <p class="hero__lede">Ari started as a Brisbane City restaurant. Catering is the same food, the same kitchen and the same people &mdash; just brought to you.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container split">
    <div class="prose">
      <span class="eyebrow">Our story</span>
      <h2>Welcome to Ari</h2>
      <p>Ari was born from my heart and my love for sharing food, stories and smiles. I grew up in Thailand, surrounded by a big, loving family where food brought us all together. Every meal was a celebration &mdash; of flavour, of laughter, of being with the people you love.</p>
      <p>I moved to Australia 24 years ago, and this country quickly became my second home. Along the way I found so much to love, but I never lost my passion for the bold, fresh, colourful flavours of Thai street food. That passion is what inspired Ari.</p>
      <p>Catering felt like the natural next step. The best moments in Thailand happen around a table that&rsquo;s too full, with everyone reaching across each other. That&rsquo;s what we want to bring into your office &mdash; not a stack of identical lunch boxes, but a proper spread that gets people talking.</p>
      <blockquote>I want every bite to take you on a little trip to Thailand &mdash; to make you feel like you&rsquo;re dancing through a busy market street, surrounded by delicious smells and warm smiles.</blockquote>
      <p>Whether your team is trying Thai food for the first time or has loved it for years, you&rsquo;re always welcome here. Thanks for stopping by. I can&rsquo;t wait to cook for you.</p>
      <p><strong>&mdash; Yada</strong></p>
    </div>
    <div class="split__media">
      <img src="/assets/img/brand/pad-kra-pow-hero.jpg" alt="Pad Kra Pow with jasmine rice" width="1500" height="1125" loading="lazy">
    </div>
  </div>
</section>

<section class="section section--cream">
  <div class="container split split--reverse">
    <div class="split__media">
      <img src="/assets/img/dishes/SBARCTJXW2SC4.jpg" alt="Set of Moo Ping pork skewers" width="574" height="574" loading="lazy">
    </div>
    <div class="prose">
      <span class="eyebrow">The name</span>
      <h2>Why &ldquo;Ari&rdquo;?</h2>
      <p>Ari isn&rsquo;t just a name &mdash; it&rsquo;s a feeling. In Bangkok, Ari is a trendy, vibrant suburb known for its cool caf&eacute;s, creative energy and, most of all, amazing street food. It&rsquo;s the kind of place where you can grab something delicious any time of day or night.</p>
      <p>Locals love it for its laid-back vibe, buzzing food stalls, and the way it brings people together. Whether you&rsquo;re on a quick lunch break, catching up with friends, or craving a late-night snack, Ari is <em>the</em> place to be.</p>
      <p>That&rsquo;s exactly the spirit we bring to catering. Fast, fresh, full of flavour, and made to share. To us, real Thai food isn&rsquo;t just about spice or ingredients &mdash; it&rsquo;s about community. It&rsquo;s about dishes that bring people together, start conversations and make memories.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <span class="eyebrow">How we work</span>
      <h2>What you can count on</h2>
    </div>
    <div class="grid grid--3">
      <div class="card">
        <div class="card__icon">{CHEF}</div>
        <h3>One kitchen, one standard</h3>
        <p>Catering comes out of the same Adelaide St kitchen that serves our restaurant guests every day. Nothing is outsourced.</p>
      </div>
      <div class="card">
        <div class="card__icon">{USERS}</div>
        <h3>A real person on the phone</h3>
        <p>You deal with us directly, not a booking platform. Call and you&rsquo;ll speak to someone who knows your order.</p>
      </div>
      <div class="card">
        <div class="card__icon">{FLAME}</div>
        <h3>Cooked to order, not held</h3>
        <p>We cook to your delivery time, not the night before. Chafing dishes and insulated carriers keep it hot until you serve.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section--cream section--tight">
  <div class="container">
    <div class="split">
      <div>
        <span class="eyebrow">Find the restaurant</span>
        <h2>Come and taste it first</h2>
        <p class="lede">Planning something big? Drop into the restaurant in Brisbane City and try the menu before you book. We&rsquo;re open seven days.</p>
      </div>
      <div class="aside-card">
        <ul class="contact-list">
          <li>{PIN} <span>{ADDRESS}</span></li>
          <li>{CLOCK} <span>Mon&ndash;Fri 9.00am&ndash;8.00pm<br>Sat&ndash;Sun 10.00am&ndash;6.00pm</span></li>
          <li>{PHONE_ICON} <a href="tel:{PHONE_HREF}">{PHONE}</a></li>
          <li>{MAIL} <a href="mailto:{EMAIL}">{EMAIL}</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>

{CTA}""" \
        .replace("{CTA}", CTA_BAND) \
        .replace("{CHEF}", ICON["chef"]).replace("{USERS}", ICON["users"]).replace("{FLAME}", ICON["flame"]) \
        .replace("{PIN}", ICON["pin"]).replace("{CLOCK}", ICON["clock"]) \
        .replace("{PHONE_ICON}", ICON["phone"]).replace("{MAIL}", ICON["mail"]) \
        .replace("{ADDRESS}", ADDRESS).replace("{PHONE_HREF}", PHONE_HREF) \
        .replace("{PHONE}", PHONE).replace("{EMAIL}", EMAIL)

    write("/about/index.html", page(
        "/about/", "About Ari | Thai Catering Brisbane | " + NAME,
        "Ari Thai Catering is the catering arm of Ari - Thai Street Food in Brisbane City. Read Yada's story and how we cook and deliver for offices and events.",
        body, "/about/", og_image="/assets/img/brand/entree-tile.jpg"))


def build_enquiry():
    body = """<section class="hero hero--page" style="background-image:url('/assets/img/brand/menu-hero.jpg')">
  <div class="container">
    <div class="hero__inner">
      <span class="eyebrow">Get a quote</span>
      <h1>Tell us about your event</h1>
      <p class="hero__lede">Two minutes now, a menu and a fixed quote back within one business day. No obligation, no sales calls.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="container enquiry-layout">
    <div>
      <ol class="progress">
        <li aria-current="step">1. Your event</li>
        <li>2. Food &amp; service</li>
        <li>3. Your details</li>
      </ol>

      <div class="form-card">
        <form id="enquiry-form" action="{FORM_ENDPOINT}" method="POST">
          <input type="hidden" name="_subject" value="New catering enquiry &ndash; {NAME}">
          <input type="hidden" name="_template" value="table">
          <input type="hidden" name="_captcha" value="false">
          <input type="hidden" name="_next" value="https://{DOMAIN}/enquiry/thank-you/">
          <div class="hp" aria-hidden="true"><label>Leave this empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>

          <fieldset class="fieldset">
            <legend>Your event</legend>
            <p class="fieldset__hint">The basics, so we can check we&rsquo;re free and price it properly.</p>

            <div class="field">
              <span class="label">What kind of event is it?</span>
              <div class="choices">
                <label class="choice"><input type="radio" name="Event type" value="Office or working lunch" required><span>Office or working lunch</span></label>
                <label class="choice"><input type="radio" name="Event type" value="Board or client meeting"><span>Board or client meeting</span></label>
                <label class="choice"><input type="radio" name="Event type" value="Staff celebration"><span>Staff celebration</span></label>
                <label class="choice"><input type="radio" name="Event type" value="Conference or all-day event"><span>Conference or all-day event</span></label>
                <label class="choice"><input type="radio" name="Event type" value="Something else"><span>Something else</span></label>
              </div>
            </div>

            <div class="field-row">
              <div class="field">
                <label for="date">Date of the event</label>
                <input type="date" id="date" name="Event date" required>
              </div>
              <div class="field">
                <label for="time">Delivery time</label>
                <input type="time" id="time" name="Delivery time" required>
              </div>
            </div>

            <div class="field-row">
              <div class="field">
                <label for="guests">How many guests?</label>
                <input type="number" id="guests" name="Guest count" min="10" step="1" placeholder="e.g. 25" required>
              </div>
              <div class="field">
                <label for="suburb">Delivery suburb</label>
                <input type="text" id="suburb" name="Delivery suburb" placeholder="e.g. Brisbane City" autocomplete="address-level2" required>
              </div>
            </div>

            <div class="field">
              <label for="address">Delivery address <span class="opt">(optional for now)</span></label>
              <input type="text" id="address" name="Delivery address" placeholder="Level, building, street" autocomplete="street-address">
            </div>

            <div class="form-nav">
              <button type="button" class="btn btn--ghost" data-nav="back">Back</button>
              <button type="button" class="btn btn--primary" data-nav="next">Continue</button>
            </div>
          </fieldset>

          <fieldset class="fieldset">
            <legend>Food &amp; service</legend>
            <p class="fieldset__hint">A rough steer is plenty &mdash; we&rsquo;ll suggest a menu and you can change anything.</p>

            <div class="field">
              <span class="label">Which package looks closest?</span>
              <div class="choices">
                <label class="choice"><input type="radio" name="Package" value="Street Lunch - from $24pp"><span>Street Lunch &mdash; from $24pp</span></label>
                <label class="choice"><input type="radio" name="Package" value="Ari Banquet - from $34pp"><span>Ari Banquet &mdash; from $34pp</span></label>
                <label class="choice"><input type="radio" name="Package" value="Street Feast - from $46pp"><span>Street Feast &mdash; from $46pp</span></label>
                <label class="choice"><input type="radio" name="Package" value="Not sure yet - recommend something"><span>Not sure &mdash; recommend something</span></label>
              </div>
            </div>

            <div class="field">
              <span class="label">How would you like it served?</span>
              <div class="choices">
                <label class="choice"><input type="radio" name="Service style" value="Drop-off, we serve ourselves"><span>Drop-off, we serve ourselves</span></label>
                <label class="choice"><input type="radio" name="Service style" value="Drop-off with buffet setup"><span>Drop-off with buffet setup</span></label>
                <label class="choice"><input type="radio" name="Service style" value="Staffed service"><span>Staffed service</span></label>
              </div>
            </div>

            <div class="field-row">
              <div class="field">
                <label for="vegan">Vegan guests <span class="opt">(optional)</span></label>
                <input type="number" id="vegan" name="Vegan guests" min="0" step="1" placeholder="0">
              </div>
              <div class="field">
                <label for="gf">Gluten-free guests <span class="opt">(optional)</span></label>
                <input type="number" id="gf" name="Gluten-free guests" min="0" step="1" placeholder="0">
              </div>
            </div>

            <div class="field">
              <label for="dietary">Allergies or other dietary needs <span class="opt">(optional)</span></label>
              <textarea id="dietary" name="Dietary notes" placeholder="Nut allergy, dairy free, halal, no pork &mdash; anything we should know."></textarea>
            </div>

            <div class="form-nav">
              <button type="button" class="btn btn--ghost" data-nav="back">Back</button>
              <button type="button" class="btn btn--primary" data-nav="next">Continue</button>
            </div>
          </fieldset>

          <fieldset class="fieldset">
            <legend>Your details</legend>
            <p class="fieldset__hint">Last step. We&rsquo;ll reply within one business day.</p>

            <div class="field-row">
              <div class="field">
                <label for="name">Your name</label>
                <input type="text" id="name" name="Name" autocomplete="name" required>
              </div>
              <div class="field">
                <label for="company">Company <span class="opt">(optional)</span></label>
                <input type="text" id="company" name="Company" autocomplete="organization">
              </div>
            </div>

            <div class="field-row">
              <div class="field">
                <label for="email">Email</label>
                <input type="email" id="email" name="Email" autocomplete="email" required>
              </div>
              <div class="field">
                <label for="phone">Phone</label>
                <input type="tel" id="phone" name="Phone" autocomplete="tel" required>
              </div>
            </div>

            <div class="field">
              <label for="po">Purchase order number <span class="opt">(optional)</span></label>
              <input type="text" id="po" name="PO number" placeholder="Goes on your invoice">
            </div>

            <div class="field">
              <label for="notes">Anything else? <span class="opt">(optional)</span></label>
              <textarea id="notes" name="Notes" placeholder="Loading dock access, lift codes, budget per head, a theme &mdash; whatever helps."></textarea>
            </div>

            <div class="form-nav">
              <button type="button" class="btn btn--ghost" data-nav="back">Back</button>
              <button type="submit" class="btn btn--primary" data-nav="submit">Send enquiry</button>
            </div>
            <p class="form-note">We only use your details to quote and organise your catering. See our <a href="/privacy-policy/">privacy policy</a>.</p>
          </fieldset>
        </form>
      </div>
    </div>

    <aside>
      <div class="aside-card">
        <h3>Rather just talk?</h3>
        <ul class="contact-list">
          <li>{PHONE_ICON} <a href="tel:{PHONE_HREF}"><strong>{PHONE}</strong></a></li>
          <li>{MAIL} <a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>{PIN} <span>{ADDRESS}</span></li>
        </ul>
      </div>
      <div class="aside-card">
        <h3>What happens next</h3>
        {NEXT}
      </div>
      <div class="aside-card">
        <h3>Before you send</h3>
        {BEFORE}
      </div>
    </aside>
  </div>
</section>""" \
        .replace("{FORM_ENDPOINT}", FORM_ENDPOINT).replace("{NAME}", NAME).replace("{DOMAIN}", DOMAIN) \
        .replace("{PHONE_ICON}", ICON["phone"]).replace("{MAIL}", ICON["mail"]).replace("{PIN}", ICON["pin"]) \
        .replace("{PHONE_HREF}", PHONE_HREF).replace("{PHONE}", PHONE).replace("{EMAIL}", EMAIL) \
        .replace("{ADDRESS}", ADDRESS) \
        .replace("{NEXT}", ticks([
            "We check the date and confirm we&rsquo;re available",
            "You get a suggested menu and an all-inclusive quote",
            "Change anything you like &mdash; then confirm when you&rsquo;re ready",
        ])) \
        .replace("{BEFORE}", ticks([
            "Minimum 10 guests",
            "24 hours&rsquo; notice (48 for the larger packages)",
            "Final numbers due 48 hours before delivery",
        ]))

    write("/enquiry/index.html", page(
        "/enquiry/", "Get a Catering Quote | " + NAME,
        "Request a Thai catering quote for your Brisbane office or event. Tell us the date, headcount and dietary needs and we will send a menu and fixed price within one business day.",
        body, "/enquiry/", og_image="/assets/img/brand/menu-hero.jpg"))


def build_thanks():
    body = """<section class="section" style="text-align:center">
  <div class="container" style="max-width:44rem">
    <span class="eyebrow">Enquiry sent</span>
    <h1>Thanks &mdash; we&rsquo;ve got it.</h1>
    <p class="lede" style="margin-inline:auto">We&rsquo;ll come back to you with a menu and a fixed quote within one business day. If your event is sooner than that, give us a call and we&rsquo;ll sort it now.</p>
    <div class="btn-row" style="justify-content:center;margin-top:1.5rem">
      <a class="btn btn--dark" href="tel:{PHONE_HREF}">Call {PHONE}</a>
      <a class="btn btn--ghost on-light" href="/menu/">Browse the menu</a>
    </div>
  </div>
</section>""".replace("{PHONE_HREF}", PHONE_HREF).replace("{PHONE}", PHONE)

    write("/enquiry/thank-you/index.html", page(
        "/enquiry/thank-you/", "Thanks for your enquiry | " + NAME,
        "Your catering enquiry has been sent. We reply within one business day.",
        body, "/enquiry/"))


LEGAL_NOTE = ('<p style="background:#fff5e2;border:1px solid #f2d99a;border-radius:9px;padding:1rem 1.15rem;'
              'font-size:0.93rem"><strong>Draft for review.</strong> This page is a starting point written to match '
              'how the site actually works. Please read it against your final trading terms &mdash; and have it '
              'checked professionally &mdash; before the site goes live.</p>')


def build_privacy():
    body = """<section class="hero hero--page">
  <div class="container"><div class="hero__inner">
    <span class="eyebrow">Legal</span><h1>Privacy policy</h1>
    <p class="hero__lede">How we handle the information you send us.</p>
  </div></div>
</section>
<section class="section"><div class="container prose">
  {NOTE}
  <p><strong>Last updated:</strong> {YEAR}</p>

  <h2>Who we are</h2>
  <p>{NAME} (&ldquo;we&rdquo;, &ldquo;us&rdquo;) provides Thai catering in Brisbane, Queensland. You can reach us at <a href="mailto:{EMAIL}">{EMAIL}</a> or {PHONE}.</p>

  <h2>What we collect</h2>
  <p>We collect only what you give us. Through the enquiry form on this site that is:</p>
  <ul>
    <li>your name, company, email address and phone number;</li>
    <li>details of your event &mdash; date, delivery time, guest numbers, delivery address and suburb;</li>
    <li>dietary requirements and allergies you choose to tell us about;</li>
    <li>any purchase order number or notes you add.</li>
  </ul>
  <p>This site does not use advertising or analytics cookies, and it does not track you across other websites.</p>

  <h2>How we use it</h2>
  <p>We use your information to reply to your enquiry, prepare a quote, organise and deliver your catering, and invoice you. We may contact you about your booking. We do not sell your information, and we do not add you to a marketing list without your consent.</p>

  <h2>Who else sees it</h2>
  <p>Enquiries submitted through this site are delivered to our email inbox by a third-party form service. Our email provider and, where relevant, our accounting software also store your details. We ask these providers to keep your information secure, but they operate under their own privacy terms.</p>

  <h2>How long we keep it</h2>
  <p>We keep enquiry and booking records for as long as we need them to run the business and to meet Australian tax and record-keeping obligations, then delete them.</p>

  <h2>Your choices</h2>
  <p>You can ask us what information we hold about you, ask us to correct it, or ask us to delete it. Email <a href="mailto:{EMAIL}">{EMAIL}</a> and we&rsquo;ll respond as soon as we can. If you&rsquo;re not satisfied with how we&rsquo;ve handled a privacy matter, you can contact the Office of the Australian Information Commissioner at <a href="https://www.oaic.gov.au/" rel="noopener">oaic.gov.au</a>.</p>

  <h2>Changes</h2>
  <p>If we change this policy we&rsquo;ll update the date at the top of this page.</p>
</div></section>""".replace("{NOTE}", LEGAL_NOTE).replace("{NAME}", NAME).replace("{EMAIL}", EMAIL) \
                   .replace("{PHONE}", PHONE).replace("{YEAR}", str(YEAR))

    write("/privacy-policy/index.html", page(
        "/privacy-policy/", "Privacy policy | " + NAME,
        "How Ari Thai Catering collects, uses and protects the information you send through this website.",
        body, "/privacy-policy/"))


def build_terms():
    body = """<section class="hero hero--page">
  <div class="container"><div class="hero__inner">
    <span class="eyebrow">Legal</span><h1>Terms &amp; conditions</h1>
    <p class="hero__lede">The terms we cater under.</p>
  </div></div>
</section>
<section class="section"><div class="container prose">
  {NOTE}
  <p><strong>Last updated:</strong> {YEAR}</p>

  <h2>Quotes</h2>
  <p>Quotes are valid for 14 days and are based on the guest numbers, menu and delivery details you give us. Prices shown on this website are indicative starting prices per person and include GST. Your quote is the price that applies.</p>

  <h2>Confirming a booking</h2>
  <p>A booking is confirmed when you accept the quote in writing. For orders over $500 we ask for a 50% deposit to hold the date, with the balance due on the day of the event unless we&rsquo;ve agreed account terms with you.</p>

  <h2>Notice and minimums</h2>
  <ul>
    <li>Minimum 10 guests.</li>
    <li>24 hours&rsquo; notice for the Street Lunch package; 48 hours for Ari Banquet and Street Feast.</li>
    <li>Final guest numbers are due 48 hours before delivery. That number is what we cook and invoice for. We&rsquo;ll do our best to accommodate small increases after that.</li>
  </ul>

  <h2>Changes and cancellations</h2>
  <ul>
    <li>Cancel more than 48 hours before delivery and any deposit is refunded in full.</li>
    <li>Cancel within 48 hours and the deposit is retained to cover ingredients and prep already committed.</li>
    <li>Cancel within 24 hours and the full quoted amount is payable.</li>
    <li>Menu changes are free up to 48 hours before delivery.</li>
  </ul>

  <h2>Delivery</h2>
  <p>Delivery into Brisbane CBD and inner suburbs is included in the per-person price. Deliveries further out are quoted separately. Please make sure we have accurate access details &mdash; loading dock, lift or security codes, and a contact on site. If we can&rsquo;t deliver because access wasn&rsquo;t available, the order is still payable.</p>

  <h2>Food safety and allergens</h2>
  <p>Food is prepared to be served within two hours of delivery. Once we hand it over, responsibility for safe handling and storage passes to you, and we can&rsquo;t accept responsibility for food consumed outside that window.</p>
  <p>We take allergies seriously and will build your menu around the requirements you give us. However, our kitchen handles nuts, shellfish, gluten, soy, sesame, egg and dairy, so we cannot guarantee any dish is free from traces of an allergen. Please tell us about allergies at the time of booking, not on the day.</p>

  <h2>Equipment</h2>
  <p>Chafing dishes, platters and serving equipment remain our property. We&rsquo;ll arrange collection after your event. Replacement cost applies to items that are damaged or not returned.</p>

  <h2>Payment</h2>
  <p>We invoice with an ABN and can include your purchase order number. Invoices are payable within 7 days unless we&rsquo;ve agreed otherwise in writing.</p>

  <h2>Things outside our control</h2>
  <p>Occasionally an ingredient is unavailable and we substitute a comparable dish &mdash; we&rsquo;ll let you know if that happens. We&rsquo;re not liable for failure to deliver caused by events beyond our reasonable control, but we&rsquo;ll refund anything you&rsquo;ve paid for catering we couldn&rsquo;t supply.</p>

  <h2>Questions</h2>
  <p>Email <a href="mailto:{EMAIL}">{EMAIL}</a> or call {PHONE}.</p>
</div></section>""".replace("{NOTE}", LEGAL_NOTE).replace("{EMAIL}", EMAIL) \
                   .replace("{PHONE}", PHONE).replace("{YEAR}", str(YEAR))

    write("/terms-conditions/index.html", page(
        "/terms-conditions/", "Terms &amp; conditions | " + NAME,
        "Booking, notice, cancellation, delivery and allergen terms for Ari Thai Catering in Brisbane.",
        body, "/terms-conditions/"))


def build_404():
    body = """<section class="section" style="text-align:center">
  <div class="container" style="max-width:40rem">
    <span class="eyebrow">404</span>
    <h1>This page has been eaten.</h1>
    <p class="lede" style="margin-inline:auto">We couldn&rsquo;t find what you were after. Try the catering menu, or tell us about your event and we&rsquo;ll take it from there.</p>
    <div class="btn-row" style="justify-content:center;margin-top:1.5rem">
      <a class="btn btn--dark" href="/">Back to home</a>
      <a class="btn btn--ghost on-light" href="/enquiry/">Get a quote</a>
    </div>
  </div>
</section>"""
    write("/404.html", page("/404.html", "Page not found | " + NAME,
                            "The page you were looking for could not be found.", body, ""))


def build_meta():
    paths = ["/", "/packages/", "/menu/", "/about/", "/enquiry/", "/privacy-policy/", "/terms-conditions/"]
    urls = "\n".join("  <url><loc>https://%s%s</loc></url>" % (DOMAIN, p) for p in paths)
    write("/sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
                          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % urls)
    write("/robots.txt", "User-agent: *\nAllow: /\n\nSitemap: https://%s/sitemap.xml\n" % DOMAIN)


if __name__ == "__main__":
    print("Building %s (%s)\n" % (NAME, DOMAIN))
    build_home()
    build_packages()
    build_menu()
    build_about()
    build_enquiry()
    build_thanks()
    build_privacy()
    build_terms()
    build_404()
    build_meta()
    print("\nDone.")
