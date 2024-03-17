import sqlite3

# Establish connection to SQLite database
conn = sqlite3.connect('restaurant_reviews.db')
cursor = conn.cursor()

# Create restaurants table
cursor.execute('''
CREATE TABLE IF NOT EXISTS restaurants (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price INTEGER
)
''')

# Create customers table
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT
)
''')

# Create reviews table
cursor.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY,
    restaurant_id INTEGER,
    customer_id INTEGER,
    star_rating INTEGER,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
''')



class Restaurant:
    def __init__(self, name, price):
        self.name = name
        self.price = price
    
    # Prints restaurant's first name and last name
    def __str__(self):
        return f"Name: {self.name}, Price: {self.price}."
    
    # Select all reviews on the restaurant
    def reviews(self):
        cursor.execute("""SELECT * FROM reviews WHERE restaurant_id = ?""", (self.id,))
        return cursor.fetchall()
    
    # Seects all customers who gave reviews on restaurant
    def customer(self):
        cursor.execute("""
        SELECT * FROM customers
        INNER JOIN reviews ON customers.id = reviews.customer_id
        WHERE reviews.restaurant_id = ?
        """, (self.id,))
        return cursor.fetchall()
    
    # Persist data into the db
    def save(self):
        cursor.execute("""INSERT INTO restaurants (name, price) VALUES (?, ?)""", (self.name, self.price))
        self.id = cursor.lastrowid

    # Selects the fanciest restaurant since it has the highest restaurant
    @classmethod
    def fanciest(cls):
        cursor.execute("""SELECT * FROM restaurants ORDER BY price DESC LIMIT 1""")
        data = cursor.fetchone()

        if data:
            fanciest_restaurant = cls(data[1], data[2])
            fanciest_restaurant.id = data[0]
            return fanciest_restaurant
        else:
            return None
    
    # Returns a list of detailed review
    def all_reviews(self):
        cursor.execute("""SELECT * FROM reviews WHERE restaurant_id = ?""", (self.id,))
        all_reviews_data = cursor.fetchall()

        reviews_list = []

        # Iterate through the fetched data
        for review in all_reviews_data:

            cursor.execute('''SELECT * FROM restaurants WHERE id = ?''', (review[1]))
            restaurant_ = cursor.fetchall()

            cursor.execute('''SELECT * FROM customers WHERE id = ?''', (review[2]))
            customer_ = cursor.fetchall()

            reviews_list.append(f"Review for {restaurant_[1]} by {customer_[1]} {customer_[2]}: {review[3]} stars.")

        return reviews_list
    
    # Test method
    @classmethod
    def from_input(cls):
        name = input("Enter the restaurant's name: ")
        price = int(input("Enter the restaurant's price: "))
        return cls(name, price)



