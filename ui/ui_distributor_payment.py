import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from db.db import (
    append,
    receipt_exists,
    get_all_distributor_records,
    get_distributor_pending_summary,
    get_distributor_names_from_transactions,
)



# =========================================================
# ================= DISTRIBUTOR PAYMENT UI ================
# =========================================================

def distributor_payment_ui(parent):
    for w in parent.winfo_children():
        w.destroy()

    page = tk.Frame(parent, bg="#f4f6f9")
    page.pack(fill="both", expand=True)

    

    # ---------------- HEADER ----------------
    header = tk.Frame(page, bg="#0d6efd", height=70)
    header.pack(fill="x")

    tk.Label(
        header,
        text="💰 Distributor Payment",
        font=("Segoe UI", 20, "bold"),
        bg="#0d6efd",
        fg="white"
    ).pack(side="left", padx=25, pady=18)

    # ---------------- CARD ----------------
    card = tk.Frame(page, bg="white")
    card.pack(fill="both", expand=True, padx=20, pady=20)

    notebook = ttk.Notebook(card)
    notebook.pack(fill="both", expand=True)

    # =====================================================
    # =================== PAYMENT TAB =====================
    # =====================================================
    payment_tab = tk.Frame(notebook, bg="white")
    notebook.add(payment_tab, text="Payment")

    form = tk.Frame(payment_tab, bg="white")
    form.pack(fill="x", padx=20, pady=20)
    form.grid_columnconfigure(1, weight=1)

    def label(text, row):
        ttk.Label(form, text=text, background="white") \
            .grid(row=row, column=0, sticky="w", padx=8, pady=6)

    def entry(row, readonly=False):
        e = ttk.Entry(form)
        e.grid(row=row, column=1, sticky="ew", padx=8, pady=6)
        if readonly:
            e.configure(state="readonly")
        return e

    # ---------- Fields ----------
    label("Receipt No *", 0)
    receipt = entry(0)

    label("Bill No", 1)
    bill = entry(1)

    label("Distributor *", 2)
    distributor_cb = ttk.Combobox(
        form,
        values=[r["distributor_name"] for r in get_all_distributor_records()],
        state="readonly"
    )
    distributor_cb.grid(row=2, column=1, sticky="ew", padx=8, pady=6)

    label("Distributor ID", 3)
    dist_id = entry(3, readonly=True)

    label("Phone", 4)
    phone = entry(4, readonly=True)

    label("Bill Amount (₹) *", 5)
    bill_amt = entry(5)

    label("Paid Amount (₹) *", 6)
    paid_amt = entry(6)

    label("Balance (₹)", 7)
    balance = entry(7, readonly=True)

    label("Payment Date", 8)
    pay_date = entry(8, readonly=True)
    pay_date.configure(state="normal")
    pay_date.insert(0, date.today().strftime("%d-%m-%Y"))
    pay_date.configure(state="readonly")

    # ---------- Events ----------
    def load_distributor(event=None):
        name = distributor_cb.get()
        for r in get_all_distributor_records():
            if r["distributor_name"] == name:
                dist_id.configure(state="normal")
                phone.configure(state="normal")
                dist_id.delete(0, tk.END)
                phone.delete(0, tk.END)
                dist_id.insert(0, r["distributor_id"])
                phone.insert(0, r["phone_number"])
                dist_id.configure(state="readonly")
                phone.configure(state="readonly")

    distributor_cb.bind("<<ComboboxSelected>>", load_distributor)

    def calc_balance(event=None):
        try:
            b = float(bill_amt.get())
            p = float(paid_amt.get())
            balance.configure(state="normal")
            balance.delete(0, tk.END)
            balance.insert(0, f"{b - p:.2f}")
            balance.configure(state="readonly")
        except:
            pass

    bill_amt.bind("<KeyRelease>", calc_balance)
    paid_amt.bind("<KeyRelease>", calc_balance)

    # ---------- Save ----------
    def save_payment():
        if not receipt.get():
            messagebox.showerror("Error", "Receipt number required")
            return

        if receipt_exists(receipt.get()):
            messagebox.showerror("Error", "Receipt already exists")
            return

        try:
            b = float(bill_amt.get())
            p = float(paid_amt.get())
        except:
            messagebox.showerror("Error", "Invalid amount")
            return

        bal = b - p

        append(
            "distributor_transactions",
            [
                receipt.get(),
                bill.get(),
                dist_id.get(),
                distributor_cb.get(),
                phone.get(),
                b,
                p,
                bal,
                date.today(),
            ],
        )

        messagebox.showinfo("Success", "Payment saved successfully")

        receipt.delete(0, tk.END)
        bill.delete(0, tk.END)
        bill_amt.delete(0, tk.END)
        paid_amt.delete(0, tk.END)
        distributor_cb.set("")
        balance.configure(state="normal")
        balance.delete(0, tk.END)
        balance.configure(state="readonly")

        refresh_balances()

    ttk.Button(form, text="Save Payment", command=save_payment) \
        .grid(row=9, columnspan=2, pady=15)

    # =====================================================
    # =================== BALANCES TAB ====================
    # =====================================================
    balances_tab = tk.Frame(notebook, bg="white")
    notebook.add(balances_tab, text="Balances")

    top = tk.Frame(balances_tab, bg="white")
    top.pack(fill="x", padx=20, pady=10)

    ttk.Label(
        top,
        text="Distributor Pending Balances",
        font=("Segoe UI", 13, "bold"),
        background="white"
    ).pack(side="left")

    ttk.Label(top, text="Search:", background="white") \
        .pack(side="left", padx=(30, 6))

    filter_var = tk.StringVar()
    filter_entry = ttk.Entry(top, textvariable=filter_var, width=30)
    filter_entry.pack(side="left")

    tree = ttk.Treeview(
        balances_tab,
        columns=("name", "pending"),
        show="headings",
        height=12
    )
    tree.heading("name", text="Distributor Name")
    tree.heading("pending", text="Total Pending (₹)")
    tree.column("name", width=400, anchor="w")

    tree.column("pending", width=200, anchor="e")
    tree.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh_balances(*_):
        tree.delete(*tree.get_children())

        query = filter_var.get().lower().strip()
        rows = get_distributor_pending_summary()

        for r in rows:
            if query and query not in r["distributor_name"].lower():
                continue

            tree.insert(
                "",
                "end",
                values=(r["distributor_name"], f"{r['total_pending']:.2f}")
            )

    filter_entry.bind("<KeyRelease>", refresh_balances)
    refresh_balances()
