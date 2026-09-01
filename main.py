import pandas as pd

products = pd.read_csv("data/insurance_products.csv")
customers = pd.read_csv("data/customers.csv")

print("Insurance Policies")
print(products)

print("\nCustomers")
print(customers)