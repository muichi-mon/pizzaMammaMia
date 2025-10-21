-- pizas with prices dinamically calculated from ingredients
CREATE VIEW IF NOT EXISTS PizzaMenu AS 
SELECT 
    p.pizza_id, 
    p.name, 
    p.active, 
    SUM(i.cost * pi.grams / 100) AS ingredient_cost,
    ROUND(SUM(i.cost * pi.grams / 100) * 1.4 * 1.09, 2) AS price,
    CASE WHEN SUM(CASE WHEN i.is_meat = TRUE THEN 1 ELSE 0 END) = 0 THEN TRUE ELSE FALSE END AS is_vegetarian,
    CASE WHEN SUM(CASE WHEN i.is_meat = TRUE THEN 1 ELSE 0 END) = 0 
              AND SUM(CASE WHEN i.is_animal_prod = TRUE THEN 1 ELSE 0 END) = 0 THEN TRUE ELSE FALSE END AS is_vegan
FROM Pizza p
JOIN PizzaIngredient pi ON p.pizza_id = pi.pizza_id
JOIN Ingredient i ON pi.ingredient_id = i.ingredient_id
GROUP BY p.pizza_id, p.name, p.active;



-- drinks and stuff
CREATE VIEW IF NOT EXISTS ProductMenu AS
SELECT 
    product_id, 
    name, 
    category, 
    cost AS cost_per_item, 
    ROUND(cost * 1.4 * 1.09, 2) AS price,
    is_alcohol
FROM Product
WHERE active = TRUE;



--loyalty discounts: 10% off after every 10 pizzas
CREATE VIEW IF NOT EXISTS CustomerLoyalty AS
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    COALESCE(SUM(op.quantity), 0) AS total_pizzas_bought,
    FLOOR(COALESCE(SUM(op.quantity), 0) / 10) AS loyalty_discounts_earned,
    CASE 
        WHEN COALESCE(SUM(op.quantity), 0) >= 10 THEN TRUE 
        ELSE FALSE 
    END AS eligible_for_loyalty_discount,
    COALESCE(SUM(op.quantity), 0) % 10 AS pizzas_until_next_discount
FROM Customer c
LEFT JOIN Orders o ON c.customer_id = o.customer_id AND o.cancelled_at IS NULL
LEFT JOIN OrderPizza op ON o.order_id = op.order_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email;



--Bday discounts
CREATE VIEW IF NOT EXISTS BirthdayCustomers AS
SELECT customer_id,first_name,last_name,email,birth_date,postcode
FROM Customer
WHERE DATE_FORMAT(birth_date, '%m-%d') = DATE_FORMAT(CURDATE(), '%m-%d');



-- Simplified: Get all available delivery personnel
CREATE VIEW IF NOT EXISTS AvailableDeliveryPersonnel AS
SELECT 
    delivery_person_id,
    full_name,
    phone
FROM DeliveryPerson;
-- TODO: Add last_delivery_at field to DeliveryPerson table and filter by:
-- WHERE last_delivery_at IS NULL OR last_delivery_at <= DATE_SUB(NOW(), INTERVAL 30 MINUTE)


-- Undelivered Orders View
CREATE VIEW IF NOT EXISTS UndeliveredOrders AS
SELECT 
    o.order_id,
    o.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.email,
    o.order_time,
    o.status,
    o.postcode_snapshot,
    o.total_amount,
    o.delivery_person_id,
    CASE 
        WHEN o.delivery_person_id IS NOT NULL THEN dp.full_name
        ELSE 'Not Assigned'
    END AS delivery_person_name
FROM Orders o
JOIN Customer c ON o.customer_id = c.customer_id
LEFT JOIN DeliveryPerson dp ON o.delivery_person_id = dp.delivery_person_id
WHERE o.delivered_at IS NULL 
  AND o.cancelled_at IS NULL
ORDER BY o.order_time;

-- Top 3 Pizzas Last Month
CREATE VIEW IF NOT EXISTS TopPizzasLastMonth AS
SELECT 
    p.name AS pizza_name,
    SUM(op.quantity) AS total_sold,
    ROUND(SUM(op.quantity * op.unit_price), 2) AS total_revenue
FROM OrderPizza op
JOIN Pizza p ON op.pizza_id = p.pizza_id
JOIN Orders o ON op.order_id = o.order_id
WHERE o.order_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND o.cancelled_at IS NULL
GROUP BY p.pizza_id, p.name
ORDER BY total_sold DESC
LIMIT 3;

-- Earnings by Postcode (last month)
CREATE VIEW IF NOT EXISTS EarningsByPostcode AS
SELECT 
    o.postcode_snapshot AS postcode,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_earnings,
    ROUND(AVG(o.total_amount), 2) AS average_order_value
FROM Orders o
WHERE o.order_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND o.cancelled_at IS NULL
GROUP BY o.postcode_snapshot
ORDER BY total_earnings DESC;

-- Earnings by Age Group (last month)
CREATE VIEW IF NOT EXISTS EarningsByAgeGroup AS
SELECT 
    CASE 
        WHEN TIMESTAMPDIFF(YEAR, c.birth_date, CURDATE()) < 25 THEN '18-24'
        WHEN TIMESTAMPDIFF(YEAR, c.birth_date, CURDATE()) < 35 THEN '25-34'
        WHEN TIMESTAMPDIFF(YEAR, c.birth_date, CURDATE()) < 45 THEN '35-44'
        WHEN TIMESTAMPDIFF(YEAR, c.birth_date, CURDATE()) < 55 THEN '45-54'
        ELSE '55+'
    END AS age_group,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_earnings,
    ROUND(AVG(o.total_amount), 2) AS average_order_value
FROM Orders o
JOIN Customer c ON o.customer_id = c.customer_id
WHERE o.order_time >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
  AND o.cancelled_at IS NULL
GROUP BY age_group
ORDER BY total_earnings DESC;


-- Complete Order Details with Items
CREATE VIEW IF NOT EXISTS OrderDetails AS
SELECT 
    o.order_id,
    o.customer_id,
    CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
    c.email,
    o.order_time,
    o.status,
    o.total_amount,
    o.applied_discount,
    o.discount_code,
    o.postcode_snapshot,
    o.delivery_person_id,
    CASE 
        WHEN o.delivery_person_id IS NOT NULL THEN dp.full_name
        ELSE 'Not Assigned'
    END AS delivery_person_name,
    o.delivered_at,
    o.cancelled_at
FROM Orders o
JOIN Customer c ON o.customer_id = c.customer_id
LEFT JOIN DeliveryPerson dp ON o.delivery_person_id = dp.delivery_person_id;