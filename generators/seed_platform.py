import random

from faker import Faker
from sqlalchemy.orm import Session

from dwh.db.models import Base, Company, Customer, Order, OrderLine, Product, engine

fake = Faker("es_AR")
Faker.seed(42)
random.seed(42)

N_COMPANIES, N_SUPPLIERS, N_CUSTOMERS, N_PRODUCTS, N_ORDERS = 20, 5, 200, 100, 1000


def cuit() -> str:
    return f"{random.randint(20, 34)}-{random.randint(10**7, 10**8 - 1)}-{random.randint(0, 9)}"


def main() -> None:
    eng = engine()
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)

    with Session(eng) as s:
        suppliers = [Company(cuit=cuit(), name=fake.company(), is_supplier=True)
                     for _ in range(N_SUPPLIERS)]
        buyers = [Company(cuit=cuit(), name=fake.company()) for _ in range(N_COMPANIES)]
        s.add_all(suppliers + buyers)
        s.flush()

        products = [
            Product(supplier_id=random.choice(suppliers).id,
                    name=fake.word().capitalize(),
                    default_price=round(random.uniform(10, 500), 2))
            for _ in range(N_PRODUCTS)
        ]
        customers = [
            Customer(company_id=random.choice(buyers).id,
                     document_number=str(fake.random_number(8, True)),
                     full_name=fake.name(),
                     date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80))
            for _ in range(N_CUSTOMERS)
        ]
        s.add_all(products + customers)
        s.flush()

        for _ in range(N_ORDERS):
            customer = random.choice(customers)
            order = Order(company_id=customer.company_id,
                          customer_id=customer.id,
                          ordered_at=fake.date_time_between("-1y"))
            s.add(order)
            s.flush()
            for _ in range(random.randint(1, 4)):
                p = random.choice(products)
                s.add(OrderLine(order_id=order.id, product_id=p.id,
                                quantity=random.randint(1, 10),
                                unit_price=p.default_price))

        s.commit()
    print(f"seeded {N_ORDERS} orders")


if __name__ == "__main__":
    main()