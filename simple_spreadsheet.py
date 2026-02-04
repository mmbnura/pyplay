import ast
import string
import tkinter as tk
from tkinter import ttk

ROWS = 10
COLS = 8


class SpreadsheetApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Spreadsheet")
        self.geometry("900x500")
        self.resizable(False, False)

        self.cell_inputs = [["" for _ in range(COLS)] for _ in range(ROWS)]
        self.cell_vars = [[tk.StringVar() for _ in range(COLS)] for _ in range(ROWS)]
        self.entries = [[None for _ in range(COLS)] for _ in range(ROWS)]

        self._build_ui()
        self.recalculate()

    def _build_ui(self):
        header_frame = ttk.Frame(self, padding=10)
        header_frame.pack(fill="x")

        title = ttk.Label(
            header_frame,
            text="Simple Spreadsheet",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(side="left")

        hint = ttk.Label(
            header_frame,
            text="Tip: Use formulas like =A1+B2 or =A1*10",
            foreground="#4b5563",
        )
        hint.pack(side="right")

        control_frame = ttk.Frame(self, padding=(10, 0, 10, 10))
        control_frame.pack(fill="x")

        recalc_button = ttk.Button(control_frame, text="Recalculate", command=self.recalculate)
        recalc_button.pack(side="left")

        clear_button = ttk.Button(control_frame, text="Clear All", command=self.clear_all)
        clear_button.pack(side="left", padx=8)

        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill="both", expand=True)

        table_frame.columnconfigure(0, weight=0)
        for col in range(1, COLS + 1):
            table_frame.columnconfigure(col, weight=1)

        for col in range(COLS):
            label = ttk.Label(
                table_frame,
                text=string.ascii_uppercase[col],
                anchor="center",
                font=("Segoe UI", 10, "bold"),
            )
            label.grid(row=0, column=col + 1, sticky="nsew", padx=2, pady=2)

        for row in range(ROWS):
            row_label = ttk.Label(
                table_frame,
                text=str(row + 1),
                anchor="center",
                font=("Segoe UI", 10, "bold"),
            )
            row_label.grid(row=row + 1, column=0, sticky="nsew", padx=2, pady=2)

            for col in range(COLS):
                entry = ttk.Entry(table_frame, textvariable=self.cell_vars[row][col], width=12)
                entry.grid(row=row + 1, column=col + 1, sticky="nsew", padx=2, pady=2)
                entry.bind("<FocusIn>", lambda event, r=row, c=col: self.on_focus_in(r, c))
                entry.bind("<FocusOut>", lambda event, r=row, c=col: self.on_focus_out(r, c))
                entry.bind("<Return>", lambda event, r=row, c=col: self.on_return(event, r, c))
                self.entries[row][col] = entry

    def clear_all(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.cell_inputs[row][col] = ""
                self.cell_vars[row][col].set("")
        self.recalculate()

    def on_focus_in(self, row, col):
        raw = self.cell_inputs[row][col]
        if raw:
            self.cell_vars[row][col].set(raw)

    def on_focus_out(self, row, col):
        raw = self.cell_vars[row][col].get().strip()
        self.cell_inputs[row][col] = raw
        self.recalculate()

    def on_return(self, event, row, col):
        self.on_focus_out(row, col)
        next_row = min(row + 1, ROWS - 1)
        self.entries[next_row][col].focus_set()
        return "break"

    def recalculate(self):
        memo = {}
        visiting = set()

        def resolve_name(name):
            index = self._name_to_index(name)
            if index is None:
                return 0
            return evaluate_cell(*index)

        def evaluate_cell(row, col):
            cell_name = self._index_to_name(row, col)
            if cell_name in memo:
                return memo[cell_name]
            if cell_name in visiting:
                return 0
            visiting.add(cell_name)

            raw = self.cell_inputs[row][col].strip()
            if raw.startswith("="):
                try:
                    value = self._safe_eval(raw[1:], resolve_name)
                except Exception:
                    value = "ERR"
            else:
                value = self._parse_literal(raw)

            memo[cell_name] = value
            visiting.remove(cell_name)
            return value

        for row in range(ROWS):
            for col in range(COLS):
                value = evaluate_cell(row, col)
                self.cell_vars[row][col].set(self._format_display(value))

    @staticmethod
    def _parse_literal(raw):
        if raw == "":
            return ""
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            return raw

    @staticmethod
    def _format_display(value):
        if isinstance(value, float):
            return f"{value:.2f}".rstrip("0").rstrip(".")
        return str(value)

    @staticmethod
    def _safe_eval(expression, resolve_name):
        tree = ast.parse(expression, mode="eval")

        def eval_node(node):
            if isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                if isinstance(node.op, ast.Add):
                    return left + right
                if isinstance(node.op, ast.Sub):
                    return left - right
                if isinstance(node.op, ast.Mult):
                    return left * right
                if isinstance(node.op, ast.Div):
                    return left / right
                raise ValueError("Unsupported operator")
            if isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                if isinstance(node.op, ast.UAdd):
                    return +operand
                if isinstance(node.op, ast.USub):
                    return -operand
                raise ValueError("Unsupported unary operator")
            if isinstance(node, ast.Name):
                return resolve_name(node.id)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Unsupported expression")

        return eval_node(tree.body)

    @staticmethod
    def _name_to_index(name):
        if len(name) < 2:
            return None
        col_letter = name[0].upper()
        if col_letter not in string.ascii_uppercase[:COLS]:
            return None
        try:
            row_num = int(name[1:]) - 1
        except ValueError:
            return None
        col = string.ascii_uppercase.index(col_letter)
        if row_num < 0 or row_num >= ROWS:
            return None
        return row_num, col

    @staticmethod
    def _index_to_name(row, col):
        return f"{string.ascii_uppercase[col]}{row + 1}"


if __name__ == "__main__":
    app = SpreadsheetApp()
    app.mainloop()
