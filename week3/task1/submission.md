# SQL Benchmark Submission

Database: classicmodels (from week2 seed)

Instructions: Replace the Result section for each question with your screenshot (or a small result excerpt and count if applicable).

---

## 1) List all products

**Question**: List all products

**SQL**:
```sql
SELECT
  p."productCode",
  p."productName",
  p."productLine",
  p."quantityInStock",
  p."buyPrice",
  p."MSRP"
FROM products AS p
LIMIT 5;
```


---

## 2) Get all customers

**Question**: Get all customers

**SQL**:
```sql
SELECT 
  c."customerNumber",
  c."customerName",
  c."contactLastName",
  c."contactFirstName",
  c."phone",
  c."addressLine1",
  c."addressLine2",
  c."city",
  c."state",
  c."postalCode",
  c."country",
  c."salesRepEmployeeNumber",
  c."creditLimit"
FROM customers;
```


---

## 3) Show all orders

**Question**: Show all orders

**SQL**:
```sql
SELECT
  o."orderNumber",
  o."orderDate",
  o."requiredDate",
  o."shippedDate",
  o."status",
  o."comments",
  o."customerNumber"
FROM orders AS o;
```


---

## 4) List all employees

**Question**: List all employees

**SQL**:
```sql
SELECT
  e."employeeNumber",
  e."lastName",
  e."firstName",
  e."extension",
  e."email",
  e."officeCode",
  e."reportsTo",
  e."jobTitle"
FROM employees AS e;
```


---

## 5) Get all offices

**Question**: Get all offices

**SQL**:
```sql
SELECT
  o."officeCode",
  o."city",
  o."phone",
  o."addressLine1",
  o."addressLine2",
  o."state",
  o."country",
  o."postalCode",
  o."territory"
FROM offices AS o;
```

---

## 6) Show all product lines

**Question**: Show all product lines

**SQL**:
```sql
SELECT
  pl."productLine",
  pl."textDescription",
  pl."htmlDescription",
  pl."image"
FROM productlines AS pl;q
```


---

## 7) List all payments

**Question**: List all payments

**SQL**:
```sql
SELECT
  p."customerNumber",
  p."checkNumber",
  p."paymentDate",
  p."amount"
FROM payments AS p;
```


---

## 8) Get product names and prices

**Question**: Get product names and prices

**SQL**:
```sql
SELECT
  p."productName",
  p."buyPrice",
  p."MSRP"
FROM products AS p;
```


---

## 9) Get customer names and cities

**Question**: Get customer names and cities

**SQL**:
```sql
SELECT
  c."customerName",
  c."city"
FROM customers AS c;
```


---

## 10) List employee first and last names

**Question**: List employee first and last names

**SQL**:
```sql
SELECT
  e."firstName",
  e."lastName"
FROM employees AS e;
```


---

## 11) Get all order dates

**Question**: Get all order dates

**SQL**:
```sql
SELECT
  o."orderDate"
FROM orders AS o;
```


---

## 12) Show product vendor list

**Question**: Show product vendor list

**SQL**:
```sql
SELECT DISTINCT
  p."productVendor"
FROM products AS p
ORDER BY p."productVendor";
```


---

## 13) Get all product codes

**Question**: Get all product codes

**SQL**:
```sql
SELECT
  p."productCode"
FROM products AS p;
```


---

## 14) List all countries from offices

**Question**: List all countries from offices

**SQL**:
```sql
SELECT DISTINCT
  o."country"
FROM offices AS o
ORDER BY o."country";
```

---

## 15) Show all order statuses

**Question**: Show all order statuses

**SQL**:
```sql
SELECT DISTINCT
  o."status"
FROM orders AS o
ORDER BY o."status";
```


---

## 16) Get all payment amounts

**Question**: Get all payment amounts

**SQL**:
```sql
SELECT
  p."amount"
FROM payments AS p;
```


---

## 17) List all job titles

**Question**: List all job titles

