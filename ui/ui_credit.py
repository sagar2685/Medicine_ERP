import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from db.db import append, read




def credit_ui(parent):
    # Clear previous screen
    for widget in parent.winfo_children():
        widget.destroy()

    # DATA
    df = read("customer_details")
    all_customers = list(df["customer_id"] + " - " + df["customer_name"])

    # VARIABLES
    cust_var = tk.StringVar()
    amt_var = tk.StringVar()
    type_var = tk.StringVar(value="CREDIT")

    # Background
    parent.configure(bg="#f8f9fa")

    # HEADER
    header = tk.Frame(parent, bg="#0d6efd", height=60)
    header.pack(fill="x")
    
    tk.Label(
        header,
        text="💰 Customer Payment Entry",
        font=("Segoe UI", 18, "bold"),
        bg="#0d6efd",
        fg="white"
    ).pack(side="left", padx=20, pady=12)

    # CARD
    card = tk.Frame(parent, bg="white", relief="solid", bd=1)
    card.pack(fill="both", expand=True, padx=40, pady=20)

    form = tk.LabelFrame(card, text=" Payment Details ", font=("Segoe UI", 12, "bold"),
                        padx=20, pady=20, bg="white", fg="#212529")
    form.pack(padx=20, pady=20)

    # CUSTOMER WITH WILDCARD SEARCH
    tk.Label(form, text="Customer", bg="white", font=("Segoe UI", 11, "bold")).grid(
        row=0, column=0, sticky="w", pady=10, padx=10
    )
    cust_combo = ttk.Combobox(
        form,
        textvariable=cust_var,
        values=all_customers,
        width=35,
        font=("Segoe UI", 11)
    )
    cust_combo.grid(row=0, column=1, pady=10, padx=10)
    cust_combo.focus()

    # Wildcard search function for customer
    def on_customer_keyrelease(event):
        search_text = cust_var.get().strip().lower()
        if not search_text:
            cust_combo["values"] = all_customers
        else:
            filtered = [c for c in all_customers if search_text in c.lower()]
            cust_combo["values"] = sorted(filtered)

    cust_combo.bind('<KeyRelease>', on_customer_keyrelease)

    # AMOUNT
    tk.Label(form, text="Amount", bg="white", font=("Segoe UI", 11, "bold")).grid(
        row=1, column=0, sticky="w", pady=10, padx=10
    )
    amt_entry = ttk.Entry(form, textvariable=amt_var, width=37, font=("Segoe UI", 11))
    amt_entry.grid(row=1, column=1, pady=10, padx=10)

    # TYPE
    tk.Label(form, text="Transaction Type", bg="white", font=("Segoe UI", 11, "bold")).grid(
        row=2, column=0, sticky="w", pady=10, padx=10
    )

    type_frame = tk.Frame(form, bg="white")
    type_frame.grid(row=2, column=1, sticky="w", pady=10, padx=10)

    tk.Radiobutton(
        type_frame, text="Credit", variable=type_var, value="CREDIT",
        bg="white", font=("Segoe UI", 10)
    ).pack(side="left", padx=15)

    tk.Radiobutton(
        type_frame, text="Debit", variable=type_var, value="DEBIT",
        bg="white", font=("Segoe UI", 10)
    ).pack(side="left")

    # SAVE FUNCTION
    def save():
        if not cust_var.get():
            messagebox.showerror("Error", "Please select a customer")
            return

        try:
            amount = float(amt_var.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid amount")
            return

        cid, name = cust_var.get().split(" - ", 1)

        append(
            "credit_debit",
            [cid, name, type_var.get(), amount, date.today()]
        )

        messagebox.showinfo("Success", "Payment saved successfully")

        # CLEAR FORM
        cust_var.set("")
        amt_var.set("")
        type_var.set("CREDIT")
        cust_combo.focus()

    # BUTTON
    tk.Button(
        form,
        text="💾 Save Payment",
        command=save,
        bg="#198754",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        padx=20,
        pady=8
    ).grid(row=3, columnspan=2, pady=25, padx=10)
