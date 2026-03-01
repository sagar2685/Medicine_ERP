import tkinter as tk
from tkinter import ttk, messagebox
from db.db import get_customer_summary, search_customers



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


def customer_balance_ui(parent):
    for widget in parent.winfo_children():
        widget.destroy()

    page = tk.Frame(parent, bg=Colors.BG_PRIMARY)
    page.pack(fill="both", expand=True)

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except:
        pass

    # ================= HEADER ================= #
    header = tk.Frame(page, bg=Colors.PRIMARY, height=70)
    header.pack(fill="x")

    tk.Label(
        header,
        text="📊 Customer Balance Dashboard",
        font=("Segoe UI", 18, "bold"),
        bg=Colors.PRIMARY,
        fg="white"
    ).pack(side="left", padx=30, pady=18)

    # ================= MAIN CARD ================= #
    card = tk.Frame(
        page,
        bg=Colors.BG_CARD,
        relief="solid",
        bd=1
    )
    card.pack(fill="both", expand=True, padx=30, pady=20)

    # ================= SEARCH ================= #
    search_frame = tk.Frame(card, bg=Colors.BG_CARD)
    search_frame.pack(fill="x", padx=20, pady=15)

    tk.Label(
        search_frame,
        text="🔍 Search Customer by Name",
        font=("Segoe UI", 12, "bold"),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_PRIMARY
    ).pack(side="left")

    search_var = tk.StringVar()

    search_entry = ttk.Entry(
        search_frame,
        textvariable=search_var,
        width=40,
        font=("Segoe UI", 11)
    )
    search_entry.pack(side="left", padx=15, pady=10)

    # ================= CUSTOMER TABLE ================= #
    table_frame = tk.Frame(card, bg=Colors.BG_CARD)
    table_frame.pack(fill="x", padx=20, pady=10)

    columns = ("Customer ID", "Customer Name")

    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
    
    # Style the treeview
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=250)
    
    # Add scrollbar
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    
    tree.pack(side="left", fill="x", expand=True)
    vsb.pack(side="right", fill="y")
    
    # Context menu for copy
    context_menu = create_context_menu(card, tree=tree)
    tree.bind("<Button-3>", lambda e: show_context_menu(e, context_menu))

    # ================= SUMMARY SECTION ================= #
    summary_frame = tk.Frame(card, bg=Colors.BG_PRIMARY, pady=15, padx=20)
    summary_frame.pack(fill="x", pady=20)

    # Summary cards
    credit_card = tk.Frame(summary_frame, bg=Colors.SUCCESS, padx=20, pady=15)
    credit_card.pack(side="left", padx=10)
    
    tk.Label(
        credit_card,
        text="Total Credit",
        font=("Segoe UI", 10),
        bg=Colors.SUCCESS,
        fg="white"
    ).pack()
    
    credit_label = tk.Label(
        credit_card,
        text="₹0.00",
        font=("Segoe UI", 16, "bold"),
        bg=Colors.SUCCESS,
        fg="white"
    )
    credit_label.pack()

    debit_card = tk.Frame(summary_frame, bg=Colors.DANGER, padx=20, pady=15)
    debit_card.pack(side="left", padx=10)
    
    tk.Label(
        debit_card,
        text="Total Debit",
        font=("Segoe UI", 10),
        bg=Colors.DANGER,
        fg="white"
    ).pack()
    
    debit_label = tk.Label(
        debit_card,
        text="₹0.00",
        font=("Segoe UI", 16, "bold"),
        bg=Colors.DANGER,
        fg="white"
    )
    debit_label.pack()

    balance_card = tk.Frame(summary_frame, bg=Colors.PRIMARY, padx=25, pady=15)
    balance_card.pack(side="right", padx=10)
    
    tk.Label(
        balance_card,
        text="Net Balance",
        font=("Segoe UI", 10),
        bg=Colors.PRIMARY,
        fg="white"
    ).pack()
    
    balance_label = tk.Label(
        balance_card,
        text="₹0.00",
        font=("Segoe UI", 16, "bold"),
        bg=Colors.PRIMARY,
        fg="white"
    )
    balance_label.pack()

    # ================= COPY BUTTON ================= #
    def copy_summary():
        summary_text = f"Credit: ₹{credit_label.cget('text')}\nDebit: ₹{debit_label.cget('text')}\nBalance: ₹{balance_label.cget('text')}"
        copy_to_clipboard(summary_text)
        messagebox.showinfo("Copied", "Summary copied to clipboard!")
    
    copy_btn = tk.Button(
        card,
        text="📋 Copy Summary",
        command=copy_summary,
        bg=Colors.PRIMARY,
        fg="white",
        font=("Segoe UI", 10),
        relief="flat",
        padx=15,
        pady=5
    )
    copy_btn.pack(pady=(0, 15))

    # ================= FUNCTIONS ================= #

    def search_customer(*args):
        keyword = search_var.get().strip()
        tree.delete(*tree.get_children())

        if not keyword:
            return

        results = search_customers(keyword)

        for result in results:
            # Result is in format "customer_id / customer_name"
            if " / " in result:
                cid, cname = result.split(" / ", 1)
            else:
                cid, cname = result, ""
            tree.insert("", tk.END, values=(cid, cname))

    def show_balance(event):
        selected = tree.focus()
        if not selected:
            return

        cid, cname = tree.item(selected, "values")

        credit, debit, balance = get_customer_summary(cid, cname)

        credit_label.config(text=f"₹{credit:.2f}")
        debit_label.config(text=f"₹{debit:.2f}")

        if balance > 0:
            balance_label.config(
                text=f"₹{balance:.2f} (Customer Should Pay)",
                fg="white"
            )
        elif balance < 0:
            balance_label.config(
                text=f"₹{abs(balance):.2f} (You Should Return)",
                fg="white"
            )
        else:
            balance_label.config(
                text="₹0.00 (Settled)",
                fg="white"
            )

    # Live Search
    search_var.trace_add("write", search_customer)

    tree.bind("<<TreeviewSelect>>", show_balance)
