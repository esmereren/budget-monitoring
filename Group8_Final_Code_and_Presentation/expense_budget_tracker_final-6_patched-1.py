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


def list_categories():
    if not CATEGORY_RULES:
        print("No categories defined.")
        return
    print("-" * 60)
    print(f"{'No.':>3s}  {'Category':20s}  Keywords")
    print("-" * 60)
    for i, (category, keywords) in enumerate(CATEGORY_RULES, start=1):
        keywords_text = ", ".join(keywords)
        print(f"{i:3d}  {category:20s}  {keywords_text}")
    print("-" * 60)


def add_category_interactive():
    category = input("Category name: ").strip()
    if not category:
        print("Invalid category name.")
        return
    for existing, _ in CATEGORY_RULES:
        if existing.lower() == category.lower():
            print("Category already exists.")
            return
    keywords_input = input("Keywords (comma separated): ").strip()
    keywords = [kw.strip().lower() for kw in keywords_input.split(",") if kw.strip()]
    if not keywords:
        print("At least one keyword is required.")
        return
    CATEGORY_RULES.append((category, keywords))
    print(f"Category '{category}' added.")


def delete_category_interactive():
    if not CATEGORY_RULES:
        print("No categories to delete.")
        return
    list_categories()
    choice = input("Select category number to delete: ").strip()
    if not choice.isdigit():
        print("Invalid selection.")
        return
    idx = int(choice) - 1
    if idx < 0 or idx >= len(CATEGORY_RULES):
        print("Selection out of range.")
        return
    category, _ = CATEGORY_RULES[idx]
    confirm = input(f"Delete category '{category}'? (y/N): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return
    CATEGORY_RULES.pop(idx)
    print(f"Category '{category}' deleted.")


def edit_category_interactive():
    if not CATEGORY_RULES:
        print("No categories to edit.")
        return
    list_categories()
    choice = input("Select category number to edit: ").strip()
    if not choice.isdigit():
        print("Invalid selection.")
        return
    idx = int(choice) - 1
    if idx < 0 or idx >= len(CATEGORY_RULES):
        print("Selection out of range.")
        return

    old_category, old_keywords = CATEGORY_RULES[idx]

    new_category = input(f"New category name (enter to keep '{old_category}'): ").strip()
    if not new_category:
        new_category = old_category
    else:
        for existing, _ in CATEGORY_RULES:
            if existing.lower() == new_category.lower() and existing.lower() != old_category.lower():
                print("Category already exists. Edit cancelled.")
                return

    keywords_input = input(
        f"New keywords (comma separated, enter to keep '{', '.join(old_keywords)}'): "
    ).strip()
    if keywords_input:
        new_keywords = [kw.strip().lower() for kw in keywords_input.split(",") if kw.strip()]
        if not new_keywords:
            print("At least one keyword is required. Edit cancelled.")
            return
    else:
        new_keywords = old_keywords

    CATEGORY_RULES[idx] = (new_category, new_keywords)

    if new_category != old_category:
        for rec in expenses:
            if rec[IDX_CATEGORY] == old_category:
                rec[IDX_CATEGORY] = new_category
        for month, budgets in budgets_by_month.items():
            if old_category in budgets:
                old_value = budgets.pop(old_category)
                if new_category in budgets:
                    print(
                        f"Warning: budget already exists for '{new_category}' in {month}. "
                        "Keeping existing value."
                    )
                else:
                    budgets[new_category] = old_value

    print("Category updated.")


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

        month_raw = parts[0]
        cat = parts[1]
        value = safe_float(parts[2])

        month_str = extract_month(month_raw)
        if month_str is None or not cat or value is None:
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


def list_budgets_for_month(month_input: str):
    items = get_budget_items_for_month(month_input)
    if not items:
        print(f"No budgets found for month '{month_input}'.")
        return
    print("-" * 50)
    print(f"Budgets for {month_input}")
    print("-" * 50)
    print(f"{'Category':20s} {'Budget':>10s}")
    print("-" * 50)
    for cat, value in items:
        print(f"{cat:20s} {value:10.2f}")
    print("-" * 50)


def get_budget_items_for_month(month_input: str):
    month_budgets = budgets_by_month.get(month_input, {})
    return sorted(month_budgets.items(), key=lambda item: item[0].lower())


def list_budgets_for_month_with_numbers(month_input: str):
    items = get_budget_items_for_month(month_input)
    if not items:
        print(f"No budgets found for month '{month_input}'.")
        return []
    print("-" * 60)
    print(f"Budgets for {month_input}")
    print("-" * 60)
    print(f"{'No.':>3s}  {'Category':20s} {'Budget':>10s}")
    print("-" * 60)
    for i, (cat, value) in enumerate(items, start=1):
        print(f"{i:3d}  {cat:20s} {value:10.2f}")
    print("-" * 60)
    return items


def list_all_budgets():
    if not budgets_by_month:
        print("No budgets to display.")
        return
    for month in sorted(budgets_by_month.keys()):
        list_budgets_for_month(month)


def add_budget_interactive():
    while True:
        month_input = input("Month (YYYY-MM) (enter to stop): ").strip()
        if not month_input:
            return
        if extract_month(month_input) is None:
            print("Invalid month format.")
            continue
        break

    # Normalize month (also accepts YYYY-MM-DD input)
    month_input = extract_month(month_input)

    while True:
        cat = input("Category (enter to stop): ").strip()
        if not cat:
            return
        amount_txt = input("Budget amount: ").strip()
        amount_val = safe_float(amount_txt)
        if amount_val is None:
            print("Invalid amount.")
            continue
        if month_input not in budgets_by_month:
            budgets_by_month[month_input] = {}
        budgets_by_month[month_input][cat] = round(amount_val, 2)
        print(f"Budget saved for {month_input} / {cat}.")


def edit_budget_interactive():
    month_raw = input("Enter month (YYYY-MM): ").strip()
    month_input = extract_month(month_raw)
    if month_input is None:
        print("Invalid month format.")
        return
    items = list_budgets_for_month_with_numbers(month_input)
    if not items:
        return
    choice = input("Select budget number to edit: ").strip()
    if not choice.isdigit():
        print("Invalid selection.")
        return
    idx = int(choice) - 1
    if idx < 0 or idx >= len(items):
        print("Selection out of range.")
        return

    old_cat, old_value = items[idx]

    new_cat = input(f"New category (enter to keep '{old_cat}'): ").strip()
    if not new_cat:
        new_cat = old_cat

    new_amount = input(f"New budget amount (enter to keep '{old_value:.2f}'): ").strip()
    if new_amount:
        amount_val = safe_float(new_amount)
        if amount_val is None:
            print("Invalid amount. Edit cancelled.")
            return
        new_value = round(amount_val, 2)
    else:
        new_value = old_value

    if new_cat != old_cat:
        del budgets_by_month[month_input][old_cat]
    budgets_by_month[month_input][new_cat] = new_value
    print("Budget updated.")


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
    m_raw = input("Select month (YYYY-MM): ").strip()
    m = extract_month(m_raw)
    if m is None:
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
    month_raw = input("Enter month (YYYY-MM): ").strip()
    month_input = extract_month(month_raw)
    if month_input is None:
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
    print(
        "\n"
        "===============================\n"
        "Expense & Budget Monitor (Menu)\n"
        "===============================\n"
        "1  - Expenses\n"
        "2  - Budgets\n"
        "3  - Categories\n"
        "4  - Select analysis month (YYYY-MM)\n"
        "5  - Show monthly summary\n"
        "6  - Plot spending by category (optional)\n"
        "0  - Exit\n"
    )


def show_expenses_menu():
    print(
        "\n"
        "=================\n"
        "Expenses (Menu)\n"
        "=================\n"
        "1  - Load expenses from CSV\n"
        "2  - Save expenses to CSV\n"
        "3  - Delete all expenses\n"
        "4  - List expenses (selected month)\n"
        "5  - List expenses (all)\n"
        "6  - Add expense (manual)\n"
        "7  - Edit expense (selected month)\n"
        "0  - Back\n"
    )


def show_budgets_menu():
    print(
        "\n"
        "================\n"
        "Budgets (Menu)\n"
        "================\n"
        "1  - Load budgets from CSV\n"
        "2  - Save budgets to CSV\n"
        "3  - Delete all budgets\n"
        "4  - List budgets (selected month)\n"
        "5  - List budgets (all)\n"
        "6  - Add budget (manual)\n"
        "7  - Edit budget (selected month)\n"
        "0  - Back\n"
    )


def show_categories_menu():
    print(
        "\n"
        "=================\n"
        "Categories (Menu)\n"
        "=================\n"
        "1  - List categories\n"
        "2  - Add category\n"
        "3  - Edit category\n"
        "4  - Delete category\n"
        "0  - Back\n"
    )


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
            month_raw = input("Enter month (YYYY-MM): ").strip()
            month_input = extract_month(month_raw)
            if month_input is None:
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


def handle_categories_menu():
    while True:
        show_categories_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            list_categories()
        elif choice == "2":
            add_category_interactive()
        elif choice == "3":
            edit_category_interactive()
        elif choice == "4":
            delete_category_interactive()
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
            delete_all_budgets()
        elif choice == "4":
            month_raw = input("Enter month (YYYY-MM): ").strip()
            month_input = extract_month(month_raw)
            if month_input is None:
                print("Invalid month format.")
            else:
                list_budgets_for_month(month_input)
        elif choice == "5":
            list_all_budgets()
        elif choice == "6":
            add_budget_interactive()
        elif choice == "7":
            edit_budget_interactive()
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
            handle_categories_menu()
        elif choice == "4":
            select_month_interactive()
        elif choice == "5":
            show_monthly_summary()
        elif choice == "6":
            plot_spending_by_category()
        elif choice == "0":
            print("Good bye")
            break
        else:
            print("Invalid selection. Please choose a valid menu number.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGood bye")
