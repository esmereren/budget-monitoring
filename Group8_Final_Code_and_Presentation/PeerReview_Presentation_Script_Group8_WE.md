# Group 8 – Peer Review Presentation Script (15 minutes)

**Project:** Expense & Budget Tracking – *Where Does Our Money Go?*  
**Team:** Abusaied Khalid, Eren Cemil Esmer, Ruder Leonard  
**Session format:** 12 minutes talk (≈ 4 minutes each) + 3 minutes Q&A

---

## 0) Timing Plan (suggested)

- **00:00 – 00:20** Greeting + what we built  
- **00:20 – 04:20** Speaker 1: project overview + structure  
- **04:20 – 08:20** Speaker 2: data source, CSV reading, monthly budgets, robustness  
- **08:20 – 12:20** Speaker 3: categorization rules, edge cases, totals, output, optional plot  
- **12:20 – 15:00** Q&A / feedback

---

## 1) Speaker 1 (≈ 4 minutes) – Overview + Program Structure

Hello everyone, we are **Group 8**: Khalid, Esmer, and Ruder. We built a console-based project called **“Expense & Budget Tracking – Where Does Our Money Go?”**.

### Why we chose this topic
We often have expense data in CSV exports, but it’s not easy to understand:
- how much we spend per category,
- whether we exceed our budgets,
- and which categories dominate our spending.

So we built a tool that converts raw CSV lines into a clear monthly budget report.

### What our tool does (high-level)
In our menu-based application we can:
1. **load expenses from a CSV file**,
2. **categorize each expense** using keywords in the description,
3. **select a month (YYYY-MM)** for analysis,
4. **compare totals per category with monthly budgets** and show warnings,
5. print a **readable console summary table**,
6. and optionally **plot** category totals if Matplotlib is available.

### How we structured the program (main + menu)
We use a `main()` function with a `while True` loop. In each loop iteration we:
- show the menu,
- read the user’s choice with `input().strip()`,
- call the matching function.

This structure is simple, testable, and aligns with the course approach for modular programs.

We explicitly incorporated the feedback in our final design:
- **Monthly budgets:** we analyze budgets **per month and category**.
- **Add/Edit consumption data:** we added menu functions to **add** a new expense and **edit** an existing one.
- **Multiple keywords in one description:** we define a deterministic rule (priority order) so categorization is always consistent.
- We also made sure our proposal includes **work packages in bullet points** and **task responsibilities** per person.

Next, we will explain our data inputs and how we read them safely.

---

## 2) Speaker 2 (≈ 4 minutes) – Data Source, CSV Reading, Monthly Budgets, Robustness

We will focus on the data part: our CSV inputs, how we load them, and how we keep the program stable.

### Expense CSV format (Input)
Our primary data source is an expense CSV file where each row is one expense:
- **date** (YYYY-MM-DD),
- **description**,
- **amount**.

Example:
`2025-11-01,Coffee at Cafe,4.50`

### How we read the expense file (only basic file operations)
We read the file using:
- `open()` with `encoding="utf-8"`,
- `readlines()` to load lines,
- `.strip()` to remove trailing characters,
- `.split(",")` to separate fields,
- `float()` conversion (via a safe conversion function).

### How we prevent crashes (invalid rows)
Real CSV files can contain invalid data. To keep the program consistent:
- we check the number of fields,
- we try to convert the amount to a float,
- we validate the date format by extracting the month as `YYYY-MM` using simple string slicing and `isdigit()` checks,
- if a row is invalid, we **skip it** and continue.

This way, the program doesn’t crash because of a single bad line.

### Monthly budgets (separate from expenses)
Our lecturer suggested defining budgets monthly per category. We do this using a separate input:
- a **budget CSV** file with columns: `month,category,budget`
  - example: `2025-11,Food,300`

We load budgets into a nested dictionary:
- `budgets_by_month[month][category] = budget_value`

### “Budgets remain fixed during runtime”
In our design, budgets are **loaded** (or could be hardcoded) and then used as fixed reference values for the analysis. We do not modify budgets inside the menu during the analysis flow, which keeps the comparison logic simple and predictable.

Next, we will explain categorization, edge cases, aggregation with dictionaries, and the output/reporting logic.

---

## 3) Speaker 3 (≈ 4 minutes) – Categorization, Edge Cases, Totals, Output, Optional Plot

We will explain the core processing logic: categorization, totals, budget comparison, and visualization.

### Why we use lists and dictionaries
We store each expense record in a **list** with fixed positions:
`[date, description, amount, category, month]`

We use **dictionaries** for:
- totals per category (`category_totals`),
- budgets per month (`budgets_by_month`).

Dictionaries are ideal because we can map **category → numeric value** and update totals efficiently.

### Categorization with keyword rules
We categorize each expense using only string operations:
- we convert the description with `.lower()`,
- we check whether keywords appear in the text.

Example:
- “coffee”, “cafe”, “restaurant” → Food  
- “uber”, “taxi”, “bus”, “train” → Transport  
- “rent”, “mortgage” → Housing  
- otherwise → Other

### Handling the lecturer’s edge case: multiple keywords
If a description contains multiple keywords, we need deterministic behavior. We solve this by using a **priority order** in our rules. We check categories in a fixed order (for example Housing → Transport → Food → Entertainment → Other).  
So the first matching category wins, and the output is always consistent and testable.

### Aggregation and budget comparison
For a selected month:
1. we filter expenses to that month,
2. we compute totals with a dictionary using:
   - `totals[cat] = totals.get(cat, 0.0) + amount`,
3. we compare totals to budgets and compute remaining amounts,
4. we print a summary table:
   - Category | Budget | Spent | Remaining | Status
5. if remaining is negative, we print **BUDGET EXCEEDED** as a clear warning.

### Add/Edit consumption data (requested by lecturer)
We also provide interactive menu options:
- **Add expense:** we input date, description, amount; then we categorize and store it.
- **Edit expense:** we select a record from the selected month and update date/description/amount; we then recalculate month and category if needed.

### Optional visualization (Matplotlib)
We treat plotting as an optional feature:
- we attempt to import matplotlib with `try/except`,
- if available, we plot a bar chart of category totals,
- if not available, the rest of the program still works.

---

## 4) Work Packages (proposal alignment, short version)

- **WP1:** Read and validate expense CSV  
- **WP2:** Categorize expenses with keyword rules + priority rule  
- **WP3:** Calculate totals + compare with monthly budgets + summary table  
- **WP4:** Build and integrate the menu system (main loop) + add/edit features  
- **WP5:** Optional matplotlib plot + documentation and testing

---

## 5) Roles & Responsibilities (proposal alignment)

- **We (Esmer):** menu system + integration + optional visualization  
- **We (Khalid):** CSV file handling + validation + error handling tests  
- **We (Ruder):** categorization rules + totals/budget comparison + output formatting

---

## 6) Q&A Cheat Sheet (short answers)

**Q: Why monthly budgets?**  
A: We want budgets to be time-based. We analyze one month at a time (`YYYY-MM`) and compare spending to that month’s limits.

**Q: What if the CSV contains invalid lines?**  
A: We validate field count, use safe float conversion with `try/except`, validate date/month, and skip invalid rows.

**Q: What if a description matches multiple categories?**  
A: We use a fixed priority order so categorization is deterministic.

**Q: Why lists for expenses and dictionaries for totals?**  
A: Lists keep records simple and ordered; dictionaries make aggregation (category → total) fast and readable.

**Q: What if matplotlib is missing?**  
A: Plotting is optional; the program still prints all reports without crashing.

---

**End.** We are happy to receive your questions and feedback.
