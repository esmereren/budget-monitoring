# Group 8 – Expense & Budget Tracker (Spoken Presentation Script – WE / English)

**Total slot:** 15 minutes (≈ 12 minutes speaking + 3 minutes Q&A)

---

## Speaker 1 (≈ 4 minutes) — Problem, Scope, and Program Structure

Hello everyone. We are **Group 8**, and our project is **Expense & Budget Tracking – “Where Does Our Money Go?”**.

### What we built
We built a **console-based Expense & Budget Monitor** that helps a user answer three practical questions:
1) *How much did we spend in each category?*
2) *Do we exceed our category budgets?*
3) *Where does most of our money go?*

We designed the solution to stay strictly within the course topics: **lists and dictionaries, loops, conditions, functions, file operations, and optional Matplotlib**.

### Why monthly budgets
Budgets are time-based, so we treat them as **monthly budgets per category**. In our program we select a month like **YYYY-MM**, and then we analyze spending only for that month. This keeps the budget comparison meaningful and matches the lecturer’s comment about monthly budgets.

### IPO architecture
We structured the project using the **Input–Process–Output** principle:
- **Input:** expenses and budgets from CSV files, plus user choices from a menu
- **Process:** categorization, monthly filtering, aggregation, and budget comparison
- **Output:** a console summary table, budget warnings, and an optional bar chart

### Menu-driven design
Our program starts in `main()` and runs a `while True` menu loop. We did this because it makes the workflow very clear:
- each menu option maps to one function,
- we can test features independently,
- and the program stays interactive and user-friendly.

In the next part, we’ll explain how we read CSV files safely and how we make the program robust against invalid input.

---

## Speaker 2 (≈ 4 minutes) — Data Structures, CSV Handling, and Robustness

Now we’ll explain **what we store** and **how we read and validate the data**.

### Our core data structures
We store expenses in a list called `expenses`. Each expense is one record stored as a list:

`[date, description, amount, category, month]`

We chose a list-of-lists because it is simple and directly aligned with the course.

To keep indexing readable, we also use index constants like `IDX_DATE`, `IDX_AMOUNT`, and `IDX_CATEGORY`. This avoids mistakes and makes the code easier to explain.

Budgets are stored in a nested dictionary `budgets_by_month`:

`budgets_by_month[month][category] = budget_value`

We chose a nested dictionary because budgets naturally depend on **month** and **category**, and dictionary lookup is clean and fast.

### Reading CSV (expenses)
In `load_expenses_csv(filename)` we use:
- `with open(..., encoding='utf-8')` for safe file handling,
- `readlines()` and a loop,
- `.strip()` to clean the line,
- `.split(',')` to extract fields,
- and we skip a header row if present.

We validate each row before adding it:
- We check that we have at least 3 columns.
- We convert the amount using `safe_float()`.
- We derive the month using `extract_month()`.
- Then we categorize the expense and append the record.

If anything is invalid, we skip that row and count it as skipped. This prevents crashes and reflects real-world messy CSV files.

### Input validation and error handling
We created two helper functions:
- `safe_float()` uses `try/except ValueError` so invalid numbers don’t crash the program.
- `extract_month()` validates the `YYYY-MM` format without needing any date libraries.

We also handle `FileNotFoundError` when the file path is wrong.

### Budgets remain stable during analysis
We only **load** and **save** budgets via CSV. During analysis, budgets are treated as fixed reference values. This keeps the program consistent and matches the idea that budget values are known before comparison.

Next, we’ll explain our categorization logic, how we handle the “multiple keywords” case, and how we compute the monthly summary.

---

## Speaker 3 (≈ 4 minutes) — Categorization, Monthly Summary, and Optional Plot

Now we’ll focus on the core logic: **categorization**, **aggregation**, and **budget comparison**.

### Categorization with deterministic priority
We categorize expenses using a list of rules called `CATEGORY_RULES`. Each rule contains a category and keywords.

To assign a category, we lower-case the description and check if any keyword appears.

A key lecturer question was: *“What if the description contains multiple keywords?”*

We solve this by using a **deterministic priority order**: we check categories in a fixed order, and **the first match wins**. This is simple, consistent, and easy to test.

If nothing matches, we assign the default category **“Other”**.

### Monthly filtering
We analyze one selected month at a time. After we select `selected_month`, we filter expenses so only records for that month are included.

### Aggregation with a dictionary
We compute totals per category in `calculate_totals(records)` using:

`totals[cat] = totals.get(cat, 0.0) + amount`

We use `.get()` because it avoids extra `if` checks and keeps the loop clean.

### Summary table and warnings
In `show_monthly_summary()` we print a table with:
- category
- budget
- spent
- remaining
- status

Status logic:
- **NO BUDGET** if no budget exists for that category in that month
- **OK** if remaining >= 0
- **BUDGET EXCEEDED** if remaining < 0

If any categories exceed their budgets, we print a warning listing them.

### Optional Matplotlib chart
Plotting is optional. At startup we try to import Matplotlib, and if it’s not available we skip plotting.
If it is available, we show a bar chart of spending by category for the selected month.

That’s our full workflow: load data → categorize → select month → summarize → optionally plot.

---

## 60–90 second demo plan (if we show the program live)
1. Load expenses CSV
2. Load budgets CSV
3. Select month (YYYY-MM)
4. Show monthly summary
5. Optional: plot spending by category

---

## Q&A cheat sheet (short answers)

**Q: Why did we store expenses as a list of lists?**  
A: We stayed within the course topics; lists are simple, readable, and easy to iterate.

**Q: Why did we use index constants like `IDX_AMOUNT`?**  
A: They prevent mistakes and make record access easy to explain.

**Q: How do we handle invalid CSV data?**  
A: We validate row length, use `safe_float()` and `extract_month()`, and skip invalid rows so the program doesn’t crash.

**Q: What if a description matches multiple categories?**  
A: We use a deterministic priority order: the first matching category in `CATEGORY_RULES` is used.

**Q: Why do we analyze by month?**  
A: Budgets are time-based; monthly analysis keeps comparisons meaningful.

**Q: Why is plotting optional?**  
A: The program must still run without Matplotlib, so we detect availability with `try/except ImportError`.
