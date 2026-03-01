import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import os


# Import UI utilities
try:
    from ui.ui_utils import (
        Colors, copy_to_clipboard, get_treeview_data, get_selected_row_data,
        create_context_menu, show_context_menu
    )
except ImportError:
    class Colors:
        PRIMARY = "#0d6efd"
        SUCCESS = "#198754"
        WARNING = "#ffc107"
        DANGER = "#dc3545"
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

ERP_FILE = "data/store_details.xlsx"


def _read_store_details():
    """Helper to read store details Excel file."""
    if not os.path.exists(ERP_FILE):
        messagebox.showerror("Error", f"ERP file not found: {ERP_FILE}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(ERP_FILE)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read store_details: {e}")
        return pd.DataFrame()
    
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
    return df


def _find_column(df, *candidates):
    """Find the first matching column from candidates."""
    for col in candidates:
        if col in df.columns:
            return col
    return df.columns[0] if len(df.columns) > 0 else None


def get_expired_products():
    """Fetch medicines that are already expired."""
    df = _read_store_details()
    if df.empty:
        return pd.DataFrame()

    expiry_col = _find_column(df, "expiry_date", "expiry", "expiry_date_")
    if expiry_col is None or expiry_col not in df.columns:
        messagebox.showerror("Error", "'expiry_date' column not found in store_details")
        return pd.DataFrame()

    df[expiry_col] = pd.to_datetime(df[expiry_col], errors='coerce')
    df = df[df[expiry_col].notna()]

    today = pd.Timestamp.today().normalize()
    df = df[df[expiry_col] < today]

    medicine_col = _find_column(df, "medicine", "medicine_name", "medicine_")
    batch_col = _find_column(df, "batch_number", "batch", "batch_")
    qty_col = _find_column(df, "quantity", "qty", "quantity_")
    
    if medicine_col:
        return df[[medicine_col, batch_col, qty_col, expiry_col]]
    return pd.DataFrame()


def get_expiring_products(months):
    """Fetch medicines expiring in the next specified months."""
    df = _read_store_details()
    if df.empty:
        return pd.DataFrame()

    expiry_col = _find_column(df, "expiry_date", "expiry", "expiry_date_")
    if expiry_col is None or expiry_col not in df.columns:
        messagebox.showerror("Error", "'expiry_date' column not found in store_details")
        return pd.DataFrame()

    df[expiry_col] = pd.to_datetime(df[expiry_col], errors='coerce')
    df = df[df[expiry_col].notna()]

    today = pd.Timestamp.today().normalize()
    cutoff = today + pd.DateOffset(months=months)
    df = df[df[expiry_col] >= today]
    df = df[df[expiry_col] <= cutoff]

    medicine_col = _find_column(df, "medicine", "medicine_name", "medicine_")
    batch_col = _find_column(df, "batch_number", "batch", "batch_")
    qty_col = _find_column(df, "quantity", "qty", "quantity_")
    
    if medicine_col:
        return df[[medicine_col, batch_col, qty_col, expiry_col]]
    return pd.DataFrame()


def get_expiring_products_by_category():
    """Fetch and categorize medicines by expiry status."""
    df = _read_store_details()
    if df.empty:
        return {}

    expiry_col = _find_column(df, "expiry_date", "expiry", "expiry_date_")
    if expiry_col is None or expiry_col not in df.columns:
        messagebox.showerror("Error", "'expiry_date' column not found in store_details")
        return {}

    medicine_col = _find_column(df, "medicine", "medicine_name", "medicine_")
    batch_col = _find_column(df, "batch_number", "batch", "batch_")
    qty_col = _find_column(df, "quantity", "qty", "quantity_")
    
    cols_to_use = [medicine_col, batch_col, qty_col, expiry_col]
    cols_to_use = [c for c in cols_to_use if c is not None]
    df = df[cols_to_use].copy()
    
    col_names = ['medicine', 'batch_number', 'quantity', 'expiry_date']
    df.columns = col_names[:len(df.columns)]
    
    if 'expiry_date' in df.columns:
        expiry_col = 'expiry_date'
    else:
        return {}

    df[expiry_col] = pd.to_datetime(df[expiry_col], errors='coerce')
    df = df[df[expiry_col].notna()]

    today = pd.Timestamp.today().normalize()
    
    categories = {
        'expired': pd.DataFrame(columns=['medicine', 'batch_number', 'quantity', 'expiry_date']),
        '1_month': pd.DataFrame(columns=['medicine', 'batch_number', 'quantity', 'expiry_date']),
        '2_months': pd.DataFrame(columns=['medicine', 'batch_number', 'quantity', 'expiry_date']),
        '3_months': pd.DataFrame(columns=['medicine', 'batch_number', 'quantity', 'expiry_date']),
        '6_months': pd.DataFrame(columns=['medicine', 'batch_number', 'quantity', 'expiry_date']),
        '12_months': pd.DataFrame(columns=['medicine', 'batch_number', 'quantity', 'expiry_date'])
    }
    
    categories['expired'] = df[df[expiry_col] < today].copy()
    
    one_month = today + pd.DateOffset(months=1)
    categories['1_month'] = df[(df[expiry_col] >= today) & (df[expiry_col] <= one_month)].copy()
    
    two_months = today + pd.DateOffset(months=2)
    categories['2_months'] = df[(df[expiry_col] > one_month) & (df[expiry_col] <= two_months)].copy()
    
    three_months = today + pd.DateOffset(months=3)
    categories['3_months'] = df[(df[expiry_col] > two_months) & (df[expiry_col] <= three_months)].copy()
    
    six_months = today + pd.DateOffset(months=6)
    categories['6_months'] = df[(df[expiry_col] > three_months) & (df[expiry_col] <= six_months)].copy()
    
    twelve_months = today + pd.DateOffset(months=12)
    categories['12_months'] = df[(df[expiry_col] > six_months) & (df[expiry_col] <= twelve_months)].copy()
    
    return categories


