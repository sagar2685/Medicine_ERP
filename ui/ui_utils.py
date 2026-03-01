"""
UI Utilities Module - Shared functionality for all UI components
Includes: Copy to clipboard, professional styling, context menus
"""
import tkinter as tk
from tkinter import ttk
import pyperclip


# ==================== COLOR THEME ====================
class Colors:
    """Professional color scheme for the application"""
    PRIMARY = "#0d6efd"
    PRIMARY_HOVER = "#0b5ed7"
    SECONDARY = "#6c757d"
    SUCCESS = "#198754"
    SUCCESS_HOVER = "#157347"
    DANGER = "#dc3545"
    DANGER_HOVER = "#bb2d3b"
    WARNING = "#ffc107"
    INFO = "#0dcaf0"
    
    BG_PRIMARY = "#f8f9fa"
    BG_CARD = "#ffffff"
    BG_SIDEBAR = "#ffffff"
    BG_HEADER = "#0d6efd"
    
    TEXT_PRIMARY = "#212529"
    TEXT_SECONDARY = "#6c757d"
    TEXT_LIGHT = "#ffffff"
    
    BORDER = "#dee2e6"
    BORDER_FOCUS = "#86b7fe"


# ==================== COPY FUNCTIONS ====================

def copy_to_clipboard(text):
    """Copy text to system clipboard"""
    try:
        pyperclip.copy(str(text))
        return True
    except Exception:
        # Fallback to tkinter clipboard
        try:
            root = tk.Tk()
            root.withdraw()
            root.clipboard_clear()
            root.clipboard_append(str(text))
            root.update()
            return True
        except Exception:
            return False


def get_treeview_data(tree):
    """Get all data from a Treeview as tab-separated string"""
    data = []
    for item in tree.get_children():
        values = tree.item(item, "values")
        data.append("\t".join(str(v) for v in values))
    return "\n".join(data)


def get_selected_row_data(tree):
    """Get selected row data as tab-separated string"""
    selected = tree.selection()
    if not selected:
        return ""
    
    data = []
    for item in selected:
        values = tree.item(item, "values")
        data.append("\t".join(str(v) for v in values))
    return "\n".join(data)


# ==================== CONTEXT MENU ====================

def create_context_menu(root, tree=None, extra_commands=None):
    """Create a right-click context menu with copy options"""
    menu = tk.Menu(root, tearoff=0, bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                   font=("Segoe UI", 10))
    
    # Copy selected row
    if tree:
        menu.add_command(label="📋 Copy Selected Row", 
                         command=lambda: copy_to_clipboard(get_selected_row_data(tree)))
        menu.add_command(label="📋 Copy All Data", 
                         command=lambda: copy_to_clipboard(get_treeview_data(tree)))
        
        if extra_commands:
            menu.add_separator()
            for label, cmd in extra_commands:
                menu.add_command(label=label, command=cmd)
    
    return menu


def show_context_menu(event, menu):
    """Display the context menu at cursor position"""
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()


# ==================== STYLING ====================

def setup_professional_style():
    """Setup professional ttk styles for the application"""
    style = ttk.Style()
    
    try:
        style.theme_use('clam')
    except Exception:
        pass
    
    # Configure Treeview style
    style.configure("Treeview",
                    background=Colors.BG_CARD,
                    foreground=Colors.TEXT_PRIMARY,
                    fieldbackground=Colors.BG_CARD,
                    font=("Segoe UI", 10),
                    rowheight=28)
    
    style.configure("Treeview.Heading",
                    background=Colors.BG_PRIMARY,
                    foreground=Colors.TEXT_PRIMARY,
                    font=("Segoe UI", 10, "bold"),
                    relief="flat")
    
    style.map("Treeview",
              background=[('selected', Colors.PRIMARY)],
              foreground=[('selected', Colors.TEXT_LIGHT)])
    
    # Configure TButton style
    style.configure("Primary.TButton",
                    font=("Segoe UI", 10, "bold"),
                    background=Colors.PRIMARY,
                    foreground=Colors.TEXT_LIGHT)
    
    style.map("Primary.TButton",
              background=[('active', Colors.PRIMARY_HOVER)])
    
    # Configure TFrame style
    style.configure("Card.TFrame",
                    background=Colors.BG_CARD,
                    relief="solid",
                    borderwidth=1)
    
    return style