**SQL**:
```sql
SELECT DISTINCT
  e."jobTitle"
FROM employees AS e
ORDER BY e."jobTitle";
```


---

## 18) Get customer phone numbers

**Question**: Get customer phone numbers

**SQL**:
```sql
SELECT
  c."customerName",
  c."phone"
FROM customers AS c;
```


---

## 19) Show product MSRP values

**Question**: Show product MSRP values

**SQL**:
```sql
SELECT
  p."productName",
  p."MSRP"
FROM products AS p;
```


---

## 20) List order numbers

**Question**: List order numbers

**SQL**:
```sql
SELECT
  o."orderNumber"
FROM orders AS o;
```


---

## 21) Get orders with customer names

**Question**: Get orders with customer names

**SQL**:
```sql
SELECT
  o."orderNumber",
  o."orderDate",
  o."status",
  c."customerName"
FROM orders AS o
JOIN customers AS c
  ON c."customerNumber" = o."customerNumber";
```


---

## 22) Get employees with office city

**Question**: Get employees with office city

**SQL**:
```sql
SELECT
  e."employeeNumber",
  e."firstName",
  e."lastName",
  o."city" AS "officeCity"
FROM employees AS e
JOIN offices AS o
  ON o."officeCode" = e."officeCode";
```


---

## 23) Get payments with customer names

**Question**: Get payments with customer names

**SQL**:
```sql
SELECT
  p."customerNumber",
  c."customerName",
  p."checkNumber",
  p."paymentDate",
  p."amount"
FROM payments AS p
JOIN customers AS c
  ON c."customerNumber" = p."customerNumber";
```


---

## 24) Get order details with product names

**Question**: Get order details with product names

**SQL**:
```sql
SELECT
  od."orderNumber",
  od."productCode",
  p."productName",
  od."quantityOrdered",
  od."priceEach",
  od."orderLineNumber"
FROM orderdetails AS od
JOIN products AS p
  ON p."productCode" = od."productCode";
```


---

## 25) Get products with product line description

**Question**: Get products with product line description

**SQL**:
```sql
SELECT
  p."productCode",
  p."productName",
  p."productLine",
  pl."textDescription"
FROM products AS p
JOIN productlines AS pl
  ON pl."productLine" = p."productLine";
```


---

## 26) Get customers with sales rep names

**Question**: Get customers with sales rep names

**SQL**:
```sql
SELECT
  c."customerNumber",
  c."customerName",
  c."salesRepEmployeeNumber",
  e."firstName" AS "salesRepFirstName",
  e."lastName" AS "salesRepLastName"
FROM customers AS c
LEFT JOIN employees AS e
  ON e."employeeNumber" = c."salesRepEmployeeNumber";
```


---

## 27) Get orders with customer city

**Question**: Get orders with customer city

**SQL**:
```sql
SELECT
  o."orderNumber",
  o."orderDate",
  o."status",
  c."customerName",
  c."city"
FROM orders AS o
JOIN customers AS c
  ON c."customerNumber" = o."customerNumber";
```


---

## 28) Get employees and their manager

**Question**: Get employees and their manager

**SQL**:
```sql
SELECT
  e."employeeNumber",
  e."firstName",
  e."lastName",
  m."employeeNumber" AS "managerNumber",
  m."firstName" AS "managerFirstName",
  m."lastName" AS "managerLastName"
FROM employees AS e
LEFT JOIN employees AS m
  ON m."employeeNumber" = e."reportsTo";
```


---

## 29) Get orderdetails with product vendor

**Question**: Get orderdetails with product vendor

**SQL**:
```sql
SELECT
  od."orderNumber",
  od."productCode",
  p."productVendor",
  od."quantityOrdered",
  od."priceEach"
FROM orderdetails AS od
JOIN products AS p
  ON p."productCode" = od."productCode";
```

---

## 30) Get payments with customer country

**Question**: Get payments with customer country

**SQL**:
```sql
SELECT
  p."customerNumber",
  c."customerName",
  c."country",
  p."paymentDate",
  p."amount"
FROM payments AS p
JOIN customers AS c
  ON c."customerNumber" = p."customerNumber";
```

