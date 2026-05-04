# Classic Models SQL Assignment Guide

This workspace contains the Classic Models sample database dump and a complete SQL practice script for the assignment.

## Files In This Folder

- `mysqlsampledatabase (1).sql` - the database dump to import
- `classic_models_practice_solutions.sql` - the SQL solutions for tasks 1 to 20
- `learning-journal.md` - notes about errors, fixes, and learning points

## What You Need

- MySQL Server installed locally
- A MySQL client such as the MySQL command-line client or MySQL Workbench
- MySQL 8.0 or newer recommended because the script uses `WITH` clauses and window functions like `RANK()` and `DENSE_RANK()`

## Step-By-Step Setup

### 1. Open a terminal and log in to MySQL

Use your root account or another account with permission to create databases and load data.

```sql
mysql -u root -p
```

Enter your password when prompted.

### 2. Create the Classic Models database if needed

If the dump file does not create the database automatically, create it first.

```sql
CREATE DATABASE classicmodels;
USE classicmodels;
```

### 3. Import the dump file

Run the `source` command from inside the MySQL prompt.

```sql
source C:/Users/rubin/OneDrive/Desktop/AI fellow/week1/sql-fundamentals/mysqlsampledatabase (1).sql;
```

If the path contains spaces, keep the full path exactly as shown. You can also copy the file to a simpler folder if your MySQL client has trouble with the path.

### 4. Confirm the tables loaded correctly

Check that the schema exists and the core tables are available.

```sql
SHOW TABLES;
DESC customers;
DESC employees;
DESC orders;
DESC payments;
DESC orderdetails;
DESC offices;
```

Expected tables in this assignment include:

- customers
- employees
- offices
- orders
- orderdetails
- payments
- products
- productlines

### 5. Run the practice script

Open `classic_models_practice_solutions.sql` in MySQL Workbench or run it from the MySQL prompt.

```sql
source C:/Users/rubin/OneDrive/Desktop/AI fellow/week1/sql-fundamentals/classic_models_practice_solutions.sql;
```

You can also copy and run the queries one by one if you want to show the results gradually during a demo.

## How The Assignment Was Solved

The solution script follows the same pattern as the assignment tasks:

### Filtering and cleaning

- Task 1 filters customers by `creditLimit > 20000`
- Task 3 filters customers with a non-null state, USA country, and a credit limit range
- Task 18 shows a simple update example
- Task 19 demonstrates deleting low-value payments
- Task 20 demonstrates inserting a new payment manually

### Self joins and employee hierarchy

- Tasks 2, 4, 7, and 8 use the `employees` table to explore reporting structure
- `reportsTo` is a self-referencing column, so employees can be linked to their supervisors using the same table
- Task 7 solves the supervisor count without a join, while Task 8 solves it with a join

### Aggregation and reporting

- Tasks 5, 6, 11, 12, 13, 14, 15, and 16 use `GROUP BY`, `COUNT`, `SUM`, and window functions to produce business-style reports
- Task 5 calculates average customer credit limit by country
- Task 11 counts employees per office
- Task 13 sums payment received per office
- Task 14 sums sales amount per office
- Task 15 computes pending payment per office
- Task 16 calculates each customer’s credit limit proportion within their country

### Common table expressions and window functions

- Task 9 uses a `WITH` clause to compare customers with the average credit limit
- Task 10 uses ranking functions to rank customers by credit limit
- Task 16 uses a window function to calculate proportions by country

### Views

- Task 17 creates a reusable view named `customer_order_summary`

## Important Notes Before Running All Queries

- Tasks 18, 19, and 20 change the data
- If you want to keep the database unchanged for demonstration, run tasks 1 to 17 first and leave the data-changing queries for last
- If you need to repeat the demo, restore the database dump again before rerunning the script

## How To Demonstrate The Work

Use this flow in class, in a screen recording, or during a live demo.

### Demo Step 1. Show the schema

Run:

```sql
SHOW TABLES;
DESC customers;
DESC employees;
DESC orders;
```

Explain that the database has customers, employees, offices, orders, order details, payments, products, and product lines.

### Demo Step 2. Show one filter example

Run Task 1 or Task 3.

Explain how `WHERE` and `BETWEEN` clean and filter the data.

### Demo Step 3. Show employee hierarchy queries

Run Task 2, Task 4, Task 7, and Task 8.

Explain that the employee table is self-referencing through `reportsTo`.

### Demo Step 4. Show aggregation queries

Run Task 5, Task 11, Task 13, Task 14, and Task 16.

Explain that these queries summarize business performance by country and by office.

### Demo Step 5. Show advanced SQL features

Run Task 9, Task 10, and Task 17.

Explain that `WITH` clauses, ranking, and views make the analysis reusable and easier to read.

### Demo Step 6. Show data modification

Run Task 18, Task 19, and Task 20 last.

Explain that these are real database actions, so they should be shown after the reporting queries.

## Suggested Presentation Order

1. Import the dump file
2. Verify tables with `SHOW TABLES`
3. Run filtering queries
4. Run join queries
5. Run aggregation queries
6. Run CTE and window function queries
7. Run the view query
8. Run update, delete, and insert queries at the end

## Expected Outcome

After running the assignment, you should be able to demonstrate:

- Filtering with `WHERE`, `BETWEEN`, and `IS NOT NULL`
- Joining related tables
- Self joins for employee reporting structure
- Aggregation with `COUNT`, `SUM`, and `AVG`
- CTEs using `WITH`
- Ranking customers by credit limit
- Creating a reusable SQL view
- Updating, deleting, and inserting records

## If Something Fails

- If `source` fails, check the file path and make sure MySQL can read that location
- If `WITH` or window functions fail, upgrade to MySQL 8.0 or newer
- If a query returns duplicate office totals, check the join path and the `GROUP BY` columns
- If you want a clean rerun, import the database dump again before running the script

## Learning Journal

See `learning-journal.md` for the short record of what was learned and any notes about SQL behavior in this assignment.