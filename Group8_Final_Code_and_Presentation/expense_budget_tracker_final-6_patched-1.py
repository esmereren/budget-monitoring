try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

"""
Tries to import matplotlib for plotting.
If successful → HAS_MPL = True
If not installed → program continues without crashing.
"""

IDX_DATE = 0
IDX_DESC = 1
IDX_AMOUNT = 2
IDX_CATEGORY = 3
IDX_MONTH = 4

"""
They define the structure of one expense record, which is stored as a list:

["2025-11-01", "Coffee at Cafe", 4.50, "Food", "2025-11"]

Index	Constant	Meaning
0	IDX_DATE	Date
1	IDX_DESC	Description
2	IDX_AMOUNT	Amount
3	IDX_CATEGORY	Category
4	IDX_MONTH	Month
"""

DEFAULT_CATEGORY = "Other" # If no keyword matches an expense description, the category defaults to "Other".

CATEGORY_RULES = [
    ("Housing", ["rent", "mortgage", "utility", "utilities"]),
    ("Transport", ["uber", "taxi", "bus", "train", "metro", "tram"]),
    ("Food", ["coffee", "cafe", "restaurant", "grocery", "supermarket", "food"]),
    ("Entertainment", ["cinema", "movie", "concert", "subscription", "netflix", "spotify", "game"]),
]

expenses = [] # Stores all expense records.
budgets_by_month = {}

def safe_float(text: str):
    s = text.strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None
"""
Converts user input safely into a float.
Supports European number formats ("12,50" → 12.5).

Why return None?
Prevents program crashes.
Allows caller to validate input explicitly:
    if amount is None:
        print("Invalid amount")
"""

def extract_month(date_str: str): # Extracts "YYYY-MM" from "YYYY-MM-DD". Used for monthly grouping and analysis.
    s = date_str.strip() # remove whitespace
    if len(s) < 7: # minimum length check
        return None
    if len(s) >= 5 and s[4] != "-": # format check
        return None
    year = s[0:4]
    month = s[5:7]
    # extract year and month
    if (not year.isdigit()) or (not month.isdigit()):
        return None # validate digit
    return s[0:7] # return "YYYY-MM"


def categorize_expense(description: str):
    text = (description or "").lower()
    for category, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw in text:
                return category
    return DEFAULT_CATEGORY

"""
Takes an expense description (e.g., "Coffee at Cafe").
Converts it to lowercase safely:
(description or "") ensures that if description is None, it becomes an empty string instead of crashing.
Loops through all (category, keywords) rules in CATEGORY_RULES.
If any keyword is a substring of the description, returns that category.
If no keyword matches, returns DEFAULT_CATEGORY (e.g., "Other").
"""

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

"""
Prints a nicely formatted table of categories and their keywords.
Uses:
    - if not CATEGORY_RULES to handle empty list
    - enumerate(..., start=1) to show human-friendly numbering
    - ", ".join(keywords) to print keywords on one line
"""

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

"""
Asks the user to type a category name.
Rejects empty input.
Prevents duplicate categories (case-insensitive).
Asks for comma-separated keywords.
Splits keywords, trims spaces, converts to lowercase, removes empty pieces.
Appends (category, keywords) to CATEGORY_RULES.
"""

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

"""
Shows categories with numbers.
User chooses a number.
Validates:
must be digits
must be within range
Confirms with "y".
Deletes the rule from CATEGORY_RULES.
"""

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

    while True:
        print(
            "\nKeyword options:\n"
            "1  - Add keywords\n"
            "2  - Delete keywords\n"
            "0  - Keep keywords\n"
        )
        keyword_choice = input("Enter your choice: ").strip()
        if keyword_choice in {"0", "1", "2"}:
            break
        print("Invalid selection. Please choose a valid menu number.")

    if keyword_choice == "1":
        keywords_input = input("Add keywords (comma separated): ").strip()
        new_keywords = [kw.strip().lower() for kw in keywords_input.split(",") if kw.strip()]
        if not new_keywords:
            print("At least one keyword is required. Edit cancelled.")
            return
        existing_set = {kw.lower() for kw in old_keywords}
        combined = old_keywords[:]
        for kw in new_keywords:
            if kw not in existing_set:
                combined.append(kw)
                existing_set.add(kw)
        new_keywords = combined
    elif keyword_choice == "2":
        keywords_input = input("Delete keywords (comma separated): ").strip()
        remove_keywords = [kw.strip().lower() for kw in keywords_input.split(",") if kw.strip()]
        if not remove_keywords:
            print("At least one keyword is required. Edit cancelled.")
            return
        remove_set = {kw.lower() for kw in remove_keywords}
        new_keywords = [kw for kw in old_keywords if kw.lower() not in remove_set]
        if not new_keywords:
            print("At least one keyword must remain. Edit cancelled.")
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

