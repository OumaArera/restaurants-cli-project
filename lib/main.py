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
        cursor.execute("SELECT * FROM reviews WHERE restaurant_id = ?", (self.id,))
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
        cursor.execute("INSERT INTO restaurants (name, price) VALUES (?, ?)", (self.name, self.price))
        self.id = cursor.lastrowid
    
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


class Review:
    def __init__(self, restaurant, customer, star_rating):
        self.restaurant = restaurant
        self.customer = customer
        self.star_rating = star_rating

    def save(self):
        cursor.execute("INSERT INTO reviews (restaurant_id, customer_id, star_rating) VALUES (?, ?, ?)",
                       (self.restaurant.id, self.customer.id, self.star_rating))

    def customer(self):
        return self.customer
    
    def restaurant(self):
        return self.restaurant
    
def sample_data():
    # Add restaurants
    restaurant_a = Restaurant("Rusinga", 400)
    restaurant_a.save()
    restaurant_b = Restaurant("Mbita", 400)
    restaurant_b.save()
    restaurant_c = Restaurant("Sindo", 400)
    restaurant_c.save()

    # Add customers
    customer_a = Customer("Judy", "Atieno")
    customer_a.save()
    customer_b = Customer("Sharon", "Anyango")
    customer_b.save()
    customer_c = Customer("Rambung'", "Fee")
    customer_c.save()

    # Add reviews
    review_a = Review(restaurant_a, customer_a, 5)
    review_a.save()
    review_b = Review(restaurant_b, customer_b, 5)
    review_b.save()
    review_c = Review(restaurant_c, customer_c, 4)
    review_c.save()

def close_connection():
    conn.close()

if __name__ == "__main__":
    sample_data()
    conn.commit()
    close_connection()

