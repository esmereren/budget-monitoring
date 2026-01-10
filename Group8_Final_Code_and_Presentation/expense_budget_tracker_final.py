import os

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

IDX_DATE = 0
IDX_DESC = 1
IDX_AMOUNT = 2
IDX_CATEGORY = 3
IDX_MONTH = 4

DEFAULT_CATEGORY = "Other"

CATEGORY_RULES = [
    ("Housing", ["rent", "mortgage", "utility", "utilities"]),
    ("Transport", ["uber", "taxi", "bus", "train", "metro", "tram"]),
    ("Food", ["coffee", "cafe", "restaurant", "grocery", "supermarket", "food"]),
    ("Entertainment", ["cinema", "movie", "concert", "subscription", "netflix", "spotify", "game"]),
]

expenses = []
budgets_by_month = {}
selected_month = None


def safe_float(text: str):
    s = text.strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def extract_month(date_str: str):
    s = date_str.strip()
    if len(s) < 7:
        return None
    if len(s) >= 5 and s[4] != "-":
        return None
    year = s[0:4]
    month = s[5:7]
    if (not year.isdigit()) or (not month.isdigit()):
        return None
    return s[0:7]


def categorize_expense(description: str):
    text = (description or "").lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return category
    return DEFAULT_CATEGORY


def load_expenses_csv(filename: str):
    loaded = 0
    skipped = 0
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return

    if not lines:
        print("File is empty.")
        return

    start_idx = 0
    header = lines[0].strip().lower().replace(" ", "")
    if header.startswith("date,") and "description" in header and "amount" in header:
        start_idx = 1

    for line in lines[start_idx:]:
        raw = line.strip()
        if not raw:
            continue

        parts = [p.strip() for p in raw.split(",")]
        if len(parts) < 3:
            skipped += 1
            continue

        date_str = parts[0]
        desc = parts[1]
        amount_val = safe_float(parts[2])

        month_val = extract_month(date_str)
        if amount_val is None or month_val is None:
            skipped += 1
            continue

        category = categorize_expense(desc)
        record = [date_str, desc, amount_val, category, month_val]
        expenses.append(record)
        loaded += 1

    print(f"Loaded {loaded} expense(s). Skipped {skipped} invalid row(s).")


def save_expenses_csv(filename: str):
    if not expenses:
        print("No expenses to save.")
        return
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("date,description,amount,category\n")
            for rec in expenses:
                date_str = rec[IDX_DATE]
                desc = rec[IDX_DESC].replace("\n", " ").replace("\r", " ")
                amount_val = rec[IDX_AMOUNT]
                cat = rec[IDX_CATEGORY]
                f.write(f"{date_str},{desc},{amount_val},{cat}\n")
        print(f"Saved {len(expenses)} expense(s) to '{filename}'.")
    except Exception as e:
        print(f"Error while saving expenses: {e}")


