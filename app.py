import sys
import subprocess
import tkinter as tk
from tkinter import ttk

# ---------------- REQUIREMENTS CHECK ---------------- #

def is_installed(package):
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", package],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0


def install_requirements(requirements_file="requirements.txt"):
    try:
        with open(requirements_file, "r") as f:
            requirements = [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    except FileNotFoundError:
        return

    for package in requirements:
        pkg_name = package.split("==")[0]
        if not is_installed(pkg_name):
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package]
            )

install_requirements()

# ---------------- IMPORT UI MODULES ---------------- #

from ui.ui_store import store_ui
from ui.ui_customer import customer_ui
from ui.ui_credit import credit_ui
from ui.ui_billing import billing_ui
from ui.ui_expiry_alert import expiry_alert_ui
from ui.ui_distributor_master import distributor_master_ui
from ui.ui_distributor_payment import distributor_payment_ui
from ui.ui_store_list import store_list_ui
from ui.ui_customer_balance import customer_balance_ui


# ---------------- SCREEN LOADER ---------------- #

def load_screen(parent, screen_func):
    # Clear previous screen
    for widget in parent.winfo_children():
        widget.destroy()

    # Load new screen
    screen_func(parent)


# ---------------- MAIN UI ---------------- #

def main():
    root = tk.Tk()
    root.title("Gita Medical Hall – ERP")
    root.state("zoomed")
    root.configure(bg="#f5f7fa")

    # Set window icon
    try:
        root.iconbitmap("logo.ico")
    except Exception:
        pass  # If icon not found, continue without it

    # Global UI fonts and styles
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass

    FONT_APP_TITLE = ("Segoe UI", 20, "bold")
    FONT_APP_SUB = ("Segoe UI", 11)
    style.configure('Header.TLabel', background="#0bbcd6", foreground="#ffffff", font=FONT_APP_TITLE)
    style.configure('Header.Sub.TLabel', background="#0bbcd6", foreground="#ffffff", font=FONT_APP_SUB)

    style.configure('Sidebar.TFrame', background='white')
    style.configure('Sidebar.TButton', font=("Segoe UI", 11), background='white', foreground='#333333')
    style.map('Sidebar.TButton', background=[('active', '#eef6fb')])

    style.configure('Primary.TButton', font=("Segoe UI", 12, 'bold'), foreground="#ffffff", background="#2b6ed5")

    # ---------------- HEADER ---------------- #
    header = tk.Frame(root, bg="#0bbcd6", height=70)
    header.pack(fill="x")

    ttk.Label(
        header,
        text="GITA MEDICAL HALL",
        style='Header.TLabel'
    ).pack(side="left", padx=30, pady=12)

    ttk.Label(
        header,
        text="Pharmacy Management System",
        style='Header.Sub.TLabel'
    ).pack(side="left", padx=10, pady=22)

    # ---------------- MAIN CONTAINER ---------------- #
    main_container = tk.Frame(root, bg="#f5f7fa")
    main_container.pack(fill="both", expand=True)

    # ---------------- SIDEBAR ---------------- #
    sidebar = ttk.Frame(main_container, style='Sidebar.TFrame', width=260)
    sidebar.pack(fill="y", side="left")
    sidebar.pack_propagate(False)

    def menu_section(text):
        ttk.Label(
            sidebar,
            text=text,
            background='white',
            foreground="#666666",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 6))

    def menu_button(text, command):
        btn = ttk.Button(sidebar, text=text, style='Sidebar.TButton', command=command)
        btn.pack(fill="x", padx=8, pady=2)
        return btn

    # ---------------- CONTENT AREA ---------------- #
    content = tk.Frame(main_container, bg="#f5f7fa")
    content.pack(fill="both", expand=True)

    # ---------------- MENU ITEMS ---------------- #
    menu_section("STORE & SALES")
    menu_button("🧾  Store Entry",
                lambda: load_screen(content, store_ui))
    menu_button("📋  Store List",
                lambda: load_screen(content, store_list_ui))
    menu_button("👤  Customer Entry",
                lambda: load_screen(content, customer_ui))
    menu_button("📊  Customer Balance",
            lambda: load_screen(content, customer_balance_ui))
    menu_button("💳  Credit / Debit",
                lambda: load_screen(content, credit_ui))
    menu_button("🛒  Create Bill",
                lambda: load_screen(content, billing_ui))

    menu_section("DISTRIBUTOR")
    menu_button("🏭  Distributor Master",
                lambda: load_screen(content, distributor_master_ui))
    menu_button("💰  Distributor Payment",
                lambda: load_screen(content, distributor_payment_ui))

    menu_section("ALERTS")
    menu_button("⏰  Expiry Alerts",
                lambda: load_screen(content, expiry_alert_ui))

    # ---------------- DEFAULT HOME ---------------- #
    tk.Label(
        content,
        text="Welcome to Gita Medical Hall ERP",
        bg="#f5f7fa",
        fg="#333333",
        font=("Segoe UI", 20, "bold")
    ).pack(pady=60)

    tk.Label(
        content,
        text="Select an option from the left menu to continue",
        bg="#f5f7fa",
        fg="#666666",
        font=("Segoe UI", 12)
    ).pack()

    root.mainloop()


if __name__ == "__main__":
    main()