---

## 31) Count customers per country

**Question**: Count customers per country

**SQL**:
```sql
SELECT
  c."country",
  COUNT(*) AS "customerCount"
FROM customers AS c
GROUP BY c."country"
ORDER BY "customerCount" DESC, c."country";
```


---

## 32) Total payments per customer

**Question**: Total payments per customer

**SQL**:
```sql
SELECT
  c."customerNumber",
  c."customerName",
  SUM(p."amount") AS "totalPayments"
FROM customers AS c
JOIN payments AS p
  ON p."customerNumber" = c."customerNumber"
GROUP BY c."customerNumber", c."customerName"
ORDER BY "totalPayments" DESC;
```


---

## 33) Number of orders per status

**Question**: Number of orders per status

**SQL**:
```sql
SELECT
  o."status",
  COUNT(*) AS "orderCount"
FROM orders AS o
GROUP BY o."status"
ORDER BY "orderCount" DESC, o."status";
```


---

## 34) Products per product line

**Question**: Products per product line

**SQL**:
```sql
SELECT
  p."productLine",
  COUNT(*) AS "productCount"
FROM products AS p
GROUP BY p."productLine"
ORDER BY "productCount" DESC, p."productLine";
```


---

## 35) Employees per office

**Question**: Employees per office

**SQL**:
```sql
SELECT
  o."officeCode",
  o."city",
  COUNT(e."employeeNumber") AS "employeeCount"
FROM offices AS o
LEFT JOIN employees AS e
  ON e."officeCode" = o."officeCode"
GROUP BY o."officeCode", o."city"
ORDER BY "employeeCount" DESC, o."officeCode";
```


---

## 36) Total stock per product vendor

**Question**: Total stock per product vendor

**SQL**:
```sql
SELECT
  p."productVendor",
  SUM(p."quantityInStock") AS "totalStock"
FROM products AS p
GROUP BY p."productVendor"
ORDER BY "totalStock" DESC, p."productVendor";
```


---

## 37) Average buy price per product line

**Question**: Average buy price per product line

**SQL**:
```sql
SELECT
  p."productLine",
  AVG(p."buyPrice") AS "avgBuyPrice"
FROM products AS p
GROUP BY p."productLine"
ORDER BY "avgBuyPrice" DESC, p."productLine";
```


---

## 38) Orders per customer

**Question**: Orders per customer

**SQL**:
```sql
SELECT
  c."customerNumber",
  c."customerName",
  COUNT(o."orderNumber") AS "orderCount"
FROM customers AS c
LEFT JOIN orders AS o
  ON o."customerNumber" = c."customerNumber"
GROUP BY c."customerNumber", c."customerName"
ORDER BY "orderCount" DESC, c."customerNumber";
```


---

## 39) Max MSRP per product line

**Question**: Max MSRP per product line

**SQL**:
```sql
SELECT
  p."productLine",
  MAX(p."MSRP") AS "maxMsrp"
FROM products AS p
GROUP BY p."productLine"
ORDER BY "maxMsrp" DESC, p."productLine";
```


---

## 40) Min buy price per vendor

**Question**: Min buy price per vendor

**SQL**:
```sql
SELECT
  p."productVendor",
  MIN(p."buyPrice") AS "minBuyPrice"
FROM products AS p
GROUP BY p."productVendor"
ORDER BY "minBuyPrice" ASC, p."productVendor";
```


---

## 41) Total number of customers

**Question**: Total number of customers

**SQL**:
```sql
SELECT
  COUNT(*) AS "totalCustomers"
FROM customers;
```


---

## 42) Total number of products

**Question**: Total number of products

**SQL**:
```sql
SELECT
  COUNT(*) AS "totalProducts"
FROM products;
```


---

## 43) Total revenue from payments

**Question**: Total revenue from payments

**SQL**:
```sql
SELECT
  SUM(p."amount") AS "totalPaymentRevenue"
FROM payments AS p;
```


