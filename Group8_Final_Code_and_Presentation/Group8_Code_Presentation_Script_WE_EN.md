# Group 8 – Expense & Budget Tracker (Code Walkthrough Presentation Script)

**Style note:** We speak in *first-person plural* (“we”), because we built this as a 3-person team.

---

## 0) 15-minute structure (what we will cover)

- **0:00–1:00** What the project does and why we built it
- **1:00–5:00** Program structure (menu + functions) and our core data structures
- **5:00–9:00** File handling (CSV) + validation + error handling
- **9:00–12:30** Categorization + monthly summary (the core logic)
- **12:30–14:00** Optional plotting + limitations/next steps
- **14:00–15:00** Q&A

---

## 1) What the program does (short intro)

We built a **console-based Expense & Budget Monitor**. Our main goal is to help users understand:

- how expenses are distributed across categories,
- how much is spent per category **for a selected month**,
- and whether the monthly category budgets are exceeded.

We designed the solution to stay within the course topics: **lists, dictionaries, loops, functions, file I/O, and optional Matplotlib**.

---

## 2) Our overall architecture (IPO + main menu)

We structured the project around the **IPO (Input–Process–Output)** concept:

- **Input:** CSV files (expenses and budgets) + user menu choices
- **Process:** categorization, monthly filtering, aggregation, budget comparison
- **Output:** console tables + warnings + optional bar chart

The program starts in `main()` and runs a `while True` loop that shows a menu and calls the appropriate function. We chose this design because it keeps the program easy to use and easy to test: each menu option maps to one clear task.

---

## 3) Data structures (what we store and why)

### 3.1 Expenses: list of records
We store all expenses in a list called `expenses`.
Each expense is one record in the form:

`[date, description, amount, category, month]`

We chose a list of lists because:
- it is simple,
- it matches the course content,
- and it is easy to loop over.

### 3.2 Index constants (readability and correctness)
We defined constants like `IDX_DATE`, `IDX_AMOUNT`, `IDX_CATEGORY`, etc.
We use them to access list positions safely and consistently.
This avoids “magic numbers” like `rec[3]` and makes the code easier to explain during grading.

### 3.3 Budgets: nested dictionary by month
Budgets are stored in `budgets_by_month`, a nested dictionary:

`budgets_by_month[month][category] = budget_value`

We use a nested dictionary because:
- a budget naturally depends on a **month** and a **category**,
- dictionary lookup is fast and clean,
- and it matches the lecturer’s note about **monthly budgets**.

### 3.4 Selected month
We store the current analysis month in `selected_month` (format `YYYY-MM`).
We analyze **one month at a time**, to keep the logic clear and deterministic.

---

## 4) Input validation and robustness (how we prevent crashes)

### 4.1 Safe number conversion: `safe_float()`
When we read amounts from files or the user, we convert strings to floats using `safe_float()`.
We do this with `try/except` so invalid inputs do not crash the program.
We also replace commas with dots to support common European formatting.

### 4.2 Month extraction without date libraries: `extract_month()`
We extract `YYYY-MM` from the date string using string slicing and `.isdigit()` checks.
We intentionally avoid complex date parsing because:
- we do not need date arithmetic,
- we want to stay within course basics,
- and we want predictable behavior.

### 4.3 File errors
When reading a CSV, we handle `FileNotFoundError` and print a user-friendly message.
This is important because file paths are the most common runtime issue in console projects.

---

## 5) Reading and writing CSV files (why and how)

### 5.1 Loading expenses: `load_expenses_csv(filename)`
We read the file with:

- `with open(..., encoding='utf-8')` to ensure correct closing and robust text handling,
- `readlines()` and then loop through lines,
- `.strip()` to remove whitespace,
- `.split(',')` to separate fields.

We also handle the header row by checking if line 1 starts with `date,` and includes expected column names.

For each row we:
1. validate the number of fields,
2. convert `amount` with `safe_float()`,
3. derive `month` with `extract_month()`,
4. compute category with `categorize_expense()`.

Invalid rows are skipped, and we print how many were loaded vs skipped. We do this because real CSV files often contain inconsistent lines.

