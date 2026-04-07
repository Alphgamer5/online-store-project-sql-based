import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import sys
import os
from datetime import datetime

# Function to get resource path (works in dev and PyInstaller exe)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


db = sqlite3.connect("dbs.db")
cursor = db.cursor()

# Create tables if they don't exist
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone VARCHAR(50) NOT NULL,
        address TEXT NOT NULL,
        payment_method VARCHAR(20) NOT NULL,
        order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INT NOT NULL,
        product_id VARCHAR(50) NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        category TEXT
    )
    """)
    db.commit()
except Exception as e:
    print("Error creating tables:", e)
    db.rollback()

cart = {}
product_images = {}

# Root window
root = ttk.Window(themename="cyborg")
root.title("DMART - Modern Store")
root.geometry("1200x700")

# Configure Treeview style
style = ttk.Style()
style.configure("Treeview", font=("Segoe UI", 13), rowheight=70)
style.configure("Treeview.Heading", font=("Segoe UI", 14, "bold"))

# Top Frame (Logo and Search)
top_frame = ttk.Frame(root)
top_frame.pack(fill=X, padx=10, pady=10)

# Logo
try:
    logo_img = Image.open(resource_path("logo.png")).resize((180, 100))
    logo = ImageTk.PhotoImage(logo_img)
    logo_label = ttk.Label(top_frame, image=logo)
    logo_label.pack(side=tk.LEFT)
except Exception as e:
    print("Logo load error:", e)
    logo_label = ttk.Label(top_frame, text="DMART", font=("Segoe UI", 24, "bold"))
    logo_label.pack(side=tk.LEFT)

# Search bar
search_entry = ttk.Entry(top_frame, width=40, font=("Segoe UI", 13))
search_entry.pack(side=tk.LEFT, padx=10)

def filter_products():
    query = search_entry.get().lower()
    product_tree.delete(*product_tree.get_children())
    cursor.execute("SELECT * FROM products")
    for row in cursor.fetchall():
        if query in row[1].lower():
            pid, name, price, stock, category = row
            image = product_images.get(pid)
            product_tree.insert("", tk.END, text="", image=image, values=row)

search_btn = ttk.Button(top_frame, text="Search", command=filter_products)
search_btn.pack(side=tk.LEFT, padx=10)

# Cart button
cart_count_var = tk.StringVar(value="0")
cart_btn = ttk.Button(top_frame, textvariable=cart_count_var, bootstyle="info", command=lambda: cart_window())
cart_btn.pack(side=tk.RIGHT, padx=10)
cart_label = ttk.Label(top_frame, text="🛒 Cart", font=("Segoe UI", 13))
cart_label.pack(side=tk.RIGHT)

# Function to update cart count
def update_cart_count():
    total_items = sum(quantity for _, quantity, _, _ in cart.values())
    cart_count_var.set(str(total_items))

# Function to open cart window
def cart_window():
    win = tk.Toplevel(root)
    win.title("Your Cart")
    
    # Get main window's dimensions and position
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    root_x = root.winfo_x()
    root_y = root.winfo_y()

    # Calculate cart window dimensions (e.g., 90% of main window size)
    cart_width = int(root_width * 0.9)
    cart_height = int(root_height * 0.9)

    # Calculate position to center it relative to the main window
    cart_x = int(root_x + (root_width - cart_width) / 2)
    cart_y = int(root_y + (root_height - cart_height) / 2)

    # Set the cart window's geometry
    win.geometry(f"{cart_width}x{cart_height}+{cart_x}+{cart_y}")

    current_total = 0.0 # Calculate total first, as it's needed for the total_label
    for pid, (name, qty, price, _) in cart.items():
        current_total += (qty * price)

    # *** CRITICAL FIX: Pack the bottom elements FIRST! ***
    bottom_control_frame = ttk.Frame(win)
    bottom_control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10)) # Pack to BOTTOM

    # Total label - packed into bottom_control_frame
    total_label = ttk.Label(bottom_control_frame, text=f"Grand Total: Rs.{current_total:.2f}", font=("Segoe UI", 16, "bold"), anchor="e")
    total_label.pack(fill=tk.X, pady=(5, 0))

    # Frame for buttons - packed into bottom_control_frame
    btn_frame = ttk.Frame(bottom_control_frame)
    btn_frame.pack(fill=tk.X, pady=(0, 0))

    def remove_selected_from_cart_window():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item in the cart to remove.")
            return

        for item in selected:
            values = tree.item(item, 'values')
            product_name_to_remove = values[0]
            
            # Find the product ID in the cart based on name and remove it
            for pid, (name, _, _, _) in list(cart.items()):
                if name == product_name_to_remove:
                    del cart[pid]
                    break
        update_cart_count()
        win.destroy() # Close and re-open to refresh the cart display
        cart_window()

    checkout_btn = ttk.Button(btn_frame, text="Checkout", bootstyle="success", command=lambda: [win.destroy(), checkout()])
    checkout_btn.pack(side=tk.RIGHT, padx=5)

    remove_btn = ttk.Button(btn_frame, text="Remove Selected", bootstyle="danger", command=remove_selected_from_cart_window)
    remove_btn.pack(side=tk.LEFT, padx=5)
    # *** END CRITICAL FIX ***

    # Frame for the cart list (will expand to fill remaining space)
    tree_frame = ttk.Frame(win)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5)) # This now fills the space *above* the bottom_control_frame

    tree = ttk.Treeview(tree_frame, columns=("Name", "Qty", "Price", "Total"), show='tree headings')
    tree.heading("#0", text="Image")  # Add a column for the image
    tree.column("#0", width=80)       # Adjust width as needed
    tree.heading("Name", text="Product")
    tree.heading("Qty", text="Quantity")
    tree.heading("Price", text="Unit Price")
    tree.heading("Total", text="Total")

    # Set column alignments for the cart Treeview
    tree.column("Name", anchor=tk.CENTER)
    tree.column("Qty", anchor=tk.CENTER)
    tree.column("Price", anchor=tk.CENTER)
    tree.column("Total", anchor=tk.CENTER)

    tree.pack(fill=tk.BOTH, expand=True)

    # Populate the treeview (this block remains the same, just reordered)
    for pid, (name, qty, price, _) in cart.items():
        total = qty * price
        try:
            image_path = resource_path(f"product_images/{pid}.png")
            img = Image.open(image_path).resize((60, 40))  # Resize for cart
            photo = ImageTk.PhotoImage(img)
            # Store a reference to the image to prevent garbage collection
            tree.image_references = getattr(tree, 'image_references', [])
            tree.image_references.append(photo) 
            
            tree.insert("", tk.END, text="", image=photo, values=(name, qty, f"Rs.{price:.2f}", f"Rs.{total:.2f}"))
        except Exception as e:
            print(f"Image load failed for {pid}: {e}")
            tree.insert("", tk.END, text="", values=(name, qty, f"Rs.{price:.2f}", f"Rs.{total:.2f}"))


# Layout frames
layout = ttk.Frame(root)
layout.pack(fill=tk.BOTH, expand=True, padx=10)
layout.columnconfigure(0, weight=1)
layout.columnconfigure(1, weight=2)
layout.columnconfigure(2, weight=1)
layout.rowconfigure(0, weight=1)

# --- Product Grid ---
products_frame = ttk.LabelFrame(layout, text="🍭️ Products", bootstyle="info")
products_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
products_frame.rowconfigure(0, weight=1)
products_frame.columnconfigure(0, weight=1)

product_tree = ttk.Treeview(products_frame, columns=("ID", "Name", "Price", "Stock", "Category"), show='tree headings')
product_tree.heading("#0", text="Image")
product_tree.column("#0", width=80)
for col in ("ID", "Name", "Price", "Stock", "Category"):
    product_tree.heading(col, text=col)
    product_tree.column(col, anchor=tk.CENTER)

# Scrollbar
tree_scroll = ttk.Scrollbar(products_frame, orient="vertical", command=product_tree.yview)
product_tree.configure(yscrollcommand=tree_scroll.set)
product_tree.grid(row=0, column=0, sticky="nsew", padx=(10,0), pady=(10,0))
tree_scroll.grid(row=0, column=1, sticky="ns", pady=(10,0))

# Add to Cart button at the bottom
add_btn = ttk.Button(products_frame, text="Add to Cart", bootstyle="success", command=lambda: add_to_cart())
add_btn.grid(row=1, column=0, columnspan=2, pady=(5, 10))


# Checkout function
def checkout():
    if not cart:
        messagebox.showinfo("Cart Empty", "Your cart is empty. Add some products first.")
        return
    
    # Create a new window for customer details
    checkout_window = tk.Toplevel(root)
    checkout_window.title("Checkout")
    checkout_window.geometry("500x400")
    
    # Customer details form
    ttk.Label(checkout_window, text="Customer Details", font=("Segoe UI", 14, "bold")).pack(pady=10)
    
    fields = [
        ("Name", "customer_name"),
        ("Email", "email"),
        ("Phone", "phone"),
        ("Address", "address"),
        ("Payment Method", "payment_method")
    ]
    
    entries = {}
    for label, field in fields:
        frame = ttk.Frame(checkout_window)
        frame.pack(fill=tk.X, padx=20, pady=5)
        ttk.Label(frame, text=f"{label}:", width=15).pack(side=tk.LEFT)
        if field == "payment_method":
            payment_var = tk.StringVar(value="Cash")
            entry = ttk.Combobox(frame, textvariable=payment_var, 
                                 values=["Cash", "Credit Card", "Debit Card", "UPI"])
        else:
            entry = ttk.Entry(frame)
        entry.pack(fill=tk.X, expand=True)
        entries[field] = entry
    
    def process_order():
        # Validate fields
        for field, entry in entries.items():
            if not entry.get().strip():
                messagebox.showerror("Error", f"Please fill in {field.replace('_', ' ')}")
                return
        
        total_amount = sum(qty * price for _, qty, price, _ in cart.values())
        
        try:
            # Insert order
            cursor.execute(
                "INSERT INTO orders (customer_name, email, phone, address, payment_method) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    entries["customer_name"].get(),
                    entries["email"].get(),
                    entries["phone"].get(),
                    entries["address"].get(),
                    entries["payment_method"].get()
                )
            )
            order_id = cursor.lastrowid
            
            # Insert order items
            for pid, (name, qty, price, _) in cart.items():
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, product_name, quantity, price) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (order_id, pid, name, qty, price)
                )
                
                # Update product stock
                cursor.execute(
                    "UPDATE products SET stock = stock - ? WHERE product_id = ?",
                    (qty, pid)
                )
            
            db.commit()
            
            messagebox.showinfo(
                "Order Complete", 
                f"Thank you for your purchase!\n"
                f"Order ID: {order_id}\n"
                f"Total: ₹{total_amount:.2f}\n"
                "Your items will be delivered soon."
            )
            
            cart.clear()
            update_cart_count()
            refresh_products()
            checkout_window.destroy()
            
        except Exception as e:
            db.rollback()
            messagebox.showerror("Checkout Error", f"An error occurred during checkout:\n{str(e)}")
    
    ttk.Button(
        checkout_window, 
        text="Complete Order", 
        bootstyle="success",
        command=process_order
    ).pack(pady=20)

product_tree.tag_configure("hover", background="#333333")

def on_hover(event):
    hovered_row = product_tree.identify_row(event.y)
    for row in product_tree.get_children():
        tags = product_tree.item(row, 'tags')
        if isinstance(tags, str):
            tags = (tags,)
        product_tree.item(row, tags=tuple(tag for tag in tags if tag != 'hover'))
    if hovered_row:
        tags = product_tree.item(hovered_row, 'tags')
        if isinstance(tags, str):
            tags = (tags,)
        if 'hover' not in tags:
            product_tree.item(hovered_row, tags=tags + ('hover',))

product_tree.bind("<Motion>", on_hover)

def refresh_products():
    global product_images
    product_images.clear()
    product_tree.delete(*product_tree.get_children())
    cursor.execute("SELECT * FROM products")
    for row in cursor.fetchall():
        pid, name, price, stock, category = row
        try:
            image_path = resource_path(f"product_images/{pid}.png")
            img = Image.open(image_path).resize((100, 60))
            photo = ImageTk.PhotoImage(img)
            product_images[pid] = photo
            product_tree.insert("", tk.END, text="", image=photo, values=row)
        except Exception as e:
            print(f"Image load failed for {pid}: {e}")
            product_tree.insert("", tk.END, text="", values=row)

def add_to_cart():
    selected = product_tree.focus()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a product")
        return
    pid, name, price, stock, category = product_tree.item(selected, 'values')
    price = float(price)
    stock = int(stock)
    if stock <= 0:
        messagebox.showerror("Out of Stock", f"{name} is not available.")
        return
    if pid in cart:
        if cart[pid][1] < stock:
            cart[pid] = (name, cart[pid][1] + 1, price, stock)
        else:
            messagebox.showinfo("Limit", f"Only {stock} items available.")
            return
    else:
        cart[pid] = (name, 1, price, stock)
    update_cart_count()

refresh_products()
root.mainloop()