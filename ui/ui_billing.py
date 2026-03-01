import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
from db.db import read, search_customers, increment_store_quantity
from pdf.bill_pdf import generate_bill as create_pdf_bill
import webbrowser
import os



# Import UI utilities
try:
    from ui.ui_utils import (
        Colors, copy_to_clipboard, get_treeview_data, get_selected_row_data,
        create_context_menu, show_context_menu
    )
except ImportError:
    # Fallback if ui_utils not available
    class Colors:
        PRIMARY = "#0d6efd"
        SUCCESS = "#198754"
        BG_CARD = "#ffffff"
        BG_PRIMARY = "#f8f9fa"
        TEXT_PRIMARY = "#212529"
        TEXT_SECONDARY = "#6c757d"
    
    def copy_to_clipboard(text):
        try:
            import pyperclip
            pyperclip.copy(str(text))
            return True
        except:
            return False
    
    def get_treeview_data(tree):
        data = []
        for item in tree.get_children():
            values = tree.item(item, "values")
            data.append("\t".join(str(v) for v in values))
        return "\n".join(data)
    
    def get_selected_row_data(tree):
        selected = tree.selection()
        if not selected:
            return ""
        data = []
        for item in selected:
            values = tree.item(item, "values")
            data.append("\t".join(str(v) for v in values))
        return "\n".join(data)
    
    def create_context_menu(root, tree=None, extra_commands=None):
        from tkinter import Menu
        menu = Menu(root, tearoff=0)
        if tree:
            menu.add_command(label="Copy Selected Row", 
                           command=lambda: copy_to_clipboard(get_selected_row_data(tree)))
            menu.add_command(label="Copy All Data", 
                           command=lambda: copy_to_clipboard(get_treeview_data(tree)))
        return menu
    
    def show_context_menu(event, menu):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()


