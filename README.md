# Pizza Mamma Mia System


## Usage:
1. Run `pip install -r requirements.txt`
2. run `load_drom_sql.py`
3. Run `main_app.py`

## Key features
- Pizza prices calculated dynamically from ingredients (rounded to 2 dp).
- Discounts:
  - Birthday: 1 free cheapest pizza from the order + 1 free cheapest drink.
  - Loyalty: 10% off after customer has bought 10 pizzas (tracked over time).
  - One-time discount codes (single-use tracked).
- Delivery:
  - Delivery personnel assigned to postcode areas.
  - Orders assigned to delivery person by customer's postcode.
  - Delivery person cooldown (30 minutes after a delivery).
  - Delivery status tracked and visible.
- Business views (PizzaMenu, CustomerLoyalty, etc.) provide calculated/aggregated data.