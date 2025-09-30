class StaffService:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_undelivered_orders(self):
        # TODO: Show pending deliveries
        pass
    
    def get_top_pizzas(self, days=30):
        # TODO: Top 3 pizzas last month
        pass
    
    def get_earnings_by_gender(self):
        # TODO: Earnings report by gender
        pass
    
    def get_earnings_by_age(self):
        # TODO: Earnings report by age group
        pass
    
    def get_earnings_by_postcode(self):
        # TODO: Earnings report by postal code
        pass
    
    def add_customer(self, customer_data):
        # TODO: Add new customer
        pass
    
    def add_discount_code(self, code, discount_percent):
        # TODO: Create new discount code
        pass