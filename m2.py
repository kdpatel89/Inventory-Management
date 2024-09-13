from datetime import date

import mysql.connector


class InventoryManagement:
    
    def __init__(self):
        self.mydb = mysql.connector.connect(
            database="inventory",
            user="root",
            password="",
            host="localhost",
        )
        self.mycursor = self.mydb.cursor()
        self.main_menu()

    def main_menu(self):
        while True:
            print("\nWelcome to Sughatika")
            print("Enter 1 for adding a new product")
            print("Enter 2 for adding an order")
            print("Enter 3 for checking stock")
            print("Enter 4 for adding stock")
            print("Enter 5 for checking orders")
            print("Enter 6 for checking pending orders")
            print("Enter 7 for completing an order")
            print("Enter 8 for Exit")
            
            try:
                input_value = int(input())
                if input_value < 1 or input_value > 8:
                    raise ValueError("Enter a valid choice")
            except ValueError as e:
                print(e)
                continue
            
            if input_value == 1:
                self.register_product()
            elif input_value == 2:
                self.add_order()
            elif input_value == 3:
                self.check_stock()
            elif input_value == 4:
                self.add_stock()
            elif input_value == 5:
                self.check_order_status()
            elif input_value == 6:
                self.check_pending_orders()
            elif input_value == 7:
                self.complete_order()
            elif input_value == 8:
                break

    def register_product(self):
        print("Enter product's Model number")
        model_no = input().upper()
        if not self.check_model_no(model_no):
            type_input = input("Enter product type: ").upper()
            while True:
                try:
                    pieces_input = int(input("Enter ready pieces: "))
                    if pieces_input < 0:
                        raise ValueError("Enter a valid number")
                    break
                except ValueError as e:
                    print(e)
            sql_query = "INSERT INTO product (model_no, product_type, stock) VALUES (%s, %s, %s)"
            self.mycursor.execute(sql_query, (model_no, type_input, pieces_input))
            self.mydb.commit()
            print("Product registered successfully")
        else:
            print('That product already exists')

    def add_order(self):
        model_no = input("Enter model_no: ").upper()
        if self.check_model_no(model_no):
            while True:
                try:
                    quantity = int(input("Enter quantity: "))
                    if quantity <= 0:
                        raise ValueError("Enter a valid quantity")
                    break
                except ValueError as e:
                    print(e)
            today = date.today()
            status = "PENDING"
            order_id = self.get_order_id()
            sql_query = "INSERT INTO orders (order_id, model_no, order_date, order_status, quantity) VALUES (%s, %s, %s, %s, %s)"
            self.mycursor.execute(sql_query, (order_id, model_no, today, status, quantity))
            self.mydb.commit()
            print("Order added successfully")
        else:
            print("The Product does not exist.")

    def check_stock(self):
        print("Enter product's Model number whose stock you want to check")
        model_no = input().upper()
        if self.check_model_no(model_no):
            self.mycursor.execute("SELECT stock FROM product WHERE model_no = %s", (model_no,))
            myresult = self.mycursor.fetchone()
            print(f"In Stock: {myresult[0]}")
        else:
            print("That product doesn't exist")

    def add_stock(self):
        print("Enter product's Model number whose stock you want to add")
        model_no = input().upper()
        if self.check_model_no(model_no):
            while True:
                try:
                    quantity = int(input("Enter quantity of production: "))
                    if quantity <= 0:
                        raise ValueError("Enter a valid quantity")
                    break
                except ValueError as e:
                    print(e)
            self.mycursor.execute("UPDATE product SET stock = stock + %s WHERE model_no = %s", (quantity, model_no))
            self.mydb.commit()
            print("Stock updated successfully")
        else:
            print("That product doesn't exist")

    def check_order_status(self):
        try:
            self.mycursor.execute("SELECT * FROM orders")
            myresult = self.mycursor.fetchall()
            self.print_table(myresult)
        except mysql.connector.Error as e:
            print(f"Error: {e}")

    def check_pending_orders(self):
        try:
            self.mycursor.execute("SELECT * FROM orders WHERE order_status = 'PENDING'")
            myresult = self.mycursor.fetchall()
            self.print_table(myresult)
        except mysql.connector.Error as e:
            print(f"Error: {e}")

    def complete_order(self):
        try:
            self.mycursor.execute("SELECT * FROM orders WHERE order_status = 'PENDING'")
            myresult = self.mycursor.fetchall()
            if not myresult:
                print("No pending orders found.")
                return
            self.print_table(myresult)
            inp = int(input("Enter order_id which you want to complete: "))
            if any(x[0] == inp for x in myresult):
                self.mycursor.execute("SELECT quantity, model_no FROM orders WHERE order_id = %s", (inp,))
                myresult = self.mycursor.fetchone()
                model_no, quantity = myresult[1], myresult[0]
                self.mycursor.execute("SELECT stock FROM product WHERE model_no = %s", (model_no,))
                myresult = self.mycursor.fetchone()
                available_stock = myresult[0]
                if available_stock >= quantity:
                    self.mycursor.execute("UPDATE product SET stock = stock - %s WHERE model_no = %s", (quantity, model_no))
                    self.mydb.commit()
                    self.mycursor.execute("UPDATE orders SET order_status = 'COMPLETED', completed_date = %s WHERE order_id = %s", (date.today(), inp))
                    self.mydb.commit()
                    print("Order completed successfully")
                else:
                    print("You need to produce more stock")
            else:
                print("No such order found")
        except mysql.connector.Error as e:
            print(f"Error: {e}")

    def check_model_no(self, model_no):
        try:
            self.mycursor.execute("SELECT model_no FROM product WHERE model_no = %s", (model_no,))
            myresult = self.mycursor.fetchone()
            return myresult is not None
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return False

    def get_order_id(self):
        try:
            self.mycursor.execute("SELECT MAX(order_id) FROM orders")
            myresult = self.mycursor.fetchone()
            return int(myresult[0]) + 1 if myresult[0] is not None else 1
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return 1

    def print_table(self, data):
        if not data:
            print("No data found.")
            return
        
        # Calculate column widths
        col_widths = [max(len(str(row[i])) for row in data) for i in range(len(data[0]))]
        col_widths = [max(width, len(name)) for width, name in zip(col_widths, ["Order ID", "Model No", "Order Date", "Quantity", "Status"])]

        # Print header
        header = f"{'Order ID':<{col_widths[0]}} {'Model No':<{col_widths[1]}} {'Order Date':<{col_widths[2]}} {'Quantity':<{col_widths[3]}} {'Status':<{col_widths[4]}}"
        print(header)
        print('-' * len(header))

        # Print rows
        for row in data:
            print(f"{row[0]:<{col_widths[0]}} {row[1]:<{col_widths[1]}} {row[2]:<{col_widths[2]}} {row[4]:<{col_widths[3]}} {row[3]:<{col_widths[4]}}")

if __name__ == "__main__":
    InventoryManagement()
