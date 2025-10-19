# ERD Design - Pizza Mamma Mia

## ✅ Completed ERD Implementation

### Entities & Relationships:

#### 1. **Customer**
- `customer_id` (PK, INT, AUTO_INCREMENT)
- `first_name` (VARCHAR(80), NOT NULL)
- `last_name` (VARCHAR(80), NOT NULL)
- `birth_date` (DATE, NOT NULL)
- `postcode` (VARCHAR(20), NOT NULL)

**Constraints:**
- Birth date must be in the past
- Postcode must be 5 digits

#### 2. **Ingredient**
- `ingredient_id` (PK, INT, AUTO_INCREMENT)
- `name` (VARCHAR(120), UNIQUE, NOT NULL)
- `cost` (DECIMAL(8,2), NOT NULL)
- `is_meat` (BOOL, DEFAULT FALSE)
- `is_animal_prod` (BOOL, DEFAULT FALSE)

**Constraints:**
- Cost must be > 0
- Name must be unique

#### 3. **Pizza**
- `pizza_id` (PK, INT, AUTO_INCREMENT)
- `name` (VARCHAR(120), UNIQUE, NOT NULL)
- `active` (BOOL, DEFAULT TRUE)

**Note:** NO price column - calculated dynamically from ingredients

#### 4. **PizzaIngredient** (Junction Table)
- `pizza_id` (FK → Pizza, PK)
- `ingredient_id` (FK → Ingredient, PK)
- `grams` (INT, NOT NULL)

**Relationship:** Many-to-Many between Pizza and Ingredient
**Constraints:** Grams must be > 0

#### 5. **DeliveryPerson**
- `delivery_person_id` (PK, INT, AUTO_INCREMENT)
- `full_name` (VARCHAR(120), NOT NULL)
- `phone` (VARCHAR(30), UNIQUE, NOT NULL)

#### 6. **DiscountCode**
- `code` (PK, VARCHAR(32))
- `description` (VARCHAR(200))
- `percent_off` (DECIMAL(5,2))
- `amount_off` (DECIMAL(8,2))
- `single_use` (BOOL, DEFAULT TRUE)

**Constraints:**
- Must have either percent_off OR amount_off (not both)
- Percent must be 0-100
- Amount must be > 0

#### 7. **Orders**
- `order_id` (PK, INT, AUTO_INCREMENT)
- `customer_id` (FK → Customer, NOT NULL)
- `order_time` (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- `status` (VARCHAR(20), DEFAULT 'pending')
- `discount_code` (FK → DiscountCode)
- `delivery_person_id` (FK → DeliveryPerson)
- `postcode_snapshot` (VARCHAR(20), NOT NULL)
- `delivered_at` (DATETIME)
- `cancelled_at` (DATETIME)

**Constraints:**
- Status must be: pending, preparing, out_for_delivery, delivered, cancelled
- Delivered_at must be >= order_time
- Cancelled_at must be >= order_time

#### 8. **OrderPizza** (Junction Table)
- `order_id` (FK → Orders, PK)
- `pizza_id` (FK → Pizza, PK)
- `quantity` (INT, DEFAULT 1)

**Relationship:** Many-to-Many between Orders and Pizza
**Constraints:** Quantity must be > 0

---

## Relationships Summary:

1. **Customer → Orders** (1:N)
   - One customer can place many orders

2. **Pizza ↔ Ingredient** (M:N via PizzaIngredient)
   - Pizzas contain multiple ingredients
   - Ingredients can be in multiple pizzas

3. **Orders ↔ Pizza** (M:N via OrderPizza)
   - Orders can contain multiple pizzas
   - Same pizza can appear in multiple orders

4. **DeliveryPerson → Orders** (1:N)
   - One delivery person can deliver many orders

5. **DiscountCode → Orders** (1:N)
   - One discount code can be used in multiple orders (if not single_use)

---

## Business Rules Enforced:

✅ No price stored in Pizza table (dynamic calculation)  
✅ Vegetarian detection via ingredient flags  
✅ Birth date validation  
✅ Postcode format validation  
✅ Ingredient cost must be positive  
✅ Order status workflow  
✅ Discount code single-use option  
✅ Temporal constraints (delivered/cancelled after order)