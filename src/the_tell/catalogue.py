"""What Kettleworth Cafés Ltd buys, and the suppliers who sell it. All fictional."""

import random
from dataclasses import dataclass

from the_tell.domain import Supplier

ZERO = 0
STANDARD = 20


@dataclass(frozen=True)
class Product:
    sku: str
    description: str
    category: str
    base_price_pence: int
    vat_rate_pct: int  # the correct rate under the AP policy's VAT table


PRODUCTS = [
    Product("TEA-ASM-1K", "Assam loose leaf tea 1kg", "tea_coffee", 2450, ZERO),
    Product("TEA-EBT-1100", "English breakfast tea bags (box of 1,100)", "tea_coffee", 1890, ZERO),
    Product("TEA-EGL-500", "Earl Grey loose leaf tea 500g", "tea_coffee", 1675, ZERO),
    Product("COF-COL-1K", "Colombian coffee beans 1kg", "tea_coffee", 2290, ZERO),
    Product("COF-DEC-1K", "Decaffeinated coffee beans 1kg", "tea_coffee", 2540, ZERO),
    Product("DRY-WHL-6", "Whole milk 2L (case of 6)", "dairy", 795, ZERO),
    Product("DRY-SSK-6", "Semi-skimmed milk 2L (case of 6)", "dairy", 760, ZERO),
    Product("DRY-CRM-1L", "Double cream 1L", "dairy", 420, ZERO),
    Product("BAK-DIG-12", "Plain digestive biscuits 400g (case of 12)", "bakery", 1150, ZERO),
    Product("BAK-SHB-12", "All-butter shortbread fingers 150g (case of 12)", "bakery", 1380, ZERO),
    Product("BAK-SCN-24", "Fruit scones (tray of 24)", "bakery", 1440, ZERO),
    Product("BAK-VSP-12", "Victoria sponge, 12 slices", "bakery", 1650, ZERO),
    Product("SNK-CDG-12", "Milk chocolate digestives 300g (case of 12)", "snacks_drinks", 1320, STANDARD),
    Product("SNK-CSB-12", "Chocolate-coated shortbread 150g (case of 12)", "snacks_drinks", 1560, STANDARD),
    Product("SNK-CRS-24", "Sea salt crisps 40g (case of 24)", "snacks_drinks", 1080, STANDARD),
    Product("SNK-SPW-24", "Sparkling spring water 500ml (case of 24)", "snacks_drinks", 960, STANDARD),
    Product("PKG-CUP-1000", "12oz takeaway cups (case of 1,000)", "packaging", 6400, STANDARD),
    Product("PKG-LID-1000", "Sip lids for 12oz cups (case of 1,000)", "packaging", 3150, STANDARD),
    Product("PKG-NAP-5000", "Paper napkins (case of 5,000)", "packaging", 2780, STANDARD),
    Product("EQP-SVC-VISIT", "Espresso machine service visit", "equipment", 14500, STANDARD),
    Product("EQP-FLT-CART", "Water filter cartridge", "equipment", 6890, STANDARD),
]

PRODUCTS_BY_SKU = {p.sku: p for p in PRODUCTS}

ZERO_RATED_CATEGORIES = {"tea_coffee", "dairy", "bakery"}

# How many units a café typically orders per line, by category.
QTY_RANGE = {
    "tea_coffee": (2, 12),
    "dairy": (10, 60),
    "bakery": (2, 15),
    "snacks_drinks": (2, 12),
    "packaging": (1, 6),
    "equipment": (1, 2),
}

# Supplier type -> (name endings, categories they sell)
SUPPLIER_TYPES = {
    "tea": (["Tea Merchants", "Tea Company", "Leaf & Bean"], ["tea_coffee"]),
    "dairy": (["Dairies", "Farm Dairy"], ["dairy"]),
    "bakery": (["Bakery Supplies", "Fine Foods", "Biscuit Company"], ["bakery", "snacks_drinks"]),
    "packaging": (["Packaging", "Catering Disposables"], ["packaging"]),
    "equipment": (["Espresso Services", "Catering Engineers"], ["equipment"]),
    "wholesale": (["Wholesale", "Provisions", "Foodservice"], ["tea_coffee", "dairy", "bakery", "snacks_drinks"]),
}

PLACES = [
    "Ashby", "Brockley", "Calder", "Denholm", "Elstow", "Fenwick", "Garrow", "Hatherley",
    "Ilsley", "Kenley", "Lowther", "Marston", "Netherby", "Ormsby", "Pellow", "Quarrendon",
    "Radley", "Selby", "Thornbury", "Upton", "Wexcombe", "Yarrow", "Aldwick", "Burnell",
    "Corrie", "Dunmore", "Eskdale", "Farleigh", "Glenholt", "Harrowby", "Ingleby", "Kirkham",
    "Langdon", "Millbeck", "Norland", "Oakhurst", "Penrith Vale", "Redmire", "Stanwick", "Tarrant",
]

# Weighting of supplier types: mixed-VAT suppliers (bakery, wholesale) are common.
TYPE_CYCLE = ["tea", "dairy", "bakery", "wholesale", "packaging", "bakery", "wholesale", "equipment", "tea", "wholesale"]


def products_in(categories: list[str]) -> list[Product]:
    return [p for p in PRODUCTS if p.category in categories]


def fake_vat_number(rng: random.Random) -> str:
    d = "".join(str(rng.randint(0, 9)) for _ in range(9))
    return f"GB {d[:3]} {d[3:7]} {d[7:]}"


def make_suppliers(rng: random.Random, n: int = 40) -> list[Supplier]:
    places = rng.sample(PLACES, n)
    suppliers = []
    for i, place in enumerate(places):
        kind = TYPE_CYCLE[i % len(TYPE_CYCLE)]
        endings, categories = SUPPLIER_TYPES[kind]
        ending = rng.choice(endings)
        short = ending.split()[0]
        suppliers.append(
            Supplier(
                supplier_id=f"SUP-{i + 1:03d}",
                name=f"{place} {ending} Ltd",
                aliases=list(dict.fromkeys([f"{place} {ending}", f"{place} {short}"])),  # dedupe one-word endings
                vat_number=fake_vat_number(rng),
                bank_account_last4=f"{rng.randint(0, 9999):04d}",
                contract="fixed" if rng.random() < 0.35 else "variable",
                categories=categories,
                invoice_prefix=place[:3].upper(),
            )
        )
    return suppliers