"""
-User selects a category rule.
-They can rename the category and/or change its keyword list.
-If the category name changes, it also updates:
    -existing expense records (expenses)
    -existing budgets (budgets_by_month)

Step-by-step logic
A) Choose category to edit
    -Same pattern: list, numeric selection, bounds check.

B) Read old values
    old_category, old_keywords = CATEGORY_RULES[idx]

C) Rename logic
-User can press Enter to keep the name.
-If they type a new name, duplicates are blocked (case-insensitive).

D) Keyword update logic
-User can press Enter to keep keywords.
-Otherwise it parses comma-separated keywords.
-Rejects empty keyword list.

E) Update the rule
    CATEGORY_RULES[idx] = (new_category, new_keywords)

F) If category name changed, update expenses + budgets
 
    if new_category != old_category:
        for rec in expenses:
            if rec[IDX_CATEGORY] == old_category:
                rec[IDX_CATEGORY] = new_category

-Any expense record that had the old category is renamed to the new category.

Then budgets:

for month, budgets in budgets_by_month.items():
    if old_category in budgets:
        old_value = budgets.pop(old_category)
        if new_category in budgets:
            print("Warning ... Keeping existing value.")
        else:
            budgets[new_category] = old_value


-It moves the old budget value under the new category name (per month).
-If the new category already had a budget, it keeps the existing budget and warns.
"""

def load_expenses_csv(filename: str):
    loaded = 0
    skipped = 0
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return

    """
    Initializes counters:
        -loaded: how many valid expense rows were imported
        -skipped: how many rows were invalid and ignored
    Tries to open the file and read all lines into a list.
    If the file does not exist, catches FileNotFoundError and exits cleanly without crashing.
    """

    if not lines:
        print("File is empty.")
        return

    """
    If the file contains zero lines, it prints a message and exits.
    Prevents later code from trying to read lines[0] (which would crash).
    """

    start_idx = 0
    header = lines[0].strip().lower().replace(" ", "")
    if header.startswith("date,") and "description" in header and "amount" in header:
        start_idx = 1

    """
    -Takes the first line, normalizes it:
        -removes leading/trailing whitespace (strip())
        -makes it case-insensitive (lower())
        -removes spaces (replace(" ", ""))
    -Checks if it looks like a header row (contains date/description/amount).
    -If yes, sets start_idx = 1 so the loop skips the header.
    """

    for line in lines[start_idx:]:
        raw = line.strip()
        if not raw:
            continue

        """
        -Iterates over all rows after the header (if any).
        -Strips whitespace.
        -Skips empty lines silently.
        """
        
        parts = [p.strip() for p in raw.split(",")]
        if len(parts) < 3:
            skipped += 1
            continue

        """
        -Splits the row by commas into fields.
        -If there aren’t at least 3 fields → invalid row → count as skipped.
        """

        date_str = parts[0]
        desc = parts[1]
        amount_val = safe_float(parts[2])

        month_val = extract_month(date_str)
        if amount_val is None or month_val is None:
            skipped += 1
            continue

        """
        -Takes:
            -date string
            -description string
            -amount string → converts safely using safe_float()
        -Extracts month (YYYY-MM) from the date using extract_month().
        -If either amount or month is invalid → skip the row.
        """

        category = categorize_expense(desc)
        record = [date_str, desc, amount_val, category, month_val]
        expenses.append(record)
        loaded += 1

        """
        -Assigns a category based on keywords in the description.
        -Builds a record list in the program’s internal format:
            -[date, desc, amount, category, month]
        -Appends it to the global expenses list.
        """

    print(f"Loaded {loaded} expense(s). Skipped {skipped} invalid row(s).") # Prints summary counts so the user understands what happened.


def save_expenses_csv(filename: str):
    if not expenses:
        print("No expenses to save.")
        return
# If there’s nothing in memory, it exits early.
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

"""
-Opens a file in write mode "w" (overwrites if it exists).
-Writes a header row.
-Loops through expenses and writes each record as CSV.

Why it replaces \n and \r?
-If a description contains newline characters, it would break the CSV row structure.
-This sanitizes the text into a single line.
"""

def delete_all_expenses():
    if not expenses:
        print("No expenses to delete.")
        return
