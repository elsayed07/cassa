"""
Download placeholder images and add rich content to seeded products/brands/categories.

Usage:
    python manage.py populate
"""
from __future__ import annotations

import random
import urllib.request
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

# Picsum photos: deterministic per seed string, free, no API key
PICSUM_URL = "https://picsum.photos/seed/{seed}/{w}/{h}"

DESCRIPTIONS = {
    "tee": [
        "Crafted from 100% organic cotton, this tee offers all-day comfort with a clean, modern silhouette. The fabric is pre-washed for softness and a relaxed fit that holds its shape wash after wash.",
        "A wardrobe essential. This classic tee is cut from heavyweight jersey that drapes beautifully and resists the wear of everyday life. Available in a range of versatile colourways.",
        "Minimal by design, built to last. The reinforced collar and double-stitched hem make this the tee you'll reach for first, every time.",
    ],
    "jacket": [
        "Engineered for the in-between seasons, this jacket layers effortlessly over anything. The water-resistant shell keeps you dry while the quilted lining adds warmth without bulk.",
        "A technical shell with a clean aesthetic. Taped seams, an adjustable hem, and a media port in the chest pocket bring function to every commute and weekend adventure.",
        "Varsity-inspired construction meets contemporary tailoring. The premium wool-blend body and leather-trim sleeves make this the outerwear piece that finishes every outfit.",
    ],
    "sneaker": [
        "A low-profile silhouette with a vulcanised rubber sole and premium suede upper. The padded collar and cushioned insole keep you comfortable from morning to midnight.",
        "Retro running DNA reinterpreted for the street. The breathable mesh upper sits on a chunky foam midsole that delivers step-in comfort and lasting support.",
        "Clean lines, zero distractions. This monochromatic sneaker is built on a cupsole construction with an EVA footbed for full-day wearability.",
    ],
    "boot": [
        "Full-grain leather uppers and a Goodyear-welted construction make these boots a lifetime investment. The natural rubber lug sole grips equally well on city cobblestones and country trails.",
        "Water-resistant nubuck leather with a warm wool lining. These boots were built for the long haul — reinforced toe cap, padded collar, and a commando-style sole.",
        "Chelsea silhouette updated with a modern platform sole. The elastic gussets make them easy on and off; the polished leather keeps them sharp all day.",
    ],
    "bag": [
        "Structured enough for the office, relaxed enough for the weekend. The main compartment fits a 15-inch laptop; the front zip pocket keeps your daily essentials organised.",
        "Waxed canvas shell with full-grain leather trim. Every panel is cut and stitched by hand, and the solid brass hardware will outlast the canvas by decades.",
        "A minimal daypack built for urban movement. Padded back panel, hidden laptop sleeve, and a magnetic-close top pocket — everything in the right place.",
    ],
    "cap": [
        "Six-panel construction in a premium cotton twill. The pre-curved brim and adjustable snapback strap mean one size truly does fit all.",
        "An unstructured dad cap in washed cotton that softens beautifully with wear. The tonal embroidery on the front panel is subtle enough for every occasion.",
        "Technical mesh side panels keep you cool on the move; the front panel is dense enough to hold its structure all day. A clean logo hit completes the look.",
    ],
    "watch": [
        "Swiss quartz movement in a 40mm stainless steel case. The sapphire crystal glass resists scratching; the quick-release strap system lets you swap between leather and NATO in seconds.",
        "Minimalist dial with a sunburst finish and three-hand movement. Water-resistant to 50m and powered by a battery that lasts up to three years.",
        "An automatic movement visible through the exhibition caseback. The slim 38mm profile slides comfortably under a shirt cuff while the exhibition caseback shows the rotor in motion.",
    ],
}

BRAND_DESCRIPTIONS = {
    "Aria": "Aria crafts elevated essentials rooted in slow fashion. Every piece is designed to outlast the season it was made in.",
    "Nomad": "Nomad builds gear for people who move. Technically precise, built tough, designed to disappear into your routine.",
    "Ember": "Ember is where craft meets contemporary. Each collection starts with a material and a question: what's the best thing we can make from this?",
    "Solace": "Solace makes calm clothing. Considered proportions, muted palettes, and fabrics that feel as good as they look.",
    "Drift": "Drift brings surf culture to the city — relaxed shapes, salt-faded colours, and a commitment to natural fibres.",
}

