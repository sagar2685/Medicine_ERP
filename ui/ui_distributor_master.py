import tkinter as tk
from tkinter import ttk, messagebox

from db.db import (
    get_all_distributors,
    add_distributor,
    update_distributor_by_id,
    generate_distributor_id
)



# Import UI utilities for copy functionality
try:
    from ui.ui_utils import (
        Colors, copy_to_clipboard, get_treeview_data,
        create_context_menu, show_context_menu
    )
except ImportError:
    class Colors:
        PRIMARY = "#0d6efd"
        SUCCESS = "#198754"
    
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


def validate_phone_number(phone):
    """
    Validate phone number - must be exactly 10 digits
    Returns: (is_valid, error_message)
    """
    # Remove any spaces or dashes
    phone = phone.strip()
    
    # Check if empty
    if not phone:
        return False, "Phone number is required"
    
    # Check if contains only digits
    if not phone.isdigit():
        return False, "Phone number must contain only digits"
    
    # Check if exactly 10 digits
    if len(phone) != 10:
        return False, "Phone number must be exactly 10 digits"
    
    return True, ""


def distributor_master_ui(parent):

    # ================= CLEAR SCREEN =================
    for widget in parent.winfo_children():
        widget.destroy()

    parent.configure(bg="#f4f6f9")

    

    # ================= TITLE =================
    title = tk.Label(
        parent,
        text="Distributor Management",
        font=("Segoe UI", 18, "bold"),
        bg="#f4f6f9",
        fg="#1e88e5"
    )
    title.pack(pady=15)

    # ================= MAIN FRAME =================
    main_frame = tk.Frame(parent, bg="white", bd=1, relief="solid")
    main_frame.pack(padx=20, pady=10, fill="both", expand=True)

    # ================= LEFT FORM =================
    form_frame = tk.Frame(main_frame, bg="white")
    form_frame.pack(side="left", padx=30, pady=20)

    def label(text, row):
        tk.Label(
            form_frame,
            text=text,
            font=("Segoe UI", 10),
            bg="white"
        ).grid(row=row, column=0, sticky="w", pady=8)

    def entry_widget(row):
        e = tk.Entry(form_frame, width=30, font=("Segoe UI", 10))
        e.grid(row=row, column=1, pady=8)
        return e

    # ================= FIELDS =================

    label("Distributor ID", 0)
    distributor_id_entry = entry_widget(0)
    distributor_id_entry.config(state="readonly")

    label("Distributor Name", 1)
    name_entry = entry_widget(1)

    label("Phone Number", 2)
    phone_entry = entry_widget(2)

    label("Address", 3)
    address_entry = entry_widget(3)

    # ================= NEW =================
    def new_distributor():
        did = generate_distributor_id()

        distributor_id_entry.config(state="normal")
        distributor_id_entry.delete(0, tk.END)
        distributor_id_entry.insert(0, did)
        distributor_id_entry.config(state="readonly")

        name_entry.delete(0, tk.END)
        phone_entry.delete(0, tk.END)
        address_entry.delete(0, tk.END)

    # ================= SAVE =================
    def save_distributor():
        did = distributor_id_entry.get()
        name = name_entry.get()
        phone = phone_entry.get()
        address = address_entry.get()

        if not name:
            messagebox.showerror("Error", "Name is required")
            return

        # Validate phone number (must be 10 digits)
        is_valid, error_msg = validate_phone_number(phone)
        if not is_valid:
            messagebox.showerror("Error", error_msg)
            return

        success = add_distributor(did, name, phone, address)

        if success:
            messagebox.showinfo("Success", "Distributor Added Successfully")
            refresh_table()
            new_distributor()
        else:
            messagebox.showerror("Error", "Distributor ID already exists")

    # ================= UPDATE =================
    def update_distributor():
        did = distributor_id_entry.get()
        phone = phone_entry.get()
        address = address_entry.get()

        # Validate phone number (must be 10 digits)
        is_valid, error_msg = validate_phone_number(phone)
        if not is_valid:
            messagebox.showerror("Error", error_msg)
            return

        success = update_distributor_by_id(did, phone, address)

        if success:
            messagebox.showinfo("Success", "Distributor Updated Successfully")
            refresh_table()
        else:
            messagebox.showerror("Error", "Update Failed")

    # ================= BUTTONS =================
    btn_frame = tk.Frame(form_frame, bg="white")
    btn_frame.grid(row=4, columnspan=2, pady=15)

    tk.Button(btn_frame, text="New", width=10, bg="#1e88e5", fg="white",
              command=new_distributor).grid(row=0, column=0, padx=5)

    tk.Button(btn_frame, text="Save", width=10, bg="#43a047", fg="white",
              command=save_distributor).grid(row=0, column=1, padx=5)

    tk.Button(btn_frame, text="Update", width=10, bg="#fb8c00", fg="white",
              command=update_distributor).grid(row=0, column=2, padx=5)

    # ================= RIGHT SIDE TABLE =================
    table_frame = tk.Frame(main_frame, bg="white")
    table_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

    # ===== SEARCH BAR =====
    tk.Label(
        table_frame,
        text="Search Distributor",
        bg="white",
        font=("Segoe UI", 10)
    ).pack(anchor="w")

    search_var = tk.StringVar()
    search_entry = tk.Entry(table_frame, textvariable=search_var, width=40)
    search_entry.pack(pady=5)

    # ================= TABLE =================
    columns = ("ID", "Name", "Phone", "Address")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=140)

    tree.pack(fill="both", expand=True)

    # Add scrollbar
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")

    # Context menu for right-click copy
    def get_selected_row_data(tree):
        selected = tree.selection()
        if not selected:
            return ""
        data = []
        for item in selected:
            values = tree.item(item, "values")
            data.append("\t".join(str(v) for v in values))
        return "\n".join(data)
    
    from tkinter import Menu
    def create_context_menu(root, tree=None):
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
    
    context_menu = create_context_menu(table_frame, tree=tree)
    tree.bind("<Button-3>", lambda e: show_context_menu(e, context_menu))

    # ================= LOAD TABLE =================
    def load_table(data):
        tree.delete(*tree.get_children())
        for dist in data:
            tree.insert("", "end", values=(
                dist["distributor_id"],
                dist["distributor_name"],
                dist["phone_number"],
                dist["address"]
            ))

    # ================= REFRESH =================
    def refresh_table():
        distributors = get_all_distributors()
        load_table(distributors)

    # ================= SEARCH FILTER =================
    def filter_distributors(*args):
        search_text = search_var.get().lower()
        distributors = get_all_distributors()

        filtered = [
            d for d in distributors
            if search_text in d["distributor_name"].lower()
        ]

        load_table(filtered)

    search_var.trace("w", filter_distributors)

    # ================= SELECT ROW =================
    def on_row_select(event):
        selected_item = tree.focus()
        if not selected_item:
            return

        values = tree.item(selected_item)["values"]

        distributor_id_entry.config(state="normal")
        distributor_id_entry.delete(0, tk.END)
        distributor_id_entry.insert(0, values[0])
        distributor_id_entry.config(state="readonly")

        name_entry.delete(0, tk.END)
        name_entry.insert(0, values[1])

        phone_entry.delete(0, tk.END)
        phone_entry.insert(0, values[2])

        address_entry.delete(0, tk.END)
        address_entry.insert(0, values[3])
        
        

    tree.bind("<<TreeviewSelect>>", on_row_select)

    # ================= INITIAL LOAD =================
    new_distributor()
    refresh_table()