### 5.2 Saving expenses: `save_expenses_csv(filename)`
We export all expenses to a CSV with a header.
We also remove newline characters from descriptions to keep the output file well-formed.

### 5.3 Loading budgets: `load_budgets_csv(filename)`
We read budgets from:

`month,category,budget`

We validate:
- month format (`YYYY-MM`),
- category non-empty,
- numeric budget.

Then we store budgets into `budgets_by_month`.

### 5.4 Budgets remain fixed during analysis
One important design choice is: **we do not change budgets during the analysis itself**.
We only load/save budgets via CSV, and then treat them as fixed reference values.
This aligns with the project proposal idea that budgets are known before analysis and remain stable at runtime.

---

## 6) Categorization (the lecturer’s key question: multiple keywords)

### 6.1 Keyword rules and priority order
We categorize expenses using `CATEGORY_RULES`, which is a list of:

`(category_name, [keywords...])`

We check categories in that list order.

### 6.2 Deterministic behavior for multiple matches
If the description contains multiple keywords from different categories, we use a **priority order**:

- the first matching category in `CATEGORY_RULES` wins.

We chose this because:
- it is deterministic,
- it is simple to explain and test,
- and it directly answers the lecturer’s comment about multiple keywords.

---

## 7) Monthly analysis (aggregation + budget comparison)

### 7.1 Filtering by month
`get_expenses_for_selected_month()` returns only expenses where `rec[IDX_MONTH] == selected_month`.
We do this to keep the analysis consistent and aligned with monthly budgets.

### 7.2 Aggregation with dictionaries: `calculate_totals(records)`
We compute category totals using a dictionary:

`totals[cat] = totals.get(cat, 0.0) + amt`

We chose `.get()` because it avoids separate “if key exists” checks and keeps the loop clean.

### 7.3 Summary table and warnings: `show_monthly_summary()`
We print:
- Category
- Budget
- Spent
- Remaining
- Status

Status rules:
- **NO BUDGET** if no budget exists for that category in the selected month
- **OK** if budget - spent >= 0
- **BUDGET EXCEEDED** if budget - spent < 0

If any category is exceeded, we print a warning line with the list of exceeded categories.

---

## 8) Editing and adding expenses (optional extension)

### 8.1 Adding: `add_expense_interactive()`
We allow manual entry of an expense (date, description, amount). We then:
- compute the month,
- categorize the description,
- append the record to `expenses`.

### 8.2 Editing: `edit_expense_interactive()`
We edit only within the selected month, so we:
- list expenses for the month,
- validate the selected index with `.isdigit()` and range checks,
- allow changing date/description/amount,
- and re-categorize if the description changes.

We implemented add/edit to reflect the lecturer suggestion that the system should not rely only on a fixed CSV.

---

## 9) Optional plotting with Matplotlib

At the top of the file we try to import Matplotlib.
If it fails, we set `HAS_MPL = False`.

This allows our program to run everywhere, and the plot feature becomes optional.

`plot_spending_by_category()` creates a simple bar chart for the selected month.

---

## 10) Quick demo plan (60–90 seconds)

1. Load expenses CSV (menu option 1)
2. Load budgets CSV (menu option 3)
3. Select month (menu option 5)
4. Show summary table (menu option 10)
5. Optional: show bar chart (menu option 11)

---

## 11) Q&A cheat sheet (short answers)

**Q: Why did we use lists for expenses instead of a class or DataFrame?**  
A: We used a list-of-lists because it matches course topics, stays simple, and is easy to loop through.

**Q: Why do we use index constants like `IDX_AMOUNT`?**  
A: They make list access readable and prevent mistakes with hard-coded indices.

**Q: How do we avoid crashes from bad data?**  
A: We validate row length, use `safe_float()` with `try/except`, and skip invalid rows.

**Q: What if a description matches multiple categories?**  
A: We use a deterministic priority order: the first matching category in `CATEGORY_RULES` is used.

**Q: Why do we analyze by month?**  
A: Budgets are naturally time-based; monthly filtering keeps budget comparison meaningful.

**Q: Why is plotting optional?**  
A: The code must still run without Matplotlib, so we detect availability using `try/except ImportError`.
