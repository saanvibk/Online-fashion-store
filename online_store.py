import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# --- Database Connection ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'newpassword@123',
    'database': 'Online_fashion_store'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --- Core Functions ---
def run_query(query, params=None, fetch=False):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        if fetch:
            result = cur.fetchall()
            cur.close()
            conn.close()
            return result
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# --- GUI Application ---
class FashionStoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛍️ Online Fashion Store Management")
        self.geometry("1000x700")
        self.configure(bg="#f8f9fa")

        title = tk.Label(self, text="Online Fashion Store Dashboard", font=("Helvetica", 20, "bold"), bg="#f8f9fa")
        title.pack(pady=10)

        tabs = ttk.Notebook(self)
        tabs.pack(expand=1, fill="both")

        # Tabs
        self.customer_tab = CustomerTab(tabs)
        self.product_tab = ProductTab(tabs)
        self.orders_tab = OrderTab(tabs)   # ✅ rename to match the payment-enabled order tab
        self.payment_tab = PaymentTab(tabs)  # ✅ new payment manual update tab
        self.view_tab = ViewTab(tabs)

        # Add all tabs to Notebook
        tabs.add(self.customer_tab, text="Customer")
        tabs.add(self.product_tab, text="Product")
        tabs.add(self.orders_tab, text="Orders + Payment")  # ✅ updated label
        tabs.add(self.payment_tab, text="Update Payment Status")  # ✅ new tab for procedure
        tabs.add(self.view_tab, text="View Data")

# --- Customer Tab ---
class CustomerTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        tk.Label(self, text="Add New Customer", font=("Helvetica", 14, "bold"), bg="white").pack(pady=10)

        form = tk.Frame(self, bg="white")
        form.pack(pady=5)

        tk.Label(form, text="Name:", bg="white").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(form, text="Email:", bg="white").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(form, text="Phone:", bg="white").grid(row=2, column=0, padx=5, pady=5)
        tk.Label(form, text="Password:", bg="white").grid(row=3, column=0, padx=5, pady=5)

        self.name = tk.Entry(form)
        self.email = tk.Entry(form)
        self.phone = tk.Entry(form)
        self.password = tk.Entry(form, show="*")

        self.name.grid(row=0, column=1)
        self.email.grid(row=1, column=1)
        self.phone.grid(row=2, column=1)
        self.password.grid(row=3, column=1)

        tk.Button(self, text="Add Customer", command=self.add_customer, bg="#007bff", fg="white").pack(pady=10)

    def add_customer(self):
        query = """
            INSERT INTO Customer (Name, Email, Phone, Password)
            VALUES (%s, %s, %s, %s)
        """
        params = (self.name.get(), self.email.get(), self.phone.get(), self.password.get())
        run_query(query, params)
        messagebox.showinfo("Success", "Customer added successfully! (Trigger auto-added RegDate)")

