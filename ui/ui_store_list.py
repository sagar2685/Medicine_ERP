import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
from db.db import get_all_store_entries, search_store_entries


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


    
def store_list_ui(parent):
    for w in parent.winfo_children():
        w.destroy()

    page = tk.Frame(parent, bg=Colors.BG_PRIMARY)
    page.pack(fill="both", expand=True)

    # Header
    header = tk.Frame(page, bg=Colors.PRIMARY, height=70)
    header.pack(fill="x")

    ttk.Label(header, text="💊 Store — All Medicines", 
              font=("Segoe UI", 18, "bold"), 
              background=Colors.PRIMARY, foreground="white").pack(side="left", padx=20, pady=15)

    # Card
    card = tk.Frame(page, bg=Colors.BG_CARD, relief="solid", bd=1)
    card.pack(fill="both", expand=True, padx=20, pady=15)
    card.columnconfigure(1, weight=1)
    card.rowconfigure(1, weight=1)

    # Search row
    search_frame = tk.Frame(card, bg=Colors.BG_CARD)
    search_frame.grid(row=0, column=0, columnspan=4, sticky="w", padx=15, pady=15)
    
    tk.Label(search_frame, text="🔍 Search", font=("Segoe UI", 12, "bold"),
             bg=Colors.BG_CARD).pack(side="left")
    
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=40, font=("Segoe UI", 11))
    search_entry.pack(side="left", padx=(10, 8))

    def do_search():
        q = search_var.get()
        rows = search_store_entries(q)
        # Filter out expired products
        rows = filter_expired(rows)
        populate(rows)
        

    # Search button with icon
    search_btn = tk.Button(search_frame, text="🔍 Search", command=do_search,
                          bg=Colors.PRIMARY, fg="white", font=("Segoe UI", 10),
                          relief="flat", padx=15)
    search_btn.pack(side="left", padx=5)
    
    # Show All button
    def show_all():
        rows = get_all_store_entries()
        rows = filter_expired(rows)
        populate(rows)
   
    
    show_btn = tk.Button(search_frame, text="📋 Show All", 
                        command=show_all,
                        bg=Colors.TEXT_SECONDARY, fg="white", font=("Segoe UI", 10),
                        relief="flat", padx=15)
    show_btn.pack(side="left", padx=5)
    
    # Copy All button
    def copy_all():
        copy_to_clipboard(get_treeview_data(tree))
       
    
    copy_btn = tk.Button(search_frame, text="📋 Copy All", 
                        command=copy_all,
                        bg=Colors.SUCCESS, fg="white", font=("Segoe UI", 10),
                        relief="flat", padx=15)
    copy_btn.pack(side="left", padx=5)

    # Treeview for results
    cols = ("medicine", "batch_number", "quantity", "mrp", "distributor", "expiry_date", "mfg", "purchase_date")
    tree = ttk.Treeview(card, columns=cols, show="headings", height=12)
    
    style = ttk.Style()
    try:
        style.theme_use("clam")
        style.configure('Treeview.Heading', font=("Segoe UI", 10, 'bold'))
        style.configure('Treeview', font=("Segoe UI", 10), rowheight=25)
    except Exception:
        pass
        
    for c in cols:
        tree.heading(c, text=c.replace("_", " ").title())
        tree.column(c, anchor="w", width=120)
    
    tree.grid(row=1, column=0, columnspan=4, padx=15, pady=(0, 10), sticky='nsew')

    # vertical scrollbar
    vsb = ttk.Scrollbar(card, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.grid(row=1, column=4, sticky="ns", pady=(0, 10))

    # horizontal scrollbar
    hsb = ttk.Scrollbar(card, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)
    hsb.grid(row=2, column=0, columnspan=4, sticky='we', padx=15)

    # Context menu for right-click
    context_menu = create_context_menu(card, tree=tree)
    tree.bind("<Button-3>", lambda e: show_context_menu(e, context_menu))

    def filter_expired(rows):
        """Filter out expired products"""
        today = datetime.now().date()
        filtered_rows = []
        for r in rows:
            expiry_str = r.get("expiry_date", "")
            if expiry_str:
                try:
                    expiry_date = pd.to_datetime(expiry_str).date()
                    if expiry_date >= today:
                        filtered_rows.append(r)
                except:
                    # If parsing fails, include the row
                    filtered_rows.append(r)
            else:
                # If no expiry date, include the row
                filtered_rows.append(r)
        return filtered_rows

    def populate(rows):
        # Filter out expired products
        filtered_rows = filter_expired(rows)
        tree.delete(*tree.get_children())
        for r in filtered_rows:
            vals = [r.get(c, "") for c in cols]
            tree.insert("", "end", values=vals)

    def on_double(e):
        sel = tree.selection()
        if not sel:
            return
        vals = tree.item(sel[0], "values")
        details = "\n".join(f"{cols[i].replace('_',' ').title()}: {vals[i]}" for i in range(len(cols)))
        messagebox.showinfo("Medicine Details", details)
       

    tree.bind("<Double-1>", on_double)

    # initial populate
    populate(get_all_store_entries())

    # focus search
    search_entry.focus()
