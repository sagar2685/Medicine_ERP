import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from db.db import get_all_distributor_records, add_distributor_adjustment


def distributor_ledger_ui(parent):
    for w in parent.winfo_children():
        w.destroy()

    page = tk.Frame(parent, bg="#f4f6f9")
    page.pack(fill="both", expand=True)

    header = tk.Frame(page, bg="white", height=70)
    header.pack(fill="x")
    ttk.Label(header, text="Distributor Ledger (Credit / Debit)", font=("Segoe UI", 16, "bold"), background="white").pack(side="left", padx=20, pady=18)

    card = tk.Frame(page, bg="white")
    card.pack(fill="both", expand=True, padx=20, pady=20)

    frm = tk.Frame(card, bg="white")
    frm.pack(fill="x", padx=12, pady=12)
    frm.grid_columnconfigure(1, weight=1)

    def L(text, row):
        ttk.Label(frm, text=text, background="white").grid(row=row, column=0, sticky="w", padx=8, pady=6)

    def E(row):
        e = ttk.Entry(frm)
        e.grid(row=row, column=1, sticky="ew", padx=8, pady=6)
        return e

    L("Distributor", 0)
    dist_cb = ttk.Combobox(frm, values=[r['distributor_name'] for r in get_all_distributor_records()])
    dist_cb.grid(row=0, column=1, sticky="ew", padx=8, pady=6)

    L("Type", 1)
    type_cb = ttk.Combobox(frm, values=["credit", "debit"])
    type_cb.grid(row=1, column=1, sticky="ew", padx=8, pady=6)

    L("Amount (₹)", 2)
    amt_e = E(2)

    L("Note", 3)
    note_e = E(3)

    def do_save():
        name = dist_cb.get().strip()
        kind = type_cb.get().strip().lower()
        amt = amt_e.get().strip()
        note = note_e.get().strip()
        if not name:
            messagebox.showerror("Validation", "Select distributor")
            return
        if kind not in ("credit", "debit"):
            messagebox.showerror("Validation", "Select credit or debit")
            return
        try:
            val = float(amt)
        except Exception:
            messagebox.showerror("Validation", "Enter numeric amount")
            return
        # find distributor id from records
        recs = get_all_distributor_records()
        dist_id = None
        for r in recs:
            if r.get('distributor_name') == name or r.get('distributor_name', '').lower() == name.lower():
                dist_id = r.get('distributor_id')
                break
        if not dist_id:
            messagebox.showerror("Not found", "Distributor not found")
            return
        ok = add_distributor_adjustment(dist_id, name, kind, val, note)
        if ok:
            messagebox.showinfo("Saved", "Adjustment saved")
            dist_cb.set('')
            type_cb.set('')
            amt_e.delete(0, tk.END)
            note_e.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Failed to save adjustment")

    btn = ttk.Button(card, text="Save Adjustment", command=do_save, style='Primary.TButton')
    btn.pack(pady=12)
