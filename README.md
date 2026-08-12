# Ari Thai Catering — website

Static marketing site for the catering arm of
[Ari – Thai Street Food](https://ari-thaistreetfood.com/), Brisbane City.

Hand-built HTML/CSS/JS — no framework, no build step to deploy, no external
requests at runtime. Brand, photography and story carried over from the
restaurant site; every page is written for **corporate and office catering**.

> **Nothing here is final.** The business name, domain, prices and trading
> terms are all placeholders chosen so the site can be reviewed as a whole.
> See [Before this goes live](#before-this-goes-live).

## Pages

| Path | Page | Job it does |
|---|---|---|
| `/` | Home | Positions the offer, shows price anchors, drives to the quote form |
| `/packages/` | Packages & pricing | Three tiers with per-person pricing, add-ons, FAQ |
| `/menu/` | Catering menu | 56 dishes with photos and dietary tags, grouped for catering |
| `/about/` | About Ari | Yada's story and the Bangkok "Ari" origin, catering-angled |
| `/enquiry/` | Get a quote | Three-step enquiry form |
| `/enquiry/thank-you/` | Confirmation | Where the form redirects on success |
| `/privacy-policy/` | Privacy policy | Draft — describes what the form actually collects |
| `/terms-conditions/` | Terms & conditions | Draft — deposits, notice, cancellation, allergens |

## Preview locally

Paths are root-relative, so it needs a server rather than `file://`:

```bash
python3 -m http.server 8736
```

Then open <http://localhost:8736/>.

## How it's put together

```
assets/css/site.css     design system — colours, type, components
assets/css/fonts.css    self-hosted Roboto + Roboto Slab (latin subsets only)
assets/js/site.js       mobile nav + the 3-step form. The only JS on the site.
assets/img/dishes/      87 dish photos from the restaurant's Clover menu
assets/img/brand/       logo and hero photography
assets/menu-data.json   dish names/ids, mirrored from the restaurant menu
site.config.json        name, domain, phone, email, form endpoint
tools/build.py          regenerates every HTML page
tools/rebrand.py        swaps name/domain/email across the whole site
```

The HTML files in the repo are what gets deployed. `tools/build.py` exists so
the shared header, footer and menu grid stay identical across pages — edit the
content blocks in it and re-run:

```bash
python3 tools/build.py
```

### Design notes

Carried over from the restaurant site so the two read as siblings: the
`#05070b` header, brand yellow `#f2c519`, logo red `#d32b1e`, and Roboto /
Roboto Slab. What's different is the build — the old site is a WordPress +
Elementor mirror whose home page is 234 KB of generated markup; these pages are
13–32 KB, self-hosted fonts, no third-party requests, and mobile-first.

Layout choices follow current catering-site conversion practice: visible
per-person price anchors rather than "call for pricing", menus grouped by
occasion, a short multi-step enquiry form instead of one long one, an explicit
response-time promise, and a sticky call/quote bar on mobile.

## Changing the name and domain

The name is a placeholder in one place. To change it everywhere:

```bash
python3 tools/rebrand.py --dry-run \
  --name "Ari Thai Street Food Catering" \
  --short "Ari" \
  --domain arithaistreetfoodcatering.com.au
```

Drop `--dry-run` to apply. It rewrites every HTML file, `sitemap.xml`,
`robots.txt`, `CNAME` and `site.config.json`. `--email` also repoints the
enquiry form.

## Before this goes live

Things that need a real decision, roughly in order of importance:

1. **Business name and domain.** Currently `Ari Thai Catering` /
   `arithaicatering.com.au`. Nothing is registered yet.
2. **Package prices.** `$24 / $34 / $46` per person and the add-on prices in
   `tools/build.py` are benchmarked against Brisbane caterers (Thai catering
   starts around $20pp; corporate buffets run $25–47pp) — they are **not**
   costed against your margins. Same for the minimums (10/15/20 guests).
3. **The enquiry form.** It posts to FormSubmit at
   `arithaistreetfood@gmail.com`. FormSubmit requires the first submission to
   be confirmed from that inbox before anything comes through — send one test
   enquiry and click the activation email. Consider a dedicated
   `catering@` address instead of the restaurant inbox.
4. **`_next` redirect.** The form redirects to
   `https://arithaicatering.com.au/enquiry/thank-you/`. That URL has to be the
   real domain or the redirect breaks — `tools/rebrand.py --domain` fixes it.
5. **Legal pages.** Both are drafts written to match how the site actually
   behaves. Read them against your real trading terms and get them checked.
6. **Claims to confirm.** The site states: delivery into Brisbane CBD and inner
   suburbs is included; 24h notice (48h for larger packages); final numbers due
   48h out; ABN invoicing and PO numbers supported; chafing dishes and
   servingware provided. All are reasonable defaults — confirm each is true.
7. **Reviews.** The four testimonials are real Google reviews of the
   *restaurant* and are labelled as such. Swap in catering reviews once you
   have them.
8. **Service scope.** Built for corporate and office catering only. Weddings,
   private parties and live cooking/market stalls are deliberately absent.

## Deploying on GitHub Pages

1. Settings → Pages → deploy from the branch, root folder.
2. Add the custom domain once registered — GitHub writes `CNAME`, and
   `tools/rebrand.py --domain` keeps the rest of the site in sync.
3. Point the domain's DNS at GitHub Pages.

Until the custom domain is live, a `username.github.io/aricatering/` preview
will have broken styling — the site uses root-relative paths, same as the
restaurant site.
