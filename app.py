import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt

from database import (
    init_db,
    add_expense,
    get_expenses,
    update_expense,
    delete_expense,
    get_summary,
    get_category_summary,
    get_monthly_summary
)

CATEGORIES = [
    "Food", "Travel", "Education", "Shopping",
    "Bills", "Entertainment", "Health", "Other"
]


class ExpenseTracker(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Student Expense Tracker & Analytics")
        self.geometry("1050x650")
        self.minsize(900, 580)

        self.selected_id = None

        self.build_ui()
        self.refresh_all()

    def build_ui(self):
        title = ttk.Label(
            self,
            text="Student Expense Tracker & Analytics",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=(12, 8))

        # Expense form
        form = ttk.LabelFrame(self, text="Expense Details", padding=10)
        form.pack(fill="x", padx=15, pady=5)

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )

        self.date_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d")
        )
        ttk.Entry(
            form, textvariable=self.date_var, width=18
        ).grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Category").grid(
            row=0, column=2, sticky="w", padx=5
        )

        self.category_var = tk.StringVar(value=CATEGORIES[0])
        ttk.Combobox(
            form,
            textvariable=self.category_var,
            values=CATEGORIES,
            state="readonly",
            width=16
        ).grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Amount (₹)").grid(
            row=0, column=4, sticky="w", padx=5
        )

        self.amount_var = tk.StringVar()
        ttk.Entry(
            form, textvariable=self.amount_var, width=15
        ).grid(row=0, column=5, padx=5)

        ttk.Label(form, text="Description").grid(
            row=0, column=6, sticky="w", padx=5
        )

        self.description_var = tk.StringVar()
        ttk.Entry(
            form, textvariable=self.description_var, width=28
        ).grid(row=0, column=7, padx=5)

        buttons = ttk.Frame(form)
        buttons.grid(row=1, column=0, columnspan=8, pady=8)

        ttk.Button(
            buttons, text="Add Expense", command=self.add
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons, text="Update Selected", command=self.update
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons, text="Delete Selected", command=self.delete
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons, text="Clear", command=self.clear_form
        ).pack(side="left", padx=5)

        # Search and analytics buttons
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=15, pady=8)

        ttk.Label(search_frame, text="Search:").pack(side="left")

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=35
        )
        search_entry.pack(side="left", padx=8)

        search_entry.bind(
            "<KeyRelease>",
            lambda event: self.refresh_table()
        )

        ttk.Button(
            search_frame,
            text="Refresh",
            command=self.refresh_all
        ).pack(side="left", padx=5)

        ttk.Button(
            search_frame,
            text="View Analytics",
            command=self.show_analytics
        ).pack(side="left", padx=5)

        # Expense table
        table_frame = ttk.Frame(self)
        table_frame.pack(
            fill="both", expand=True, padx=15, pady=5
        )

        columns = (
            "id", "date", "category", "amount", "description"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=14
        )

        headings = {
            "id": "ID",
            "date": "Date",
            "category": "Category",
            "amount": "Amount (₹)",
            "description": "Description"
        }

        widths = {
            "id": 50,
            "date": 120,
            "category": 150,
            "amount": 130,
            "description": 400
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(
                col, width=widths[col], anchor="center"
            )

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind(
            "<<TreeviewSelect>>", self.load_selected
        )

        # Summary section
        summary = ttk.LabelFrame(
            self, text="Analytics Summary", padding=10
        )
        summary.pack(
            fill="x", padx=15, pady=(5, 12)
        )

        self.total_label = ttk.Label(
            summary,
            text="Total: ₹0.00",
            font=("Arial", 11, "bold")
        )
        self.total_label.pack(side="left", padx=20)

        self.month_label = ttk.Label(
            summary,
            text="This Month: ₹0.00",
            font=("Arial", 11, "bold")
        )
        self.month_label.pack(side="left", padx=20)

        self.category_label = ttk.Label(
            summary,
            text="Top Category: -",
            font=("Arial", 11, "bold")
        )
        self.category_label.pack(side="left", padx=20)

    def validate(self):
        date_text = self.date_var.get().strip()
        amount_text = self.amount_var.get().strip()
        description = self.description_var.get().strip()
        category = self.category_var.get()

        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Enter a valid date in YYYY-MM-DD format."
            )
            return None

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Amount",
                "Enter a positive numeric amount."
            )
            return None

        if category not in CATEGORIES:
            messagebox.showerror(
                "Invalid Category", "Select a valid category."
            )
            return None

        if not description:
            messagebox.showerror(
                "Missing Description",
                "Enter an expense description."
            )
            return None

        return date_text, category, amount, description

    def add(self):
        data = self.validate()

        if data:
            add_expense(*data)
            self.refresh_all()
            self.clear_form()

            messagebox.showinfo(
                "Success", "Expense added successfully."
            )

    def update(self):
        if self.selected_id is None:
            messagebox.showwarning(
                "Select Expense",
                "Select an expense from the table first."
            )
            return

        data = self.validate()

        if data:
            update_expense(self.selected_id, *data)
            self.refresh_all()
            self.clear_form()

            messagebox.showinfo(
                "Success", "Expense updated successfully."
            )

    def delete(self):
        if self.selected_id is None:
            messagebox.showwarning(
                "Select Expense",
                "Select an expense from the table first."
            )
            return

        if messagebox.askyesno(
            "Confirm Delete",
            "Delete the selected expense?"
        ):
            delete_expense(self.selected_id)
            self.refresh_all()
            self.clear_form()

    def clear_form(self):
        self.selected_id = None

        self.date_var.set(
            datetime.now().strftime("%Y-%m-%d")
        )
        self.category_var.set(CATEGORIES[0])
        self.amount_var.set("")
        self.description_var.set("")

        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def load_selected(self, event=None):
        selection = self.tree.selection()

        if not selection:
            return

        values = self.tree.item(
            selection[0], "values"
        )

        self.selected_id = int(values[0])
        self.date_var.set(values[1])
        self.category_var.set(values[2])
        self.amount_var.set(values[3])
        self.description_var.set(values[4])

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search = self.search_var.get().strip()

        for row in get_expenses(search):
            self.tree.insert("", "end", values=row)

    def refresh_summary(self):
        total, month_total, top_category = get_summary()

        self.total_label.config(
            text=f"Total: ₹{total:,.2f}"
        )

        self.month_label.config(
            text=f"This Month: ₹{month_total:,.2f}"
        )

        self.category_label.config(
            text=f"Top Category: {top_category or '-'}"
        )

    def refresh_all(self):
        self.refresh_table()
        self.refresh_summary()

    def show_analytics(self):
        category_data = get_category_summary()
        monthly_data = get_monthly_summary()

        if not category_data and not monthly_data:
            messagebox.showinfo(
                "Analytics",
                "No expense data available. Add an expense first."
            )
            return

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Category-wise bar chart
        if category_data:
            categories = [row[0] for row in category_data]
            amounts = [row[1] for row in category_data]

            axes[0].bar(categories, amounts)
            axes[0].set_title("Category-wise Expenses")
            axes[0].set_xlabel("Category")
            axes[0].set_ylabel("Amount (₹)")
            axes[0].tick_params(
                axis="x", labelrotation=45
            )
        else:
            axes[0].set_title("No Category Data")

        # Monthly expense line chart
        if monthly_data:
            months = [row[0] for row in monthly_data]
            amounts = [row[1] for row in monthly_data]

            axes[1].plot(months, amounts, marker="o")
            axes[1].set_title("Monthly Expenses")
            axes[1].set_xlabel("Month")
            axes[1].set_ylabel("Amount (₹)")
            axes[1].tick_params(
                axis="x", labelrotation=45
            )
        else:
            axes[1].set_title("No Monthly Data")

        fig.tight_layout()
        plt.show()


if __name__ == "__main__":
    init_db()
    app = ExpenseTracker()
    app.mainloop()