# If the list is already empty, it exists.
    
    confirm = input("Delete all expenses? (y/N): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return

    """
    -Asks for confirmation.
    -Only "y" proceeds.
    -Anything else cancels safely.
    """
    expenses.clear()
    print("All expenses deleted.")

    """
    -Clears the list in-place.
    -Keeps the list object but removes all elements.
    """

def load_budgets_csv(filename: str):
    loaded = 0
    skipped = 0
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return

    """
    -Uses try/except to avoid crashing if the file doesn’t exist.
    -Reads all lines into memory.
    -Tracks:
        -loaded: valid rows inserted
        -skipped: invalid rows ignored
    """

    if not lines:
        print("File is empty.")
        return
# Prevents accessing lines[0] (would crash).

    start_idx = 0
    header = lines[0].strip().lower().replace(" ", "")
    if header.startswith("month,") and "category" in header and "budget" in header:
        start_idx = 1

    """
    Detects a header line like month,category,budget.
    If header is present, skips it.
    """

    for line in lines[start_idx:]:
        raw = line.strip()
        if not raw:
            continue

        parts = [p.strip() for p in raw.split(",")]
        if len(parts) < 3:
            skipped += 1
            continue
# Splits by comma, expects at least 3 columns: month, category, budget.

        month_raw = parts[0]
        cat = parts[1]
        value = safe_float(parts[2])

        month_str = extract_month(month_raw)
        if month_str is None or not cat or value is None:
            skipped += 1
            continue

        """
        -Converts amount with safe_float() (handles comma decimals).
        -Extracts YYYY-MM via extract_month().
        -Rejects invalid month/category/value.
        """

        if month_str not in budgets_by_month:
            budgets_by_month[month_str] = {}
        budgets_by_month[month_str][cat] = round(value, 2)
        loaded += 1

    print(f"Loaded {loaded} budget row(s). Skipped {skipped} invalid row(s).")


def save_budgets_csv(filename: str):
    if not budgets_by_month:
        print("No budgets to save.")
        return
# Avoid creting an empty file
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("month,category,budget\n")
            for month in sorted(budgets_by_month.keys()):
                for cat, value in budgets_by_month[month].items():
                    f.write(f"{month},{cat},{value}\n")
        """
        -Writes a header.
        -Sorts months to produce stable output order.
        -Within each month, categories are written in dictionary iteration order (not explicitly sorted).
        """
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
# Retrieves budget for a month and returns a sorted list of (category, budget) pairs.

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
# Prints each month in sorted order.

def add_budget_interactive():
    while True:
        month_input = input("Month (YYYY-MM) (enter to stop): ").strip()
        if not month_input:
            return
        if extract_month(month_input) is None:
            print("Invalid month format.")
            continue
        break
# Keeps asking until month format is valid.
# Allows user to cancel by pressing Enter
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
    year_input = input("Enter year (YYYY): ").strip()
    month_input = input("Enter month (MM): ").strip()

    if not (year_input.isdigit() and month_input.isdigit()):
        print("Invalid year or month format.")
        return

    month_number = int(month_input)
    if month_number < 1 or month_number > 12:
        print("Invalid month. Please enter a value between 01 and 12.")
        return

    month_str = extract_month(f"{year_input}-{month_number:02d}")
    if month_str is None:
        print("Invalid year or month format.")
        return

    records = [rec for rec in expenses if rec[IDX_MONTH] == month_str]
    if not records:
        print(f"No expenses found for month '{month_str}'.")
        return

    totals = calculate_totals(records)
    month_budgets = budgets_by_month.get(month_str, {})
    categories = all_categories_from_data_and_budgets(totals, month_budgets)

    print("\n=== Monthly Summary ===")
    print(f"Month: {month_str}")
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
    year_input = input("Enter year (YYYY): ").strip()
    month_input = input("Enter month (MM): ").strip()

    if not (year_input.isdigit() and month_input.isdigit()):
        print("Invalid year or month format.")
        return

    month_number = int(month_input)
    if month_number < 1 or month_number > 12:
        print("Invalid month. Please enter a value between 01 and 12.")
        return

    month_str = extract_month(f"{year_input}-{month_number:02d}")
    if month_str is None:
        print("Invalid year or month format.")
        return

    records = [rec for rec in expenses if rec[IDX_MONTH] == month_str]
    if not records:
        print(f"No expenses found for month '{month_str}'.")
        return

    totals = calculate_totals(records)
    cats = sorted(totals.keys(), key=str.lower)
    if not cats:
        print("No categories found for the selected month.")
        return
    values = [totals[c] for c in cats]
    print(f"Plotting {len(cats)} category(ies) for {month_str}.")

    month_budgets = budgets_by_month.get(month_str, {})

    plt.figure(figsize=(8, 4))
    bars = plt.bar(cats, values)
    for i, cat in enumerate(cats):
        budget = month_budgets.get(cat)
        if budget is not None:
            plt.hlines(
                y=budget,
                xmin=i - 0.4,
                xmax=i + 0.4,
                colors="red",
                linewidth=2,
            )
    plt.xlabel("Category")
    plt.ylabel("Total Spent")
    plt.title(f"Spending by Category ({month_str})")
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
        "4  - Show monthly summary\n"
        "5  - Plot spending by category (optional)\n"
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
    try:
        main()
    except KeyboardInterrupt:
        print("\nGood bye")