class Customer: 
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    # returns full name
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    # Prints customer's names(details)
    def __str__(self):
        return f"Customer: {self.full_name}."
    
    # Fetches the details of reviews of a particular customer
    def reviews(self):
        cursor.execute('''
        SELECT * FROM reviews WHERE customer_id = ?
        ''', (self.id,))
        return cursor.fetchall()
    
    # Selects all reviews that a particular customer made to restaurants
    def restaurants(self):
        cursor.execute('''
        SELECT * FROM restaurants
        INNER JOIN reviews ON restaurants.id = reviews.restaurant_id
        WHERE customer_id = ?
        ''', (self.id,))
        return cursor.fetchall()
    
    # Add data to the db
    def save(self):
        cursor.execute("""INSERT INTO customers (first_name, last_name) VALUES (?, ?)""", (self.first_name, self.last_name))
        self.id = cursor.lastrowid

    # Fetches details of customer's favorite restaurant based on review ratings
    def favorite_restaurant(self):
        cursor.execute("""SELECT * FROM reviews WHERE customer_id = ?""", (self.id,))
        reviews = cursor.fetchall()

        maximum_star_rating = 0
        favorite_restaurant = None

        for review in reviews:
            # Column 3 has the reviews rating
            if review[3] > maximum_star_rating:
                maximum_star_rating = review[3]
                favorite_restaurant_id = review[1]  #index 1 has restaurant ids

        # When there is a favorite restaurant
        if favorite_restaurant:
            cursor.execute("""SELECT * FROM restaurants WHERE id = ?""", (favorite_restaurant_id,))
            favorite_restaurant_details = cursor.fetchone()
            favorite_restaurant = Restaurant(favorite_restaurant_details[1], favorite_restaurant_details[2])
            favorite_restaurant.id = favorite_restaurant_details[0]

        return favorite_restaurant
    
    # Add customer's review to review db.
    def add_review(self, restaurant, rating):

        new_review = Review(restaurant, self, rating)
        new_review.save()

    # Deletes a review from the review db when both customer id and restaurant id are truthy.
    def delete_reviews(self, restaurant):
        cursor.execute("""DELETE FROM reviews WHERE customer_id = ? AND restaurant_id = ?""", (self.id, restaurant.id))

    # Run application in CLI
    @classmethod
    def from_input(cls):
        first_name = input("Enter customer's first name: ")
        last_name = input("Enter customer's last name: ")
        return cls(first_name, last_name)


class Review:
    def __init__(self, restaurant, customer, star_rating):
        self.restaurant = restaurant
        self.customer = customer
        self.star_rating = star_rating

    def save(self):
        cursor.execute("INSERT INTO reviews (restaurant_id, customer_id, star_rating) VALUES (?, ?, ?)",
                       (self.restaurant.id, self.customer.id, self.star_rating))
    
    # Return full review of a customer
    def full_review(self):
        restaurant_name = self.restaurant.name
        customer_name = self.customer.full_name()
        star = self.star_rating

        return f"Review for {restaurant_name} by {customer_name}: {star} stars."
    
    # Run application in CLI
    @classmethod
    def from_input(cls, restaurant, customer):
        star_rating = int(input("Enter star rating for the review: "))
        return cls(restaurant, customer, star_rating)

# Function creates a restaurant 
def create_restaurant():
    restaurant = Restaurant.from_input()
    restaurant.save()
    print(f"Restaurant '{restaurant.name}' created successfully.")

# Function creates a customer
def create_customer():
    customer = Customer.from_input()
    customer.save()
    print(f"Customer '{customer.full_name()}' created successfully.")

# Fetches data of all restaurants to assist in rating
def select_restaurant():
    cursor.execute("SELECT id, name FROM restaurants")
    restaurants = cursor.fetchall()
    print("Available Restaurants:")
    for restaurant in restaurants:
        print(f"{restaurant[0]}. {restaurant[1]}")
    restaurant_id = int(input("Enter the ID of the restaurant: "))
    return restaurant_id

# Selects customer to enable review
def select_customer():
    cursor.execute("SELECT id, first_name, last_name FROM customers")
    customers = cursor.fetchall()
    print("Available Customers:")
    for customer in customers:
        print(f"{customer[0]}. {customer[1]} {customer[2]}")
    customer_id = int(input("Enter the ID of the customer: "))
    return customer_id

# Function creates a review
def create_review():
    restaurant_id = select_restaurant()
    customer_id = select_customer()
    restaurant = Restaurant("", 0)  
    customer = Customer("", "") 
    review = Review.from_input(restaurant, customer)
    review.restaurant.id = restaurant_id
    review.customer.id = customer_id
    review.save()
    print("Review added successfully.")

# run application on the CLI
def run_cli():
    while True:
        print("\nMenu:")
        print("1. Create Restaurant")
        print("2. Create Customer")
        print("3. Create Review")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            create_restaurant()
        elif choice == "2":
            create_customer()
        elif choice == "3":
            create_review()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    run_cli()
    conn.commit()
    conn.close()