# --- Product Tab ---
class ProductTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        tk.Label(self, text="Add Product via Procedure", font=("Helvetica", 14, "bold"), bg="white").pack(pady=10)

        form = tk.Frame(self, bg="white")
        form.pack(pady=5)

        labels = ["Product Name:", "Description:", "Price:", "Stock:", "Brand:", "Category ID:"]
        self.entries = []

        for i, text in enumerate(labels):
            tk.Label(form, text=text, bg="white").grid(row=i, column=0, padx=5, pady=5)
            e = tk.Entry(form, width=40)
            e.grid(row=i, column=1, padx=5, pady=5)
            self.entries.append(e)

        tk.Button(self, text="Add Product", command=self.add_product, bg="#28a745", fg="white").pack(pady=10)

    def add_product(self):
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Unpack entry values
            name = self.entries[0].get()
            desc = self.entries[1].get()
            price = float(self.entries[2].get())
            stock = int(self.entries[3].get())
            brand = self.entries[4].get()
            catid = int(self.entries[5].get())

            cur.callproc("AddProduct", (name, desc, price, stock, brand, catid))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("Success", f"Product '{name}' added successfully via stored procedure!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# --- Order / Payment Tab ---

# --- View Data Tab ---
class ViewTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")
        tk.Label(self, text="Database Tables / Views", font=("Helvetica", 14, "bold"), bg="white").pack(pady=10)

        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Show Customers", command=lambda: self.show_data("Customer")).grid(row=0, column=0, padx=10, pady=5)
        tk.Button(btn_frame, text="Show Products", command=lambda: self.show_data("Product")).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(btn_frame, text="Show Orders", command=lambda: self.show_data("Orders")).grid(row=1, column=0, padx=10, pady=5)
        tk.Button(btn_frame, text="Show Payments", command=lambda: self.show_data("Payment")).grid(row=1, column=1, padx=10, pady=5)

        # 🔍 Filter for Orders by Customer ID
        filter_frame = tk.Frame(self, bg="white")
        filter_frame.pack(pady=8)

        tk.Label(filter_frame, text="Filter Orders by Customer ID:", bg="white", font=("Helvetica", 11)).grid(row=0, column=0, padx=5)
        self.filter_entry = tk.Entry(filter_frame, width=10, font=("Helvetica", 11))
        self.filter_entry.grid(row=0, column=1, padx=5)
        tk.Button(filter_frame, text="Filter Orders", command=self.filter_orders_by_customer,
                  bg="#17a2b8", fg="white", font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=8)

        # Treeview for displaying table data
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(expand=True, fill="both", pady=20, padx=20)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def show_data(self, table):
        """General data viewer for all tables"""
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            # Clear old data
            self.tree.delete(*self.tree.get_children())

            # Configure columns
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=120)

            # Insert rows
            for row in rows:
                self.tree.insert("", "end", values=row)

            cur.close()
            conn.close()

            if not rows:
                messagebox.showinfo("Info", f"No records found in {table} table.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def filter_orders_by_customer(self):
        """Filter the Orders table by CustomerID"""
        cust_id = self.filter_entry.get().strip()
        if not cust_id:
            messagebox.showwarning("Input Needed", "Please enter a valid Customer ID.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM Orders WHERE CustomerID = %s", (cust_id,))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            # Clear old data
            self.tree.delete(*self.tree.get_children())

            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=120)

            for row in rows:
                self.tree.insert("", "end", values=row)

            cur.close()
            conn.close()

            if not rows:
                messagebox.showinfo("No Results", f"No orders found for Customer ID {cust_id}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# payment page
class PaymentPage(tk.Toplevel):
    """Popup shown after placing an order to complete payment."""
    def __init__(self, parent, order_id, amount):
        super().__init__(parent)
        self.title("Complete Payment")
        self.geometry("400x300")
        self.configure(bg="white")
        self.order_id = order_id
        self.amount = amount

        tk.Label(self, text="💳 Complete Your Payment", font=("Helvetica", 14, "bold"), bg="white").pack(pady=12)
        tk.Label(self, text=f"Order ID: {order_id}", font=("Helvetica", 12), bg="white").pack(pady=5)
        tk.Label(self, text=f"Amount to Pay: ₹{amount}", font=("Helvetica", 12, "bold"), bg="white").pack(pady=5)

        # Pay Now button
        tk.Button(self, text="Pay Now", command=self.process_payment,
                  bg="#28a745", fg="white", font=("Helvetica", 11, "bold"), padx=16, pady=6).pack(pady=20)

        # Status label for feedback
        self.status_label = tk.Label(self, text="", font=("Helvetica", 11), bg="white", fg="gray")
        self.status_label.pack(pady=5)

    def process_payment(self):
        """Find payment record by order and mark it completed via procedure."""
        try:
            conn = get_connection()
            cur  = conn.cursor()

            # find matching payment
            cur.execute("SELECT PaymentID FROM Payment WHERE OrderID = %s", (self.order_id,))
            result = cur.fetchone()

            if not result:
                messagebox.showerror("Error", "No payment record found for this order.")
                return

            payment_id = result[0]

            # call procedure
            cur.callproc("UpdatePaymentStatus", (payment_id, 'Completed'))
            conn.commit()

            self.status_label.config(text=f"Payment #{payment_id} completed ✅", fg="green")
            messagebox.showinfo("Success", f"Payment of ₹{self.amount} completed!")

            cur.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))

class PaymentTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        tk.Label(self, text="💳 Complete Payment", font=("Helvetica", 14, "bold"), bg="white").pack(pady=10)

        form = tk.Frame(self, bg="white")
        form.pack(pady=5)

        # Payment ID input
        tk.Label(form, text="Enter Payment ID:", bg="white", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=8)
        self.payment_id = tk.Entry(form, width=20, font=("Helvetica", 11))
        self.payment_id.grid(row=0, column=1, padx=5, pady=8)

        # Pay Button
        tk.Button(
            self,
            text="Pay Now",
            command=self.process_payment,
            bg="#28a745",
            fg="white",
            font=("Helvetica", 12, "bold"),
            padx=15,
            pady=5
        ).pack(pady=20)

    def process_payment(self):
        """Marks the payment as completed and updates corresponding order."""
        payment_id = self.payment_id.get().strip()

        if not payment_id:
            messagebox.showwarning("Missing Input", "Please enter a valid Payment ID.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            # Call stored procedure to update payment and order status
            cur.callproc("UpdatePaymentStatus", (payment_id, 'Completed'))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("Success", f"Payment ID {payment_id} marked as Completed successfully!")
            self.payment_id.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

class OrderTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        tk.Label(self, text="Place Order (Multi-Item + Triggers + Functions)", font=("Helvetica", 14, "bold"), bg="white").pack(pady=10)

        form = tk.Frame(self, bg="white")
        form.pack(pady=5)

        # Customer + Address
        tk.Label(form, text="Customer ID:", bg="white").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(form, text="Address:", bg="white").grid(row=1, column=0, padx=5, pady=5)

        self.custid = tk.Entry(form)
        self.address = tk.Entry(form, width=40)
        self.custid.grid(row=0, column=1, padx=5, pady=5)
        self.address.grid(row=1, column=1, padx=5, pady=5)

        # Product section
        tk.Label(form, text="Product:", bg="white").grid(row=2, column=0, padx=5, pady=5)
        tk.Label(form, text="Quantity:", bg="white").grid(row=3, column=0, padx=5, pady=5)

        self.product_cb = ttk.Combobox(form, width=40, state="readonly")
        self.quantity = tk.Entry(form, width=10)
        self.quantity.insert(0, "1")

        self.product_cb.grid(row=2, column=1, padx=5, pady=5)
        self.quantity.grid(row=3, column=1, padx=5, pady=5)

        self.load_products()

        tk.Button(form, text="Add to Cart", command=self.add_to_cart, bg="#17a2b8", fg="white").grid(row=4, column=1, sticky="e", pady=5)

        # Cart Display
        tk.Label(self, text="Items in Cart:", bg="white", font=("Helvetica", 12, "bold")).pack(pady=5)
        self.cart_box = tk.Listbox(self, width=70, height=6)
        self.cart_box.pack(pady=5)

        # Total
        total_frame = tk.Frame(self, bg="white")
        total_frame.pack(pady=5)
        tk.Label(total_frame, text="Total Amount:", bg="white").grid(row=0, column=0, padx=5)
        self.total_amount = tk.Entry(total_frame, width=15)
        self.total_amount.grid(row=0, column=1, padx=5)
        self.total = 0.0

        # Buttons
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Order More", command=self.reset_product_fields, bg="#007bff", fg="white").grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Place Order", command=self.place_order, bg="#ffc107", fg="black").grid(row=0, column=1, padx=10)

    def load_products(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT ProductID, Name, Price FROM Product WHERE Stock > 0")
        self.products = cur.fetchall()
        cur.close()
        conn.close()
        product_list = [f"{p[0]} - {p[1]} (₹{p[2]})" for p in self.products]
        self.product_cb["values"] = product_list
        if product_list:
            self.product_cb.current(0)

    def add_to_cart(self):
        try:
            selected = self.product_cb.get()
            qty = int(self.quantity.get())
            prod_id, name, price = self.parse_product(selected)
            total_price = float(price) * qty  # convert Decimal → float
            self.cart_box.insert(tk.END, f"{name} × {qty} = ₹{round(total_price, 2)}")
            self.total += float(total_price)  # also ensure total is float

            self.total_amount.delete(0, tk.END)
            self.total_amount.insert(0, str(round(self.total, 2)))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def parse_product(self, text):
        pid = int(text.split(" - ")[0])
        for p in self.products:
            if p[0] == pid:
                return p[0], p[1], p[2]
        raise ValueError("Product not found")

    def reset_product_fields(self):
        self.quantity.delete(0, tk.END)
        self.quantity.insert(0, "1")
        messagebox.showinfo("Info", "You can now select another product!")

    def place_order(self):
        try:
            if not self.cart_box.size():
                messagebox.showwarning("Warning", "No items in cart!")
                return

            conn = get_connection()
            cur = conn.cursor()

            # Insert new order
            cur.execute("""
                INSERT INTO Orders (OrderDate, DeliveryDate, CustomerID, Address, TotalAmount)
                VALUES (CURDATE(), NULL, %s, %s, %s)
            """, (self.custid.get(), self.address.get(), self.total_amount.get()))
            conn.commit()

            # Fetch last inserted Order ID
            cur.execute("SELECT LAST_INSERT_ID()")
            order_id = cur.fetchone()[0]

            messagebox.showinfo(
                "Success",
                f"Order placed successfully!\nOrder ID: {order_id}\nTriggers updated payment & stock."
            )
            cur.close()
            conn.close()

            # ✅ Open payment window
            self.payment_window = PaymentPage(self, order_id, self.total_amount.get())

            # Reset UI
            self.cart_box.delete(0, tk.END)
            self.total_amount.delete(0, tk.END)
            self.total = 0.0
        except Exception as e:
            messagebox.showerror("Error", str(e))

# --- Run Application ---
if __name__ == "__main__":
    app = FashionStoreApp()
    app.mainloop()