def billing_ui(parent):

    # ---------------- RESET SCREEN ----------------
    for w in parent.winfo_children():
        w.destroy()
    parent.configure(bg=Colors.BG_PRIMARY)

    bill_items = []
    grand_total = tk.DoubleVar(value=0.0)

   

    # ---------------- MAIN FRAME ----------------
    frame = tk.Frame(parent, bg=Colors.BG_PRIMARY)
    frame.pack(fill="both", expand=True)

    # ---------------- HEADER ----------------
    header = tk.Frame(frame, bg=Colors.PRIMARY, height=60)
    header.pack(fill="x")
    
    tk.Label(header, text="🧾 Medicine Billing",
             font=("Segoe UI", 18, "bold"),
             bg=Colors.PRIMARY, fg="white").pack(side="left", padx=20, pady=12)

    # ---------------- CARD ----------------
    card = tk.Frame(frame, bg=Colors.BG_CARD, relief="solid", bd=1)
    card.pack(fill="both", expand=True, padx=20, pady=15)

    # ---------------- CUSTOMER ----------------
    cust_frame = tk.LabelFrame(card, text="Customer Details", font=("Segoe UI", 11, "bold"), 
                              padx=15, pady=10, bg=Colors.BG_CARD)
    cust_frame.pack(fill="x", padx=15, pady=10)

    tk.Label(cust_frame, text="Customer Name", bg=Colors.BG_CARD, 
             font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")

    customer_var = tk.StringVar()
    customer_cb = ttk.Combobox(cust_frame, textvariable=customer_var, width=40, font=("Segoe UI", 10))
    customer_cb.grid(row=0, column=1, padx=10, pady=5)
    
    # Get all customers for wildcard search
    all_customers = search_customers("")
    customer_cb["values"] = all_customers

    # ---------------- WILDCARD SEARCH FOR CUSTOMER ----------------
    def on_customer_keyrelease(event):
        """Filter customers based on partial/wildcard search."""
        search_text = customer_var.get().strip().lower()
        
        if not search_text:
            # If empty, show all customers
            customer_cb["values"] = all_customers
        else:
            # Filter customers containing the search text (wildcard search)
            filtered = [cust for cust in all_customers if search_text in cust.lower()]
            customer_cb["values"] = sorted(filtered)

    # Bind key release event for wildcard search
    customer_cb.bind('<KeyRelease>', on_customer_keyrelease)
    customer_cb['state'] = 'normal'

    # Copy button for customer
    def copy_customer():
        if customer_var.get():
            copy_to_clipboard(customer_var.get())
            messagebox.showinfo("Copied", "Customer name copied to clipboard!")
            
    
    tk.Button(cust_frame, text="📋 Copy", command=copy_customer, 
              bg=Colors.PRIMARY, fg="white", font=("Segoe UI", 9),
              relief="flat", padx=10).grid(row=0, column=2, padx=5)

    # ---------------- MEDICINE SECTION ----------------
    med_frame = tk.LabelFrame(card, text="Add Medicine", font=("Segoe UI", 11, "bold"),
                             padx=15, pady=10, bg=Colors.BG_CARD)
    med_frame.pack(fill="x", padx=15, pady=10)

    # Labels
    tk.Label(med_frame, text="Medicine", bg=Colors.BG_CARD, font=("Segoe UI", 10)).grid(row=0, column=0, padx=5)
    tk.Label(med_frame, text="Expiry", bg=Colors.BG_CARD, font=("Segoe UI", 10)).grid(row=0, column=2, padx=5)
    tk.Label(med_frame, text="Batch", bg=Colors.BG_CARD, font=("Segoe UI", 10)).grid(row=0, column=4, padx=5)
    tk.Label(med_frame, text="Qty", bg=Colors.BG_CARD, font=("Segoe UI", 10)).grid(row=0, column=6, padx=5)

    medicine_var = tk.StringVar()
    expiry_var = tk.StringVar()
    batch_var = tk.StringVar()
    qty_var = tk.StringVar()

    medicine_cb = ttk.Combobox(med_frame, textvariable=medicine_var, width=25, font=("Segoe UI", 10))
    expiry_cb = ttk.Combobox(med_frame, textvariable=expiry_var, width=15, font=("Segoe UI", 10))
    batch_cb = ttk.Combobox(med_frame, textvariable=batch_var, width=15, font=("Segoe UI", 10))
    qty_entry = ttk.Entry(med_frame, textvariable=qty_var, width=10, font=("Segoe UI", 10))

    medicine_cb.grid(row=1, column=0, padx=5, pady=5)
    expiry_cb.grid(row=1, column=2, padx=5, pady=5)
    batch_cb.grid(row=1, column=4, padx=5, pady=5)
    qty_entry.grid(row=1, column=6, padx=5, pady=5)

    # ---------------- STORE DATA ----------------
    store_df = read("store_details")
    store_df.columns = store_df.columns.str.lower().str.replace(" ", "_")

    # Filter out expired products
    today = datetime.now().date()
    
    # Convert expiry_date to datetime for comparison
    store_df["expiry_date_parsed"] = pd.to_datetime(store_df["expiry_date"], errors='coerce')
    
    # Keep only non-expired products (expiry_date >= today)
    non_expired_df = store_df[store_df["expiry_date_parsed"].dt.date >= today]
    
    # If all products are expired, show empty list
    if non_expired_df.empty:
        all_medicines = []
    else:
        all_medicines = sorted(non_expired_df["medicine"].astype(str).unique())
    
    medicine_cb["values"] = all_medicines

    # ---------------- WILDCARD SEARCH FOR MEDICINE ----------------
    def on_medicine_keyrelease(event):
        """Filter medicines based on partial/wildcard search."""
        search_text = medicine_var.get().strip().lower()
        
        if not search_text:
            # If empty, show all medicines
            medicine_cb["values"] = all_medicines
        else:
            # Filter medicines containing the search text (wildcard search)
            filtered = [med for med in all_medicines if search_text in med.lower()]
            medicine_cb["values"] = sorted(filtered)

    # Bind key release event for wildcard search (triggers on every keystroke)
    medicine_cb.bind('<KeyRelease>', on_medicine_keyrelease)
    
    # Also enable auto-completion with immediate dropdown
    medicine_cb['values'] = all_medicines
    medicine_cb['state'] = 'normal'

    # ---------------- EVENTS ----------------
    def on_medicine_change(event=None):
        df = store_df[store_df["medicine"] == medicine_var.get()]
        expiry_cb["values"] = sorted(
            df["expiry_date"].astype(str).unique()
        )
        expiry_var.set("")
        batch_var.set("")
        batch_cb["values"] = []

    def on_expiry_change(event=None):
        df = store_df[
            (store_df["medicine"] == medicine_var.get()) &
            (store_df["expiry_date"].astype(str) == expiry_var.get())
        ]
        batch_cb["values"] = sorted(
            df["batch_number"].astype(str).unique()
        )

    medicine_cb.bind("<<ComboboxSelected>>", on_medicine_change)
    expiry_cb.bind("<<ComboboxSelected>>", on_expiry_change)

    # ---------------- TABLE ----------------
    table_frame = tk.Frame(card, bg=Colors.BG_CARD)
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    cols = ("Medicine", "Expiry", "Batch", "Qty", "MRP", "Amount")

    tree = ttk.Treeview(
        table_frame,
        columns=cols,
        show="headings",
        height=8
    )

    # Style the treeview
    style = ttk.Style()
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center")

    # Add scrollbars
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    hsb.pack(side="bottom", fill="x")

    # Context menu for copy functionality
    context_menu = create_context_menu(card, tree=tree)
    tree.bind("<Button-3>", lambda e: show_context_menu(e, context_menu))

    # ---------------- ADD ITEM ----------------
    def add_item():
        try:
            qty = int(qty_var.get())
        except:
            messagebox.showerror("Error", "Invalid quantity")
            return

        selected_medicine = medicine_var.get().strip()
        selected_expiry = expiry_var.get().strip()
        selected_batch = batch_var.get().strip()

        if not selected_medicine or not selected_expiry or not selected_batch:
            messagebox.showerror(
                "Error",
                "Please select Medicine, Expiry and Batch"
            )
            return

        # -------- DUPLICATE CHECK --------
        for item in tree.get_children():
            values = tree.item(item)["values"]

            if (
                str(values[0]).strip() == selected_medicine and
                str(values[1]).strip() == selected_expiry and
                str(values[2]).strip() == selected_batch
            ):
                messagebox.showerror(
                    "Duplicate Entry",
                    "This medicine with same batch is already added!"
                )
                return
        # ---------------------------------

        df = store_df[
            (store_df["medicine"] == selected_medicine) &
            (store_df["expiry_date"].astype(str) == selected_expiry) &
            (store_df["batch_number"].astype(str) == selected_batch)
        ]

        if df.empty:
            messagebox.showerror("Error", "Stock not found")
            return

        available = int(df.iloc[0]["quantity"])
        mrp = float(df.iloc[0]["mrp"])

        if qty > available:
            messagebox.showerror(
                "Error",
                f"Only {available} available"
            )
            return

        amount = qty * mrp

        tree.insert(
            "",
            "end",
            values=(
                selected_medicine,
                selected_expiry,
                selected_batch,
                qty,
                mrp,
                f"{amount:.2f}"
            )
        )

        bill_items.append(
            (
                selected_medicine,
                selected_expiry,
                selected_batch,
                qty,
                mrp,
                amount
            )
        )

        grand_total.set(grand_total.get() + amount)
        qty_var.set("")

    ttk.Button(
        med_frame,
        text="➕ Add Item",
        command=add_item
    ).grid(row=1, column=8, padx=10)

    # ---------------- TOTAL DISPLAY ----------------
    total_frame = tk.Frame(card, bg=Colors.BG_CARD, relief="groove", bd=1)
    total_frame.pack(fill="x", padx=15, pady=10)

    tk.Label(
        total_frame,
        text="Grand Total:",
        font=("Segoe UI", 14, "bold"),
        bg=Colors.BG_CARD
    ).pack(side="left", padx=15, pady=10)

    total_label = tk.Label(
        total_frame,
        textvariable=grand_total,
        font=("Segoe UI", 18, "bold"),
        fg=Colors.SUCCESS,
        bg=Colors.BG_CARD
    )
    total_label.pack(side="left", padx=10)

    # Copy total button
    def copy_total():
        copy_to_clipboard(f"{grand_total.get():.2f}")
        messagebox.showinfo("Copied", f"Total ₹{grand_total.get():.2f} copied to clipboard!")
    
    tk.Button(total_frame, text="📋 Copy Total", command=copy_total,
              bg=Colors.PRIMARY, fg="white", font=("Segoe UI", 9),
              relief="flat", padx=10).pack(side="right", padx=15)

    # ---------------- GENERATE BILL ----------------
    def generate_bill():

        if not bill_items:
            messagebox.showerror("Error", "No items added")
            return

        customer_name = customer_var.get().strip()
        if not customer_name:
            messagebox.showerror("Error", "Customer name is required")
            return

        # Update stock
        for med, exp, batch, qty, mrp, _ in bill_items:
            increment_store_quantity(med, batch, exp, -qty)

        # Generate PDF
        pdf_filename = create_pdf_bill(customer_name, bill_items)

        messagebox.showinfo(
            "Success",
            f"Bill generated: {pdf_filename}\nStock updated successfully!"
        )

        # Get current date for the subfolder path
        today_date = datetime.now().strftime('%Y-%m-%d')
        pdf_path = os.path.join("customer_bills", today_date, pdf_filename)
        webbrowser.open(f"file://{os.path.abspath(pdf_path)}")

        clear_page()

    # ---------------- CLEAR PAGE ----------------
    def clear_page():
        tree.delete(*tree.get_children())
        bill_items.clear()
        grand_total.set(0.0)
        customer_var.set("")
        medicine_var.set("")
        expiry_var.set("")
        batch_var.set("")
        qty_var.set("")

    btn_frame = tk.Frame(card, bg=Colors.BG_CARD)
    btn_frame.pack(pady=15)

    # Generate Bill Button
    gen_btn = tk.Button(
        btn_frame,
        text="🧾 Generate Bill",
        command=generate_bill,
        bg=Colors.SUCCESS,
        fg="white",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padx=20,
        pady=8
    )
    gen_btn.pack(side="left", padx=10)

    # Clear Button
    tk.Button(
        btn_frame,
        text="🗑️ Clear Page",
        command=clear_page,
        bg="#dc3545",
        fg="white",
        font=("Segoe UI", 11),
        relief="flat",
        padx=20,
        pady=8
    ).pack(side="left", padx=10)
