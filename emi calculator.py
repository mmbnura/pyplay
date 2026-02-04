import customtkinter as ctk
from tkinter import ttk, messagebox

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# ---------------- Indian Number Formatting ----------------
def format_indian_number(number):
    number = number.replace(",", "")
    if not number.isdigit():
        return number
    if len(number) <= 3:
        return number
    last3 = number[-3:]
    rest = number[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        parts.insert(0, rest)
    return ",".join(parts) + "," + last3

def on_loan_key_release(event):
    value = entry_loan.get()
    entry_loan.delete(0, "end")
    entry_loan.insert(0, format_indian_number(value))

# ---------------- EMI Calculation ----------------
def calculate_emi():
    try:
        principal = float(entry_loan.get().replace(",", ""))
        annual_rate = float(entry_rate.get())
        years = int(entry_years.get())

        if principal <= 0 or annual_rate <= 0 or years <= 0:
            raise ValueError

        # Clear previous table
        for row in tree.get_children():
            tree.delete(row)

        r = annual_rate / (12 * 100)
        n = years * 12

        emi = (principal * r * (1 + r) ** n) / ((1 + r) ** n - 1)
        balance = principal

        # Display EMI
        emi_var.set(f"₹ {emi:,.2f}")

        # Populate month-wise breakup
        for month in range(1, n + 1):
            interest = balance * r
            principal_component = emi - interest
            balance -= principal_component

            if balance < 0:
                balance = 0

            tree.insert(
                "",
                "end",
                values=(
                    month,
                    f"{emi:,.2f}",
                    f"{principal_component:,.2f}",
                    f"{interest:,.2f}",
                    f"{balance:,.2f}"
                )
            )

    except:
        messagebox.showerror("Invalid Input", "Please enter valid numeric values")

def reset_screen():
    entry_loan.delete(0, "end")
    entry_rate.delete(0, "end")
    entry_years.delete(0, "end")
    emi_var.set("₹ 0.00")
    for row in tree.get_children():
        tree.delete(row)

# ---------------- App Window ----------------
app = ctk.CTk()
app.title("EMI Calculator")
app.geometry("1100x650")
app.resizable(False, False)

main = ctk.CTkFrame(app, fg_color="#EEF4FF")
main.pack(fill="both", expand=True)

# ---------------- Left Panel ----------------
left = ctk.CTkFrame(main, width=420, corner_radius=24, fg_color="white")
left.pack(side="left", padx=30, pady=30, fill="y")

# ---------------- Right Panel ----------------
right = ctk.CTkFrame(main, corner_radius=24, fg_color="#E5E7EB")
right.pack(side="right", padx=30, pady=30, fill="both", expand=True)

# ---------------- Left Content ----------------
ctk.CTkLabel(
    left,
    text="EMI Calculator",
    font=ctk.CTkFont(size=22, weight="bold"),
    text_color="#1E3A8A"
).pack(pady=(30, 25))

entry_font = ctk.CTkFont(size=14)

def labeled_entry(parent, label, placeholder):
    ctk.CTkLabel(parent, text=label).pack(anchor="w", padx=30)
    e = ctk.CTkEntry(parent, height=44, font=entry_font, placeholder_text=placeholder)
    e.pack(fill="x", padx=30, pady=8)
    return e

entry_loan = labeled_entry(left, "Loan Amount (₹)", "e.g. 5,00,000")
entry_loan.bind("<KeyRelease>", on_loan_key_release)

entry_rate = labeled_entry(left, "Rate of Interest (% p.a.)", "e.g. 7")
entry_years = labeled_entry(left, "Tenure (Years)", "e.g. 10")

ctk.CTkButton(
    left,
    text="Calculate EMI",
    height=46,
    font=ctk.CTkFont(size=15, weight="bold"),
    fg_color="#2563EB",
    hover_color="#1E40AF",
    command=calculate_emi
).pack(pady=(20, 10))

# ---------------- Monthly EMI Display ----------------
ctk.CTkLabel(
    left,
    text="Monthly EMI",
    font=ctk.CTkFont(size=13, weight="bold"),
    text_color="#065F46"
).pack(anchor="w", padx=30, pady=(10, 2))

emi_var = ctk.StringVar(value="₹ 0.00")

ctk.CTkEntry(
    left,
    height=46,
    font=ctk.CTkFont(size=16, weight="bold"),
    textvariable=emi_var,
    state="readonly",
    fg_color="#E7F6EC",
    text_color="#047857",
    justify="center"
).pack(fill="x", padx=30, pady=(0, 25))

ctk.CTkButton(
    left,
    text="Reset",
    height=40,
    font=ctk.CTkFont(size=14, weight="bold"),
    fg_color="#9CA3AF",
    hover_color="#6B7280",
    command=reset_screen
).pack(pady=(5, 20))

# ---------------- Right Panel Table ----------------
ctk.CTkLabel(
    right,
    text="Month-wise EMI Breakup",
    font=ctk.CTkFont(size=18, weight="bold"),
    text_color="#1E3A8A"
).pack(pady=15)

table_frame = ctk.CTkFrame(right)
table_frame.pack(fill="both", expand=True, padx=15, pady=10)

scrollbar = ttk.Scrollbar(table_frame)
scrollbar.pack(side="right", fill="y")

style = ttk.Style()
style.configure("Treeview", font=("Segoe UI", 11), rowheight=26)
style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

tree = ttk.Treeview(
    table_frame,
    columns=("Month", "EMI", "Principal", "Interest", "Outstanding"),
    show="headings",
    yscrollcommand=scrollbar.set
)

scrollbar.config(command=tree.yview)

tree.heading("Month", text="Month")
tree.heading("EMI", text="EMI Amount")
tree.heading("Principal", text="Principal")
tree.heading("Interest", text="Interest")
tree.heading("Outstanding", text="Outstanding Principal")

tree.column("Month", width=70, anchor="center")
tree.column("EMI", width=120, anchor="e")
tree.column("Principal", width=120, anchor="e")
tree.column("Interest", width=120, anchor="e")
tree.column("Outstanding", width=150, anchor="e")

tree.pack(fill="both", expand=True)

app.mainloop()
