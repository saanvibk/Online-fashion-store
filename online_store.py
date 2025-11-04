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
        self.order_tab = OrderTab(tabs)
        self.view_tab = ViewTab(tabs)

        tabs.add(self.customer_tab, text="👤 Customer")
        tabs.add(self.product_tab, text="👜 Product")
        tabs.add(self.order_tab, text="📦 Orders / Payments")
        tabs.add(self.view_tab, text="📊 View Data")

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

        labels = ["Product Name:", "Description:", "Image URL:", "Price:", "Stock:", "Brand:", "Category ID:"]
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

            # unpack entries
            name = self.entries[0].get()
            desc = self.entries[1].get()
            image = self.entries[2].get()
            price = float(self.entries[3].get())
            stock = int(self.entries[4].get())
            brand = self.entries[5].get()
            catid = int(self.entries[6].get())

            cur.callproc("AddProduct", (name, desc, image, price, stock, brand, catid))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("Success", f"Product '{name}' added successfully via stored procedure!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# --- Order / Payment Tab ---
class OrderTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="white")

        tk.Label(self, text="Place Order (Triggers + Functions)", font=("Helvetica", 14, "bold"), bg="white").pack(pady=10)

        form = tk.Frame(self, bg="white")
        form.pack(pady=5)

        tk.Label(form, text="Customer ID:", bg="white").grid(row=0, column=0)
        tk.Label(form, text="Address:", bg="white").grid(row=1, column=0)
        tk.Label(form, text="Total Amount:", bg="white").grid(row=2, column=0)

        self.custid = tk.Entry(form)
        self.address = tk.Entry(form)
        self.amount = tk.Entry(form)

        self.custid.grid(row=0, column=1)
        self.address.grid(row=1, column=1)
        self.amount.grid(row=2, column=1)

        tk.Button(self, text="Place Order", command=self.place_order, bg="#ffc107").pack(pady=10)

    def place_order(self):
        query = """
            INSERT INTO Orders (OrderDate, DeliveryDate, CustomerID, Address, TotalAmount)
            VALUES (CURDATE(), NULL, %s, %s, %s)
        """
        params = (self.custid.get(), self.address.get(), self.amount.get())
        run_query(query, params)
        messagebox.showinfo("Success", "Order placed! Triggers auto-updated Payment and Product stock.")

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

        # Treeview for displaying table data
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(expand=True, fill="both", pady=20, padx=20)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def show_data(self, table):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]  # ✅ Get column names

            # Clear old data
            self.tree.delete(*self.tree.get_children())

            # Reconfigure columns
            self.tree["columns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", width=120)

            # Insert new rows
            for row in rows:
                self.tree.insert("", "end", values=row)

            cur.close()
            conn.close()

            if not rows:
                messagebox.showinfo("Info", f"No records found in {table} table.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

# --- Run Application ---
if __name__ == "__main__":
    app = FashionStoreApp()
    app.mainloop()
