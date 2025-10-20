"""
Load sample data into the database using SQLAlchemy ORM
"""
from main import app, db
from ORM.Customer import Customer
from ORM.Pizza import Pizza
from ORM.Product import Product
from ORM.Ingredient import Ingredient
from ORM.PizzaIngredient import PizzaIngredient
from decimal import Decimal

def load_sample_data():
    """Load sample data using SQLAlchemy ORM"""
    
    with app.app_context():
        print("Loading sample data...")
        
        # Clear existing data
        db.drop_all()
        db.create_all()
        print("Tables created")
        
        # Add Ingredients
        ingredients_data = [
            # Base ingredients
            ('Tomato Sauce', 0.50, False, False),
            ('Mozzarella Cheese', 1.20, False, True),
            ('Olive Oil', 0.30, False, False),
            ('Dough', 0.40, False, False),
            # Vegetables
            ('Mushrooms', 0.80, False, False),
            ('Bell Peppers', 0.60, False, False),
            ('Onions', 0.40, False, False),
            ('Tomatoes', 0.50, False, False),
            ('Olives', 0.70, False, False),
            ('Spinach', 0.60, False, False),
            ('Arugula', 0.70, False, False),
            ('Basil', 0.40, False, False),
            ('Garlic', 0.30, False, False),
            ('Jalapeños', 0.60, False, False),
            ('Pineapple', 0.80, False, False),
            # Meats
            ('Pepperoni', 1.50, True, True),
            ('Italian Sausage', 1.40, True, True),
            ('Ham', 1.30, True, True),
            ('Bacon', 1.60, True, True),
            ('Chicken', 1.80, True, True),
            ('Beef', 2.00, True, True),
            ('Anchovies', 1.90, True, True),
            # Cheese varieties
            ('Parmesan', 1.50, False, True),
            ('Gorgonzola', 1.70, False, True),
            ('Ricotta', 1.30, False, True),
            ('Feta', 1.40, False, True),
        ]
        
        for name, cost, is_meat, is_animal_prod in ingredients_data:
            ingredient = Ingredient(
                name=name,
                cost=Decimal(str(cost)),
                is_meat=is_meat,
                is_animal_prod=is_animal_prod
            )
            db.session.add(ingredient)
        
        db.session.commit()
        print(f"Added {len(ingredients_data)} ingredients")
        
        # Add Pizzas
        pizzas_data = [
            ('Margherita', 8.99, True, False),
            ('Pepperoni Classic', 10.99, False, False),
            ('Vegetarian Supreme', 11.99, True, False),
            ('Hawaiian', 10.99, False, False),
            ('BBQ Chicken', 12.99, False, False),
            ('Meat Lovers', 13.99, False, False),
            ('Four Cheese', 11.99, True, False),
            ('Mediterranean', 11.99, True, False),
            ('Spicy Diavola', 11.99, False, False),
            ('Mushroom Truffle', 12.99, True, False),
        ]
        
        for name, price, is_veg, is_vegan in pizzas_data:
            pizza = Pizza(
                name=name,
                price=Decimal(str(price)),
                is_vegetarian=is_veg,
                is_vegan=is_vegan,
                active=True
            )
            db.session.add(pizza)
        
        db.session.commit()
        print(f"Added {len(pizzas_data)} pizzas")
        
        # Add Pizza-Ingredient relationships
        # Get all ingredients and pizzas
        ingredients = {i.name: i for i in Ingredient.query.all()}
        pizzas = {p.name: p for p in Pizza.query.all()}
        
        # Pizza ingredient recipes
        recipes = {
            'Margherita': [
                ('Tomato Sauce', 100),
                ('Mozzarella Cheese', 150),
                ('Olive Oil', 10),
                ('Dough', 250),
                ('Basil', 5),
            ],
            'Pepperoni Classic': [
                ('Tomato Sauce', 100),
                ('Mozzarella Cheese', 150),
                ('Dough', 250),
                ('Pepperoni', 80),
            ],
            'Vegetarian Supreme': [
                ('Tomato Sauce', 100),
                ('Mozzarella Cheese', 150),
                ('Dough', 250),
                ('Mushrooms', 60),
                ('Bell Peppers', 50),
                ('Onions', 40),
                ('Tomatoes', 50),
                ('Olives', 30),
            ],
            'Hawaiian': [
                ('Tomato Sauce', 100),
                ('Mozzarella Cheese', 150),
                ('Dough', 250),
                ('Ham', 70),
                ('Pineapple', 80),
            ],
            'BBQ Chicken': [
                ('Mozzarella Cheese', 150),
                ('Dough', 250),
                ('Chicken', 100),
                ('Onions', 40),
                ('Bell Peppers', 50),
            ],
            'Meat Lovers': [
                ('Tomato Sauce', 100),
                ('Mozzarella Cheese', 150),
                ('Dough', 250),
                ('Pepperoni', 60),
                ('Italian Sausage', 60),
                ('Bacon', 50),
                ('Beef', 50),
            ],
            'Four Cheese': [
                ('Tomato Sauce', 80),
                ('Mozzarella Cheese', 100),
                ('Dough', 250),
                ('Parmesan', 50),
                ('Gorgonzola', 50),
                ('Ricotta', 50),
            ],
            'Mediterranean': [
                ('Tomato Sauce', 100),
                ('Mozzarella Cheese', 120),
                ('Dough', 250),
                ('Feta', 60),
                ('Olives', 40),
                ('Tomatoes', 50),
                ('Spinach', 40),
                ('Garlic', 10),
            ],
            'Spicy Diavola': [
                ('Tomato Sauce', 100),
                ('Mozzarella Cheese', 150),
                ('Dough', 250),
                ('Pepperoni', 80),
                ('Jalapeños', 40),
                ('Italian Sausage', 60),
            ],
            'Mushroom Truffle': [
                ('Olive Oil', 20),
                ('Mozzarella Cheese', 150),
                ('Dough', 250),
                ('Mushrooms', 100),
                ('Parmesan', 40),
                ('Arugula', 30),
                ('Garlic', 10),
            ],
        }
        
        for pizza_name, recipe in recipes.items():
            pizza = pizzas[pizza_name]
            for ingredient_name, grams in recipe:
                ingredient = ingredients[ingredient_name]
                pi = PizzaIngredient(
                    pizza_id=pizza.pizza_id,
                    ingredient_id=ingredient.ingredient_id,
                    grams=grams
                )
                db.session.add(pi)
        
        db.session.commit()
        print("Added pizza-ingredient relationships")
        
        # Add Products
        products_data = [
            ('Coca Cola (330ml)', 'beverage', 1.50, False),
            ('Fanta Orange (330ml)', 'beverage', 1.50, False),
            ('Sprite (330ml)', 'beverage', 1.50, False),
            ('Water (500ml)', 'beverage', 1.00, False),
            ('Orange Juice (250ml)', 'beverage', 2.00, False),
            ('Mozzarella Sticks (6 pieces)', 'snack', 3.50, False),
            ('Chicken Wings (8 pieces)', 'snack', 4.50, False),
            ('Caesar Salad', 'snack', 4.20, False),
            ('Tiramisu (slice)', 'snack', 3.80, False),
            ('Chocolate Brownie', 'snack', 3.20, False),
            ('Panna Cotta', 'snack', 3.50, False),
            ('Gelato (2 scoops)', 'snack', 3.00, False),
            ('Cheesecake (slice)', 'snack', 4.00, False),
        ]
        
        for name, category, cost, active in products_data:
            product = Product(
                name=name,
                category=category,
                cost=Decimal(str(cost)),
                active=active
            )
            db.session.add(product)
        
        db.session.commit()
        print(f"Added {len(products_data)} products")
        
        print("\n✅ Sample data loaded successfully!")
        
        # Verify
        print(f"\nDatabase contents:")
        print(f"  - Ingredients: {Ingredient.query.count()}")
        print(f"  - Pizzas: {Pizza.query.count()}")
        print(f"  - Products: {Product.query.count()}")
        print(f"  - Pizza-Ingredient relationships: {PizzaIngredient.query.count()}")
        
        # Show sample pizzas
        print(f"\n Sample pizzas:")
        for pizza in Pizza.query.limit(3).all():
            veg_status = "Vegan" if pizza.is_vegan else ("Vegetarian" if pizza.is_vegetarian else "Contains meat")
            print(f"  - {pizza.name}: €{pizza.price} ({veg_status})")

if __name__ == '__main__':
    load_sample_data()
