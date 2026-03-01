import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date
import calendar
from db.db import (
    append,
    get_all_distributor_records,
    find_store_entry,
    increment_store_quantity
)




def store_ui(parent):

    # ---------------- RESET SCREEN ----------------
    for widget in parent.winfo_children():
        widget.destroy()

    page = tk.Frame(parent, bg="#f4f6f9")
    page.pack(fill="both", expand=True)

    

    # ---------------- STYLE ----------------
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except:
        pass

    # Professional Color Scheme
    COLORS = {
        'PRIMARY': '#0d6efd',
        'SUCCESS': '#198754',
        'WARNING': '#ffc107',
        'DANGER': '#dc3545',
        'BG_CARD': '#ffffff',
        'BG_PRIMARY': '#f8f9fa',
        'TEXT_PRIMARY': '#212529',
        'TEXT_SECONDARY': '#6c757d'
    }

    FONT_TITLE = ("Segoe UI", 22, "bold")
    FONT_LABEL = ("Segoe UI", 12)
    FONT_ENTRY = ("Segoe UI", 12)

    # ---------------- HEADER ----------------
    header = tk.Frame(page, bg=COLORS['PRIMARY'], height=70)
    header.pack(fill="x")

    tk.Label(
        header,
        text="💊 Add Medicine to Store",
        bg=COLORS['PRIMARY'],
        fg="white",
        font=("Segoe UI", 22, "bold")
    ).pack(side="left", padx=30, pady=18)

    ttk.Separator(page).pack(fill="x")

    # ---------------- CARD ----------------
    card = tk.Frame(page, bg=COLORS['BG_CARD'], padx=30, pady=30, relief="solid", bd=1)
    card.pack(fill="both", expand=True, padx=30, pady=20)

    # ---------------- VARIABLES ----------------
    medicine = tk.StringVar()
    quantity = tk.IntVar(value=1)
    batch = tk.StringVar()
    mrp = tk.StringVar()
    distributor = tk.StringVar()

    # ---------------- HELPERS ----------------
    def create_label(text, row, col):
        tk.Label(card, text=text, font=FONT_LABEL, bg=COLORS['BG_CARD'], 
                fg=COLORS['TEXT_PRIMARY']).grid(
            row=row, column=col, sticky="w", pady=8, padx=10
        )

    def create_entry(var, row, col):
        e = tk.Entry(card, textvariable=var, width=35, font=FONT_ENTRY,
                    relief="solid", bd=1)
        e.grid(row=row + 1, column=col, pady=5, padx=10)
        return e

    # ---------------- LEFT COLUMN ----------------
    create_label("Medicine Name", 0, 0)
    med_entry = create_entry(medicine, 0, 0)

    create_label("Quantity", 2, 0)
    qty_combo = ttk.Combobox(
        card,
        textvariable=quantity,
        values=list(range(1, 1001)),
        state="readonly",
        width=33
    )
    qty_combo.grid(row=3, column=0, pady=5, padx=10)

    create_label("Batch Number", 4, 0)
    create_entry(batch, 4, 0)

    create_label("MRP (₹)", 6, 0)
    create_entry(mrp, 6, 0)

    # ---------------- DATE PICKER ----------------
    def create_date_picker(row, col):
        frame = tk.Frame(card, bg=COLORS['BG_CARD'])
        frame.grid(row=row + 1, column=col, pady=5)

        de = DateEntry(
            frame,
            width=28,
            date_pattern="yyyy-mm-dd",
            font=("Segoe UI", 11),
            background=COLORS['PRIMARY'],
            foreground='white',
            relief="solid",
            bd=1,
            mindate=None,
            maxdate=None,
            showweeknumbers=False,
            selectmode='day'
        )
        de.pack(side="left", padx=10)
        
        cal_btn = tk.Button(
            frame,
            text="📅",
            font=("Segoe UI", 12),
            bg=COLORS['PRIMARY'],
            fg="white",
            relief="flat",
            padx=8,
            pady=2,
            command=lambda: de.drop_down()
        )
        cal_btn.pack(side="left", padx=(0, 10))
        
        return de

    # ---------------- RIGHT COLUMN ----------------
    create_label("Expiry Date", 0, 1)
    expiry = create_date_picker(0, 1)

    create_label("Manufacture Date", 2, 1)
    mfg = create_date_picker(2, 1)

    create_label("Distributor", 4, 1)

    dist_names = []
    try:
        distributor_records = get_all_distributor_records()
        if distributor_records:
            if isinstance(distributor_records[0], dict):
                dist_names = [d["distributor_name"] for d in distributor_records if "distributor_name" in d]
            else:
                dist_names = [d[1] for d in distributor_records]
    except Exception as e:
        print(f"Error fetching distributors: {e}")
        dist_names = []

    if not dist_names:
        try:
            from db.db import get_all_distributors
            alt_records = get_all_distributors()
            if alt_records:
                if isinstance(alt_records[0], dict):
                    dist_names = [d.get("distributor_name", d.get("name", "")) for d in alt_records]
                else:
                    dist_names = [str(d[1]) for d in alt_records]
        except Exception as e:
            print(f"Error with fallback: {e}")

    if not dist_names:
        messagebox.showwarning(
            "No Distributors",
            "No distributors found. Please add distributors from Distributor Master first."
        )
    
    dist_combo = ttk.Combobox(
        card,
        textvariable=distributor,
        values=dist_names,
        state="readonly",
        width=33
    )
    dist_combo.grid(row=5, column=1, pady=5)

    create_label("Purchase Date", 6, 1)
    dop = create_date_picker(6, 1)

    # ---------------- SAVE LOGIC ----------------
    def save():

        med_val = medicine.get().strip()
        batch_val = batch.get().strip()
        dist_val = distributor.get().strip()

        if not med_val:
            messagebox.showerror("Validation", "Medicine name required")
            return

        if not batch_val:
            messagebox.showerror("Validation", "Batch number required")
            return

        if not dist_val:
            messagebox.showerror("Validation", "Distributor required")
            return

        try:
            mrp_val = float(mrp.get())
            if mrp_val <= 0:
                raise ValueError
        except:
            messagebox.showerror("Validation", "Enter valid MRP")
            return

        expiry_val = expiry.get_date().strftime("%Y-%m-%d")
        mfg_val = mfg.get_date().strftime("%Y-%m-%d")
        dop_val = dop.get_date().strftime("%Y-%m-%d")
        qty_val = quantity.get()

        # ---------------- DATE VALIDATION ----------------
        from datetime import datetime
        
        try:
            expiry_date = datetime.strptime(expiry_val, "%Y-%m-%d").date()
            mfg_date = datetime.strptime(mfg_val, "%Y-%m-%d").date()
            dop_date = datetime.strptime(dop_val, "%Y-%m-%d").date()
            
            # Manufacture Date should be <= Purchase Date
            if mfg_date > dop_date:
                messagebox.showerror(
                    "Validation Error",
                    f"Manufacture Date ({mfg_val}) cannot be after Purchase Date ({dop_val})"
                )
                return
            
            # Expiry Date should be > Manufacture Date
            if expiry_date <= mfg_date:
                messagebox.showerror(
                    "Validation Error",
                    f"Expiry Date ({expiry_val}) must be after Manufacture Date ({mfg_val})"
                )
                return
            
            # Expiry Date should be > Purchase Date
            if expiry_date <= dop_date:
                messagebox.showerror(
                    "Validation Error",
                    f"Expiry Date ({expiry_val}) must be after Purchase Date ({dop_val})"
                )
                return
                
        except Exception as e:
            messagebox.showerror("Error", f"Date validation error: {str(e)}")
            return

        found = find_store_entry(
            med_val,
            batch_val,
            expiry_val,
            dist_val
        )

        if found:
            row_id, existing_qty = found
            confirm = messagebox.askyesno(
                "Already Exists",
                f"This medicine already exists for this distributor.\n"
                f"Current Qty: {existing_qty}\nAdd {qty_val} more?"
            )

            if confirm:
                updated = increment_store_quantity(
                    med_val,
                    batch_val,
                    expiry_val,
                    qty_val
                )
                if updated:
                    messagebox.showinfo("Success", "Quantity updated successfully")
                else:
                    messagebox.showerror("Error", "Update failed")
            clear()
            return

        append(
            "store_details",
            [
                med_val,
                qty_val,
                expiry_val,
                mfg_val,
                batch_val,
                mrp_val,
                dist_val,
                dop_val,
            ]
        )

        messagebox.showinfo("Success", "Medicine added successfully")
        clear()

    # ---------------- CLEAR ----------------
    def clear():
        medicine.set("")
        quantity.set(1)
        batch.set("")
        mrp.set("")
        distributor.set("")
        # Reset date pickers to today's date
        today = date.today()
        expiry.set_date(today)
        mfg.set_date(today)
        dop.set_date(today)
        med_entry.focus()

    # ---------------- BUTTONS ----------------
    btn_frame = tk.Frame(card, bg=COLORS['BG_CARD'])
    btn_frame.grid(row=8, columnspan=2, pady=25)

    save_btn = tk.Button(
        btn_frame,
        text="💾 Save Medicine",
        command=save,
        bg=COLORS['SUCCESS'],
        fg="white",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        padx=25,
        pady=10
    )
    save_btn.pack(side="left", padx=15)

    clear_btn = tk.Button(
        btn_frame,
        text="🔄 Clear",
        command=clear,
        bg=COLORS['WARNING'],
        fg=COLORS['TEXT_PRIMARY'],
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        padx=25,
        pady=10
    )
    clear_btn.pack(side="left", padx=15)
