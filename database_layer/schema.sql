--customer table
CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(80) NOT NULL,
    last_name VARCHAR(80) NOT NULL,
    birth_date DATE NOT NULL,
    postcode VARCHAR(20) NOT NULL,
    
    -- Constraints
    CONSTRAINT chk_birth_date CHECK (birth_date <= CURDATE()),
    CONSTRAINT chk_postcode CHECK (postcode REGEXP '^[0-9]{5}$')
);

--ingredient table
CREATE TABLE Ingredient (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    cost DECIMAL(8,2) NOT NULL,
    is_meat BOOL DEFAULT FALSE,
    is_animal_prod BOOL DEFAULT FALSE,
    
    -- Constraints
    CONSTRAINT chk_cost CHECK (cost > 0)
);

--pizza table
CREATE TABLE Pizza (
    pizza_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    active BOOL DEFAULT TRUE
);

--pizza-ingredient table
CREATE TABLE PizzaIngredient (
    pizza_id INT NOT NULL,
    ingredient_id INT NOT NULL,
    grams INT NOT NULL,
    
    PRIMARY KEY (pizza_id, ingredient_id),
    
    FOREIGN KEY (pizza_id) REFERENCES Pizza(pizza_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredient(ingredient_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_grams CHECK (grams > 0)
);

--delivery person table
CREATE TABLE DeliveryPerson (
    delivery_person_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    phone VARCHAR(30) NOT NULL UNIQUE
);

--discount code table
CREATE TABLE DiscountCode (
    code VARCHAR(32) PRIMARY KEY,
    description VARCHAR(200),
    percent_off DECIMAL(5,2),
    amount_off DECIMAL(8,2),
    single_use BOOL DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT chk_discount_values CHECK (
        (percent_off IS NOT NULL AND amount_off IS NULL) OR 
        (percent_off IS NULL AND amount_off IS NOT NULL)
    ),
    CONSTRAINT chk_percent_range CHECK (percent_off IS NULL OR (percent_off > 0 AND percent_off <= 100)),
    CONSTRAINT chk_amount_positive CHECK (amount_off IS NULL OR amount_off > 0)
);

--order table
CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    discount_code VARCHAR(32),
    delivery_person_id INT,
    postcode_snapshot VARCHAR(20) NOT NULL,
    delivered_at DATETIME,
    cancelled_at DATETIME,
    
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (discount_code) REFERENCES DiscountCode(code) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (delivery_person_id) REFERENCES DeliveryPerson(delivery_person_id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_status CHECK (status IN ('pending', 'preparing', 'out_for_delivery', 'delivered', 'cancelled')),
    CONSTRAINT chk_delivered_after_order CHECK (delivered_at IS NULL OR delivered_at >= order_time),
    CONSTRAINT chk_cancelled_after_order CHECK (cancelled_at IS NULL OR cancelled_at >= order_time)
);

--order-pizza table
CREATE TABLE OrderPizza (
    order_id INT NOT NULL,
    pizza_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    
    PRIMARY KEY (order_id, pizza_id),
    
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (pizza_id) REFERENCES Pizza(pizza_id) 
        ON DELETE RESTRICT ON UPDATE CASCADE,
    
    -- Constraints
    CONSTRAINT chk_quantity CHECK (quantity > 0)
);

--indexes for performance optimization
CREATE INDEX idx_customer_postcode ON Customer(postcode);
CREATE INDEX idx_customer_birth_date ON Customer(birth_date);
CREATE INDEX idx_orders_customer ON Orders(customer_id);
CREATE INDEX idx_orders_status ON Orders(status);
CREATE INDEX idx_orders_time ON Orders(order_time);
CREATE INDEX idx_orders_delivery_person ON Orders(delivery_person_id);
CREATE INDEX idx_ingredient_meat ON Ingredient(is_meat);
CREATE INDEX idx_pizza_active ON Pizza(active);