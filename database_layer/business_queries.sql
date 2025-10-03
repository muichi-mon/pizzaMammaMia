-- Business Queries for Pizza Mamma Mia
-- TODO: Write SQL queries for all business needs

-- TODO: Calculate pizza prices dynamically (ingredients + 40% margin + 9% VAT)
-- SELECT pizza_name, calculated_price FROM ...

-- TODO: Check customer loyalty (10+ pizzas = 10% discount)
-- SELECT customer_id, pizza_count FROM ...

-- TODO: Birthday discount eligibility
-- SELECT customer_id FROM customers WHERE birthday = CURDATE()

-- TODO: Assign delivery person by postcode
-- SELECT delivery_person_id FROM delivery_personnel WHERE postcode = ?

-- TODO: Check delivery availability (not busy for 30 mins)
-- SELECT * FROM delivery_personnel WHERE last_delivery < NOW() - INTERVAL 30 MINUTE

-- TODO: Top 3 pizzas last month
-- SELECT pizza_name, COUNT(*) FROM orders JOIN order_items ...

-- TODO: Earnings by demographics
-- SELECT gender, age_group, SUM(total) FROM ...

-- TODO: Undelivered orders
-- SELECT * FROM orders WHERE delivery_status != 'delivered'

-- TODO: Vegetarian/vegan check
-- SELECT pizza_name FROM pizzas WHERE NOT EXISTS (meat ingredients)