def create_header(parent, title, subtitle=None):
    """Create a professional header with title and optional subtitle"""
    header = tk.Frame(parent, bg=Colors.BG_HEADER, height=70)
    header.pack(fill="x")
    
    title_label = tk.Label(
        header,
        text=title,
        font=("Segoe UI", 18, "bold"),
        bg=Colors.BG_HEADER,
        fg=Colors.TEXT_LIGHT
    )
    title_label.pack(side="left", padx=25, pady=15)
    
    if subtitle:
        subtitle_label = tk.Label(
            header,
            text=subtitle,
            font=("Segoe UI", 10),
            bg=Colors.BG_HEADER,
            fg="rgba(255,255,255,0.8)"
        )
        subtitle_label.pack(side="left", padx=(0, 25), pady=18)
    
    return header


def create_card(parent, padx=20, pady=15):
    """Create a professional card container"""
    card = tk.Frame(
        parent,
        bg=Colors.BG_CARD,
        relief="solid",
        bd=1,
        highlightbackground=Colors.BORDER,
        highlightthickness=1
    )
    card.pack(fill="both", expand=True, padx=padx, pady=pady)
    return card


def create_section_title(parent, text):
    """Create a section title label"""
    label = tk.Label(
        parent,
        text=text,
        font=("Segoe UI", 12, "bold"),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_PRIMARY
    )
    return label


def create_input_field(parent, label_text, row, column=0, colspan=1, width=30):
    """Create a labeled input field"""
    label = tk.Label(
        parent,
        text=label_text,
        font=("Segoe UI", 10),
        bg=Colors.BG_CARD,
        fg=Colors.TEXT_SECONDARY
    )
    label.grid(row=row, column=column, sticky="w", pady=(10, 5))
    
    entry = ttk.Entry(parent, width=width, font=("Segoe UI", 10))
    entry.grid(row=row + 1, column=column, columnspan=colspan, 
               sticky="w", padx=(0, 10), pady=(0, 10))
    
    return entry


def create_button_frame(parent):
    """Create a professional button frame"""
    frame = tk.Frame(parent, bg=Colors.BG_CARD)
    return frame


# ==================== MESSAGE BOXES ====================

def show_success(parent, message):
    """Show success message"""
    from tkinter import messagebox
    messagebox.showinfo("Success", message, parent=parent)


def show_error(parent, message):
    """Show error message"""
    from tkinter import messagebox
    messagebox.showerror("Error", message, parent=parent)


def show_warning(parent, message):
    """Show warning message"""
    from tkinter import messagebox
    messagebox.showwarning("Warning", message, parent=parent)


# ==================== TABLE HELPERS ====================

def create_treeview(parent, columns, headings=None, height=10):
    """Create a professional Treeview with scrollbars"""
    if headings is None:
        headings = [col.replace("_", " ").title() for col in columns]
    
    # Frame to hold tree and scrollbars
    frame = tk.Frame(parent, bg=Colors.BG_CARD)
    
    # Create Treeview
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    
    # Configure columns
    for i, col in enumerate(columns):
        tree.heading(col, text=headings[i])
        tree.column(col, anchor="w", width=120)
    
    # Vertical scrollbar
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    
    # Horizontal scrollbar
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=hsb.set)
    
    # Grid layout
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    
    return tree, frame


def populate_tree(tree, rows, columns):
    """Populate a Treeview with data"""
    tree.delete(*tree.get_children())
    for row in rows:
        if isinstance(row, dict):
            values = [row.get(col, "") for col in columns]
        else:
            values = list(row)
        tree.insert("", "end", values=values)
