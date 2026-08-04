import random

from faker import Faker
from sqlalchemy.orm import Session

from dwh.db.models import Base, Company, Customer, Order, OrderLine, Product, CatalogItem, engine

fake = Faker("es_AR")
Faker.seed(42)
random.seed(42)

N_COMPANIES, N_SUPPLIERS, N_CUSTOMERS, N_PRODUCTS, N_ORDERS = 20, 5, 200, 100, 1000
ADJECTIVES = ["Heavy-Duty", "Industrial", "Reinforced", "Galvanised",
              "Compact", "Professional", "Standard", "Premium"]
MATERIALS = ["Steel", "Aluminium", "PVC", "Copper", "Rubber", "Nylon"]
ITEMS = ["Valve", "Bearing", "Coupling", "Hose Clamp", "Gasket", "Bracket",
         "Cable Tie", "Fastener", "Pump", "Filter", "Hinge", "Pallet Jack"]

def product_name() -> str:
    return f"{random.choice(ADJECTIVES)} {random.choice(MATERIALS)} {random.choice(ITEMS)}"

def cuit() -> str:
    return f"{random.randint(20, 34)}-{random.randint(10**7, 10**8 - 1)}-{random.randint(0, 9)}"


def main() -> None:
    eng = engine()
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)

    with Session(eng) as s:
        suppliers = [Company(cuit=cuit(), user_name=fake.unique.user_name()[:20], name=fake.company(), is_supplier=True)
                     for _ in range(N_SUPPLIERS)]
        buyers = [Company(cuit=cuit(), user_name=fake.unique.user_name()[:20], name=fake.company())
                  for _ in range(N_COMPANIES)]
        s.add_all(suppliers + buyers)
        s.flush()

        products = [
            Product(supplier_id=random.choice(suppliers).id,
                    name=product_name(),
                    default_price=round(random.uniform(10, 500), 2))
            for _ in range(N_PRODUCTS)
        ]
        customers = [
            Customer(company_id=random.choice(buyers).id,
                     document_number=str(fake.unique.random_number(8, True)),
                     full_name=fake.name(),
                     date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80))
            for _ in range(N_CUSTOMERS)
        ]
        s.add_all(products + customers)
        s.flush()

        catalog = {}
        company_products = {}
        for company in buyers:
            company_products[company.id] = []
            for product in random.sample(products, random.randint(5, 20)):
                price=round(float(product.default_price) * round(random.uniform(1.5, 2), 2))
                catalog_item = CatalogItem(company_id=company.id,
                                           product_id=product.id,
                                           price=price)
                catalog[(company.id, product.id)] = price
                company_products[company.id].append(product)
                s.add(catalog_item)
        s.flush()


        for _ in range(N_ORDERS):
            customer = random.choice(customers)
            order = Order(company_id=customer.company_id,
                          customer_id=customer.id,
                          ordered_at=fake.date_time_between("-1y"))
            s.add(order)
            s.flush()
            for _ in range(random.randint(1, 4)):
                p = random.choice(company_products[customer.company_id])
                s.add(OrderLine(order_id=order.id, product_id=p.id,
                                quantity=random.randint(1, 10),
                                unit_price=catalog[(customer.company_id, p.id)]))

        s.commit()
    print(f"seeded {N_ORDERS} orders, {N_COMPANIES} companies, {N_CUSTOMERS} customers, {N_SUPPLIERS} suppliers, {N_PRODUCTS} products")


if __name__ == "__main__":
    main()