---

## 44) Average product price

**Question**: Average product price

**SQL**:
```sql
SELECT
  AVG(p."buyPrice") AS "avgBuyPrice"
FROM products AS p;
```


---

## 45) Max payment amount

**Question**: Max payment amount

**SQL**:
```sql
SELECT
  MAX(p."amount") AS "maxPaymentAmount"
FROM payments AS p;
```

---

## 46) Min payment amount

**Question**: Min payment amount

**SQL**:
```sql
SELECT
  MIN(p."amount") AS "minPaymentAmount"
FROM payments AS p;
```


---

## 47) Count total orders

**Question**: Count total orders

**SQL**:
```sql
SELECT
  COUNT(*) AS "totalOrders"
FROM orders;
```


---

## 48) Total quantity in stock

**Question**: Total quantity in stock

**SQL**:
```sql
SELECT
  SUM(p."quantityInStock") AS "totalQuantityInStock"
FROM products AS p;
```


---

## 49) Average MSRP

**Question**: Average MSRP

**SQL**:
```sql
SELECT
  AVG(p."MSRP") AS "avgMsrp"
FROM products AS p;
```


---

## 50) Number of employees

**Question**: Number of employees

**SQL**:
```sql
SELECT
  COUNT(*) AS "totalEmployees"
FROM employees;
```


---

# Part 2: Evaluation Strategy for Text-to-SQL Agents

## Goals
- Verify SQL correctness, not just syntactic validity.
- Ensure the returned results are accurate for the user intent.
- Measure robustness, efficiency, and self-correction behavior.

## Proposed Evaluation Methods

### 1) Exact SQL Match (strict)
- Compare generated SQL against a gold query (string or normalized).
- Use a SQL formatter + parser to normalize whitespace and ordering.
- Limitation: equivalent queries can look different.

### 2) Execution Accuracy (primary)
- Run both gold query and model query against the same database.
- Compare results using set equality (order-insensitive) and schema match.
- For aggregations, compare numeric values with a tolerance (e.g., 1e-6).

### 3) Component-Level Checks
- Table selection: verify required tables appear.
- Column selection: verify key columns used in SELECT, WHERE, GROUP BY, JOIN.
- Join correctness: validate join keys and join types.
- Filter correctness: confirm predicates match the question intent.

### 4) Error Handling and Retry
- Track if the first query fails and whether retries converge to a correct query.
- Measure number of retries and time to success.

### 5) Natural Language Answer Quality
- If the agent returns a natural language answer, verify it matches the query result.
- Use a rubric: correctness, completeness, and clarity.

### 6) Efficiency and Safety
- Record query execution time and ensure no unsafe statements (only SELECT).
- Flag expensive patterns (cartesian joins, missing filters).

## Metrics Summary
- Exact Match Rate: percent of queries matching gold SQL after normalization.
- Execution Accuracy: percent of queries producing identical results to gold.
- Component Accuracy: per-component precision/recall (tables, columns, joins).
- Retry Success Rate: percent of failures that recover to correct results.
- Avg Latency: mean query execution time.
- Safety Rate: percent of queries that are read-only and safe.

## Evaluation Procedure (Recommended)
1) Run gold queries and cache result sets.
2) Run model queries on the same database.
3) Compare results with set-based equality and schema checks.
4) Log errors, retries, and execution times.
5) Score using the metrics above and report a summary.

---

# Appendix: How to Run (Docker + psql)

## Start PostgreSQL (Docker)
```powershell
docker run --name mydb -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mydb -p 5432:5432 -d postgres:15
```

## Seed the Database
```powershell
Get-Content .\seed.sql | docker exec -i mydb psql -U postgres -d mydb
```

## Connect with psql
```powershell
psql -h localhost -U postgres -d mydb
```

## Helpful psql settings
```sql
\x on
\pset pager off
```

## Large result tips
```sql
SELECT COUNT(*) FROM (<your_query_here>) AS q;
SELECT * FROM (<your_query_here>) AS q LIMIT 5;
```