CATEGORY_DESCRIPTIONS = {
    "clothing": "Timeless wardrobe builders made from materials that age well.",
    "footwear": "Shoes, boots, and sneakers for every surface and every occasion.",
    "accessories": "The details that complete the look.",
    "t-shirts": "Everyday tees in weights and fits for every wardrobe.",
    "jackets": "Outerwear from lightweight layers to full winter shells.",
    "denim": "Selvedge, raw, and washed — denim cut to last.",
    "sneakers": "Low-profile and performance silhouettes for the city and beyond.",
    "boots": "Chelsea, lace-up, and work styles built to take a beating.",
    "bags": "Packs, totes, and briefcases for everything you carry.",
    "hats": "Caps, beanies, and buckets for sun or rain.",
    "watches": "Time kept simply and well.",
}

# Curated Picsum IDs that look like fashion/lifestyle photography
PRODUCT_PHOTO_IDS = [
    10, 11, 12, 20, 21, 22, 30, 31, 32, 40, 41, 42,
    50, 51, 52, 60, 61, 62, 70, 71, 72, 80, 81, 82,
    90, 91, 100, 101, 110, 111, 120, 121, 130, 131, 140,
    150, 151, 160, 161, 170, 171, 180, 181, 190, 191,
]


def _fetch_image(url: str) -> bytes | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()
    except Exception:
        return None


class Command(BaseCommand):
    help = "Add images and rich content to seeded products, brands, and categories"

    def handle(self, *args, **options):
        self._populate_brands()
        self._populate_categories()
        self._populate_products()
        self.stdout.write(self.style.SUCCESS("Population complete."))

    def _populate_brands(self):
        from apps.catalog.models import Brand

        for brand in Brand.objects.all():
            name = brand.safe_translation_getter("name", any_language=True) or brand.slug
            desc = BRAND_DESCRIPTIONS.get(name, f"Quality products from {name}.")
            brand.set_current_language("en")
            if not brand.safe_translation_getter("description", any_language=True):
                brand.description = desc
                brand.save()

            if not brand.logo:
                seed = f"brand-{brand.slug}"
                url = PICSUM_URL.format(seed=seed, w=400, h=400)
                data = _fetch_image(url)
                if data:
                    brand.logo.save(f"{brand.slug}.jpg", ContentFile(data), save=True)
                    self.stdout.write(f"  Brand image: {name}")

        self.stdout.write(f"  Brands populated")

    def _populate_categories(self):
        from apps.catalog.models import Category

        for cat in Category.objects.all():
            slug = cat.slug
            desc = CATEGORY_DESCRIPTIONS.get(slug, "")
            cat.set_current_language("en")
            if not cat.safe_translation_getter("description", any_language=True) and desc:
                cat.description = desc
                cat.save()

            if not cat.image:
                url = PICSUM_URL.format(seed=f"cat-{slug}", w=800, h=400)
                data = _fetch_image(url)
                if data:
                    cat.image.save(f"{slug}.jpg", ContentFile(data), save=True)
                    self.stdout.write(f"  Category image: {slug}")

        self.stdout.write("  Categories populated")

    def _populate_products(self):
        from apps.catalog.models import Product
        from apps.catalog.models.product import ProductImage

        photo_ids = list(PRODUCT_PHOTO_IDS)
        random.shuffle(photo_ids)
        photo_cycle = photo_ids * 10  # enough for any product count

        updated = 0
        for i, product in enumerate(Product.objects.all()):
            name = product.safe_translation_getter("name", any_language=True) or ""
            noun = name.split()[-1].lower() if name else "product"
            desc_pool = DESCRIPTIONS.get(noun, DESCRIPTIONS["tee"])
            desc = desc_pool[i % len(desc_pool)]

            product.set_current_language("en")
            if not product.safe_translation_getter("description", any_language=True):
                product.description = desc
                product.save()

            if not product.images.exists():
                # Primary image
                primary_id = photo_cycle[i * 3 % len(photo_cycle)]
                url = PICSUM_URL.format(seed=f"p-{primary_id}-{product.slug[:8]}", w=800, h=800)
                data = _fetch_image(url)
                if data:
                    img = ProductImage(product=product, alt_text=name, position=0, is_primary=True)
                    img.image.save(f"{product.slug}-1.jpg", ContentFile(data), save=True)

                # Second angle
                secondary_id = photo_cycle[(i * 3 + 1) % len(photo_cycle)]
                url2 = PICSUM_URL.format(seed=f"p-{secondary_id}-{product.slug[:8]}-b", w=800, h=800)
                data2 = _fetch_image(url2)
                if data2:
                    img2 = ProductImage(product=product, alt_text=f"{name} detail", position=1, is_primary=False)
                    img2.image.save(f"{product.slug}-2.jpg", ContentFile(data2), save=True)

                updated += 1
                self.stdout.write(f"  Images: {name}")

        self.stdout.write(f"  Products populated ({updated} with new images)")