def expiry_alert_ui(parent):
    """Builds the Expiry Alert UI with tabs for all categories."""
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg=Colors.BG_PRIMARY)

    

    header = tk.Frame(parent, bg=Colors.DANGER, height=60)
    header.pack(fill="x")
    
    tk.Label(
        header,
        text="⚠️ Expiring Medicines Report",
        font=("Segoe UI", 18, "bold"),
        bg=Colors.DANGER,
        fg="white"
    ).pack(side="left", padx=20, pady=12)

    card = tk.Frame(parent, bg=Colors.BG_CARD, relief="solid", bd=1)
    card.pack(fill="both", expand=True, padx=20, pady=15)

    btn_frame = tk.Frame(card, bg=Colors.BG_CARD)
    btn_frame.pack(pady=(10, 5))

    def refresh_all():
        load_all_data()

    refresh_btn = tk.Button(btn_frame, text="🔄 Refresh All", width=18, 
                           bg=Colors.WARNING, fg=Colors.TEXT_PRIMARY,
                           font=("Segoe UI", 11, "bold"), relief="flat", pady=8,
                           command=refresh_all)
    refresh_btn.pack(side="left", padx=10)

    def copy_selected():
        copy_to_clipboard(get_treeview_data(tree))

    copy_btn = tk.Button(btn_frame, text="📋 Copy Selected", width=15,
                        bg=Colors.SUCCESS, fg="white",
                        font=("Segoe UI", 11), relief="flat", pady=8,
                        command=copy_selected)
    copy_btn.pack(side="left", padx=10)

    notebook = ttk.Notebook(card)
    notebook.pack(fill="both", expand=True, padx=15, pady=10)

    treeviews = {}
    columns = ("Medicine", "Batch", "Quantity", "Expiry Date")

    categories = [
        ("expired", "🔴 Already Expired"),
        ("1_month", "🔴 Expiring in 1 Month"),
        ("2_months", "🟠 Expiring in 2 Months"),
        ("3_months", "🟡 Expiring in 3 Months"),
        ("6_months", "🟢 Expiring in 6 Months"),
        ("12_months", "🟢 Expiring in 12 Months")
    ]

    for cat_key, cat_label in categories:
        tab_frame = tk.Frame(notebook, bg=Colors.BG_CARD)
        notebook.add(tab_frame, text=cat_label)
        
        count_label = tk.Label(tab_frame, text="Loading...", font=("Segoe UI", 10, "bold"), 
                               bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY, pady=5)
        count_label.pack(fill="x", padx=10, pady=(10, 0))
        
        tree_frame = tk.Frame(tab_frame, bg=Colors.BG_CARD)
        tree_frame.pack(pady=10, fill="both", expand=True, padx=10)

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)

        style = ttk.Style()
        try:
            style.theme_use("clam")
            style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
            style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        except:
            pass

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=180, anchor="center")

        context_menu = create_context_menu(tab_frame, tree=tree)
        tree.bind("<Button-3>", lambda e, m=context_menu: show_context_menu(e, m))

        treeviews[cat_key] = {'tree': tree, 'count_label': count_label}

    tree = treeviews['expired']['tree']

    def load_all_data():
        try:
            categories_data = get_expiring_products_by_category()
            
            for cat_key, cat_label in categories:
                tree_info = treeviews[cat_key]
                tree = tree_info['tree']
                count_label = tree_info['count_label']
                
                tree.delete(*tree.get_children())
                df = categories_data.get(cat_key, pd.DataFrame())
                
                count = len(df)
                if cat_key == 'expired':
                    count_label.config(text=f"⚠️ Already Expired: {count} medicine(s)")
                else:
                    month_text = cat_key.replace('_month', ' month').replace('_months', ' months')
                    count_label.config(text=f"⚠️ Expiring in {month_text}: {count} medicine(s)")
                
                if df.empty:
                    tree.insert("", "end", values=("No medicines in this category", "", "", ""))
                else:
                    cols = df.columns.tolist()
                    med_col = next((c for c in cols if 'medicine' in c.lower()), cols[0])
                    batch_col = next((c for c in cols if 'batch' in c.lower()), cols[1] if len(cols) > 1 else '')
                    qty_col = next((c for c in cols if 'quantity' in c.lower() or 'qty' in c.lower()), cols[2] if len(cols) > 2 else '')
                    exp_col = next((c for c in cols if 'expiry' in c.lower()), cols[-1])
                    
                    for _, row in df.iterrows():
                        exp_val = row[exp_col]
                        exp_str = exp_val.strftime("%Y-%m-%d") if hasattr(exp_val, 'strftime') else str(exp_val)
                        tree.insert("", "end", values=(
                            row[med_col],
                            row[batch_col],
                            row[qty_col],
                            exp_str,
                        ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_tab_change(event):
        selected_tab = notebook.index(notebook.select())
        cat_keys = [c[0] for c in categories]
        if 0 <= selected_tab < len(cat_keys):
            cat_key = cat_keys[selected_tab]
            treeviews[cat_key]['tree']

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    load_all_data()