def delete_all_expenses():
    if not expenses:
        print("No expenses to delete.")
        return
    confirm = input("Delete all expenses? (y/N): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return
    expenses.clear()
    print("All expenses deleted.")


def load_budgets_csv(filename: str):
    loaded = 0
    skipped = 0
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return

    if not lines:
        print("File is empty.")
        return

    start_idx = 0
    header = lines[0].strip().lower().replace(" ", "")
    if header.startswith("month,") and "category" in header and "budget" in header:
        start_idx = 1

    for line in lines[start_idx:]:
        raw = line.strip()
        if not raw:
            continue

        parts = [p.strip() for p in raw.split(",")]
        if len(parts) < 3:
            skipped += 1
            continue

        month_str = parts[0]
        cat = parts[1]
        value = safe_float(parts[2])

        if extract_month(month_str) is None or not cat or value is None:
            skipped += 1
            continue

        if month_str not in budgets_by_month:
            budgets_by_month[month_str] = {}
        budgets_by_month[month_str][cat] = round(value, 2)
        loaded += 1

    print(f"Loaded {loaded} budget row(s). Skipped {skipped} invalid row(s).")


def save_budgets_csv(filename: str):
    if not budgets_by_month:
        print("No budgets to save.")
        return
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("month,category,budget\n")
            for month in sorted(budgets_by_month.keys()):
                for cat, value in budgets_by_month[month].items():
                    f.write(f"{month},{cat},{value}\n")
        print(f"Saved budgets to '{filename}'.")
    except Exception as e:
        print(f"Error while saving budgets: {e}")


def delete_all_budgets():
    if not budgets_by_month:
        print("No budgets to delete.")
        return
    confirm = input("Delete all budgets? (y/N): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return
    budgets_by_month.clear()
    print("All budgets deleted.")


def available_months():
    months = set()
    for rec in expenses:
        months.add(rec[IDX_MONTH])
    for m in budgets_by_month.keys():
        months.add(m)
    return sorted(months)


def select_month_interactive():
    global selected_month
    months = available_months()
    if not months:
        print("No months available. Load expenses and/or budgets first.")
        return
    print("Available months:", ", ".join(months))
    m = input("Select month (YYYY-MM): ").strip()
    if extract_month(m) is None:
        print("Invalid month format.")
        return
    selected_month = m
    print(f"Selected month: {selected_month}")


def get_expenses_for_selected_month():
    if selected_month is None:
        return []
    return [rec for rec in expenses if rec[IDX_MONTH] == selected_month]


def list_expenses(records):
    if not records:
        print("No expenses to display.")
        return
    print("-" * 80)
    print(f"{'No.':>3s}  {'Date':10s}  {'Category':14s}  {'Amount':>10s}  Description")
    print("-" * 80)
    for i, rec in enumerate(records, start=1):
        date_str = rec[IDX_DATE]
        cat = rec[IDX_CATEGORY]
        amt = rec[IDX_AMOUNT]
        desc = rec[IDX_DESC]
        print(f"{i:3d}  {date_str:10s}  {cat:14s}  {amt:10.2f}  {desc}")
    print("-" * 80)


def add_expense_interactive():
    date_str = input("Date (YYYY-MM-DD): ").strip()
    month_val = extract_month(date_str)
    if month_val is None:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    desc = input("Description: ").strip()
    amount_txt = input("Amount: ").strip()
    amount_val = safe_float(amount_txt)
    if amount_val is None:
        print("Invalid amount.")
        return

    cat = categorize_expense(desc)
    expenses.append([date_str, desc, amount_val, cat, month_val])
    print(f"Added expense in category '{cat}' (month {month_val}).")


def edit_expense_interactive():
    month_input = input("Enter month (YYYY-MM): ").strip()
    if extract_month(month_input) is None:
        print("Invalid month format.")
        return
    records = [rec for rec in expenses if rec[IDX_MONTH] == month_input]
    if not records:
        print(f"No expenses found for month '{month_input}'.")
        return

    list_expenses(records)
    choice = input("Select expense number to edit: ").strip()
    if not choice.isdigit():
        print("Invalid selection.")
        return
    idx = int(choice) - 1
    if idx < 0 or idx >= len(records):
        print("Selection out of range.")
        return

    rec = records[idx]

    new_date = input(f"New date (enter to keep '{rec[IDX_DATE]}'): ").strip()
    if new_date:
        month_val = extract_month(new_date)
        if month_val is None:
            print("Invalid date. Edit cancelled.")
            return
        rec[IDX_DATE] = new_date
        rec[IDX_MONTH] = month_val

    new_desc = input(f"New description (enter to keep current): ").strip()
    if new_desc:
        rec[IDX_DESC] = new_desc
        rec[IDX_CATEGORY] = categorize_expense(new_desc)

    new_amount = input(f"New amount (enter to keep '{rec[IDX_AMOUNT]:.2f}'): ").strip()
    if new_amount:
        amount_val = safe_float(new_amount)
        if amount_val is None:
            print("Invalid amount. Edit cancelled.")
            return
        rec[IDX_AMOUNT] = amount_val

    print("Expense updated.")


def calculate_totals(records):
    totals = {}
    for rec in records:
        cat = rec[IDX_CATEGORY]
        amt = rec[IDX_AMOUNT]
        totals[cat] = totals.get(cat, 0.0) + amt
    return totals


def all_categories_from_data_and_budgets(totals, month_budgets):
    cats = set(totals.keys()) | set(month_budgets.keys())
    return sorted(cats, key=str.lower)


def show_monthly_summary():
    if selected_month is None:
        print("No month selected. Please select a month first.")
        return
    records = get_expenses_for_selected_month()
    if not records:
        print(f"No expenses found for month '{selected_month}'.")
        return

    totals = calculate_totals(records)
    month_budgets = budgets_by_month.get(selected_month, {})
    categories = all_categories_from_data_and_budgets(totals, month_budgets)

    print("\n=== Monthly Summary ===")
    print(f"Month: {selected_month}")
    print("-" * 72)
    print(f"{'Category':18s} {'Budget':>10s} {'Spent':>10s} {'Remain':>10s}  Status")
    print("-" * 72)

    exceeded = []
    total_spent_all = 0.0
    total_budget_all = 0.0

    for cat in categories:
        spent = totals.get(cat, 0.0)
        budget = month_budgets.get(cat)
        total_spent_all += spent

        if budget is None:
            status = "NO BUDGET"
            remain_str = ""
            budget_str = ""
        else:
            total_budget_all += budget
            remain = budget - spent
            status = "OK" if remain >= 0 else "BUDGET EXCEEDED"
            if remain < 0:
                exceeded.append(cat)
            remain_str = f"{remain:10.2f}"
            budget_str = f"{budget:10.2f}"

        spent_str = f"{spent:10.2f}"
        print(f"{cat:18s} {budget_str:>10s} {spent_str:>10s} {remain_str:>10s}  {status}")

    print("-" * 72)
    if total_budget_all > 0:
        print(f"{'TOTAL':18s} {total_budget_all:10.2f} {total_spent_all:10.2f}")
    else:
        print(f"{'TOTAL':18s} {'':>10s} {total_spent_all:10.2f}")

    if exceeded:
        print("WARNING: Budget exceeded in:", ", ".join(exceeded))


def plot_spending_by_category():
    if not HAS_MPL:
        print("Matplotlib not available. Plotting is skipped.")
        return
    if selected_month is None:
        print("No month selected. Please select a month first.")
        return
    records = get_expenses_for_selected_month()
    if not records:
        print(f"No expenses found for month '{selected_month}'.")
        return

    totals = calculate_totals(records)
    cats = sorted(totals.keys(), key=str.lower)
    values = [totals[c] for c in cats]

    plt.figure(figsize=(8, 4))
    plt.bar(cats, values)
    plt.xlabel("Category")
    plt.ylabel("Total Spent")
    plt.title(f"Spending by Category ({selected_month})")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()


def show_main_menu():
    print("""
===============================
Expense & Budget Monitor (Menu)
===============================
1  - Expenses
2  - Budgets
3  - Select analysis month (YYYY-MM)
4  - Show monthly summary
5  - Plot spending by category (optional)
0  - Exit
""")


def show_expenses_menu():
    print("""
=================
Expenses (Menu)
=================
1  - Load expenses from CSV
2  - Save expenses to CSV
3  - Delete all expenses
4  - List expenses (selected month)
5  - List expenses (all)
6  - Add expense (manual)
7  - Edit expense (selected month)
0  - Back
""")


def show_budgets_menu():
    print("""
================
Budgets (Menu)
================
1  - Load budgets from CSV
2  - Save budgets to CSV
3  - List budgets (selected month)
4  - Delete all budgets
0  - Back
""")


def handle_expenses_menu():
    while True:
        show_expenses_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            fn = input("Expense CSV filename: ").strip()
            load_expenses_csv(fn)
        elif choice == "2":
            fn = input("Save expenses to filename: ").strip()
            save_expenses_csv(fn)
        elif choice == "3":
            delete_all_expenses()
        elif choice == "4":
            month_input = input("Enter month (YYYY-MM): ").strip()
            if extract_month(month_input) is None:
                print("Invalid month format.")
            else:
                records = [rec for rec in expenses if rec[IDX_MONTH] == month_input]
                list_expenses(records)
        elif choice == "5":
            list_expenses(expenses)
        elif choice == "6":
            add_expense_interactive()
        elif choice == "7":
            edit_expense_interactive()
        elif choice == "0":
            break
        else:
            print("Invalid selection. Please choose a valid menu number.")

        input("\nPress Enter to continue...")


def handle_budgets_menu():
    while True:
        show_budgets_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            fn = input("Budget CSV filename: ").strip()
            load_budgets_csv(fn)
        elif choice == "2":
            fn = input("Save budgets to filename: ").strip()
            save_budgets_csv(fn)
        elif choice == "3":
            month_input = input("Enter month (YYYY-MM): ").strip()
            if extract_month(month_input) is None:
                print("Invalid month format.")
            else:
                list_budgets_for_month(month_input)
        elif choice == "4":
            delete_all_budgets()
        elif choice == "0":
            break
        else:
            print("Invalid selection. Please choose a valid menu number.")

        input("\nPress Enter to continue...")


def main():
    while True:
        show_main_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            handle_expenses_menu()
        elif choice == "2":
            handle_budgets_menu()
        elif choice == "3":
            select_month_interactive()
        elif choice == "4":
            show_monthly_summary()
        elif choice == "5":
            plot_spending_by_category()
        elif choice == "0":
            print("Good bye")
            break
        else:
            print("Invalid selection. Please choose a valid menu number.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
