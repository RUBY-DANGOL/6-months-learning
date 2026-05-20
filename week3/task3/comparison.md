# Task 3: Generated SQL Comparison

This report compares auto-generated SQL against Task 2 reference queries.

## Q1: List all products

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productCode",
  "products"."productName",
  "products"."productLine",
  "products"."quantityInStock",
  "products"."buyPrice",
  "products"."MSRP"
FROM "products";
```

Reference SQL:
```
SELECT
  p."productCode",
  p."productName",
  p."productLine",
  p."quantityInStock",
  p."buyPrice",
  p."MSRP"
FROM products AS p;
```

## Q2: Get all customers

Status: DIFFERENT

Generated SQL:
```
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  "customers"."contactLastName",
  "customers"."contactFirstName",
  "customers"."phone",
  "customers"."addressLine1",
  "customers"."addressLine2",
  "customers"."city",
  "customers"."state",
  "customers"."postalCode",
  "customers"."country",
  "customers"."salesRepEmployeeNumber",
  "customers"."creditLimit"
FROM "customers";
```

Reference SQL:
```
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
FROM customers AS c;
```

## Q3: Show all orders

Status: DIFFERENT

Generated SQL:
```
SELECT
  "orders"."orderNumber",
  "orders"."orderDate",
  "orders"."requiredDate",
  "orders"."shippedDate",
  "orders"."status",
  "orders"."comments",
  "orders"."customerNumber"
FROM "orders";
```

Reference SQL:
```
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

## Q4: List all employees

Status: DIFFERENT

Generated SQL:
```
SELECT
  "employees"."employeeNumber",
  "employees"."lastName",
  "employees"."firstName",
  "employees"."extension",
  "employees"."email",
  "employees"."officeCode",
  "employees"."reportsTo",
  "employees"."jobTitle"
FROM "employees";
```

Reference SQL:
```
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

## Q5: Get all offices

Status: DIFFERENT

Generated SQL:
```
SELECT
  "offices"."officeCode",
  "offices"."city",
  "offices"."phone",
  "offices"."addressLine1",
  "offices"."addressLine2",
  "offices"."state",
  "offices"."country",
  "offices"."postalCode",
  "offices"."territory"
FROM "offices";
```

Reference SQL:
```
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

## Q6: Show all product lines

Status: DIFFERENT

Generated SQL:
```
SELECT
  "productlines"."productLine",
  "productlines"."textDescription",
  "productlines"."htmlDescription",
  "productlines"."image"
FROM "productlines";
```

Reference SQL:
```
SELECT
  pl."productLine",
  pl."textDescription",
  pl."htmlDescription",
  pl."image"
FROM productlines AS pl;
```

## Q7: List all payments

Status: DIFFERENT

Generated SQL:
```
SELECT
  "payments"."customerNumber",
  "payments"."checkNumber",
  "payments"."paymentDate",
  "payments"."amount"
FROM "payments";
```

Reference SQL:
```
SELECT
  p."customerNumber",
  p."checkNumber",
  p."paymentDate",
  p."amount"
FROM payments AS p;
```

## Q8: Get product names and prices

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productName",
  "products"."buyPrice",
  "products"."MSRP"
FROM "products";
```

Reference SQL:
```
SELECT
  p."productName",
  p."buyPrice",
  p."MSRP"
FROM products AS p;
```

## Q9: Get customer names and cities

Status: DIFFERENT

Generated SQL:
```
SELECT
  "customers"."customerName",
  "customers"."city"
FROM "customers";
```

Reference SQL:
```
SELECT
  c."customerName",
  c."city"
FROM customers AS c;
```

## Q10: List employee first and last names

Status: DIFFERENT

Generated SQL:
```
SELECT
  "employees"."firstName",
  "employees"."lastName"
FROM "employees";
```

Reference SQL:
```
SELECT
  e."firstName",
  e."lastName"
FROM employees AS e;
```

## Q11: Get all order dates

Status: DIFFERENT

Generated SQL:
```
SELECT
  "orders"."orderDate"
FROM "orders";
```

Reference SQL:
```
SELECT
  o."orderDate"
FROM orders AS o;
```

## Q12: Show product vendor list

Status: DIFFERENT

Generated SQL:
```
SELECT DISTINCT
  "products"."productVendor"
FROM "products";
```

Reference SQL:
```
SELECT DISTINCT
  p."productVendor"
FROM products AS p
ORDER BY p."productVendor";
```

## Q13: Get all product codes

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productCode"
FROM "products";
```

Reference SQL:
```
SELECT
  p."productCode"
FROM products AS p;
```

## Q14: List all countries from offices

Status: DIFFERENT

Generated SQL:
```
SELECT DISTINCT
  COUNT(*) AS "count"
FROM "offices";
```

Reference SQL:
```
SELECT DISTINCT
  o."country"
FROM offices AS o
ORDER BY o."country";
```

## Q15: Show all order statuses

Status: DIFFERENT

Generated SQL:
```
SELECT DISTINCT
  "orders"."status"
FROM "orders";
```

Reference SQL:
```
SELECT DISTINCT
  o."status"
FROM orders AS o
ORDER BY o."status";
```

## Q16: Get all payment amounts

Status: DIFFERENT

Generated SQL:
```
SELECT
  "payments"."amount"
FROM "payments";
```

Reference SQL:
```
SELECT
  p."amount"
FROM payments AS p;
```

## Q17: List all job titles

Status: DIFFERENT

Generated SQL:
```
SELECT DISTINCT
  "employees"."jobTitle"
FROM "employees";
```

Reference SQL:
```
SELECT DISTINCT
  e."jobTitle"
FROM employees AS e
ORDER BY e."jobTitle";
```

## Q18: Get customer phone numbers

Status: DIFFERENT

Generated SQL:
```
SELECT
  "customers"."customerName",
  "customers"."phone"
FROM "customers";
```

Reference SQL:
```
SELECT
  c."customerName",
  c."phone"
FROM customers AS c;
```

## Q19: Show product MSRP values

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productName",
  "products"."MSRP"
FROM "products";
```

Reference SQL:
```
SELECT
  p."productName",
  p."MSRP"
FROM products AS p;
```

## Q20: List order numbers

Status: DIFFERENT

Generated SQL:
```
SELECT
  "orders"."orderNumber"
FROM "orders";
```

Reference SQL:
```
SELECT
  o."orderNumber"
FROM orders AS o;
```

## Q21: Get orders with customer names

Status: DIFFERENT

Generated SQL:
```
SELECT
  "orders"."orderNumber",
  "orders"."orderDate",
  "orders"."status",
  "customers"."customerName"
FROM "orders"
JOIN "customers" ON "orders"."customerNumber" = "customers"."customerNumber";
```

Reference SQL:
```
SELECT
  o."orderNumber",
  o."orderDate",
  o."status",
  c."customerName"
FROM orders AS o
JOIN customers AS c
  ON c."customerNumber" = o."customerNumber";
```

## Q22: Get employees with office city

Status: DIFFERENT

Generated SQL:
```
SELECT
  "employees"."employeeNumber",
  "employees"."firstName",
  "employees"."lastName",
  "employees"."city"
FROM "employees"
JOIN "offices" ON "employees"."officeCode" = "offices"."officeCode";
```

Reference SQL:
```
SELECT
  e."employeeNumber",
  e."firstName",
  e."lastName",
  o."city" AS "officeCity"
FROM employees AS e
JOIN offices AS o
  ON o."officeCode" = e."officeCode";
```

## Q23: Get payments with customer names

Status: DIFFERENT

Generated SQL:
```
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  "payments"."checkNumber",
  "payments"."paymentDate",
  "payments"."amount"
FROM "payments"
JOIN "customers" ON "payments"."customerNumber" = "customers"."customerNumber";
```

Reference SQL:
```
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

## Q24: Get order details with product names

Status: DIFFERENT

Generated SQL:
```
SELECT
  "orderdetails"."orderNumber",
  "products"."productCode",
  "products"."productName",
  "orderdetails"."quantityOrdered",
  "orderdetails"."priceEach",
  "orderdetails"."orderLineNumber"
FROM "orderdetails"
JOIN "products" ON "orderdetails"."productCode" = "products"."productCode";
```

Reference SQL:
```
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

## Q25: Get products with product line description

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productCode",
  "products"."productName",
  "products"."productLine",
  "productlines"."textDescription"
FROM "products"
JOIN "productlines" ON "products"."productLine" = "productlines"."productLine";
```

Reference SQL:
```
SELECT
  p."productCode",
  p."productName",
  p."productLine",
  pl."textDescription"
FROM products AS p
JOIN productlines AS pl
  ON pl."productLine" = p."productLine";
```

## Q26: Get customers with sales rep names

Status: DIFFERENT

Generated SQL:
```
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  "customers"."salesRepEmployeeNumber",
  "employees"."firstName" AS "salesRepFirstName",
  "employees"."lastName" AS "salesRepLastName"
FROM "customers"
LEFT JOIN "employees" ON "customers"."salesRepEmployeeNumber" = "employees"."employeeNumber";
```

Reference SQL:
```
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

## Q27: Get orders with customer city

Status: DIFFERENT

Generated SQL:
```
SELECT
  "orders"."orderNumber",
  "orders"."orderDate",
  "orders"."status",
  "customers"."customerName",
  "customers"."city"
FROM "orders"
JOIN "customers" ON "orders"."customerNumber" = "customers"."customerNumber";
```

Reference SQL:
```
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

## Q28: Get employees and their manager

Status: DIFFERENT

Generated SQL:
```
SELECT
  "employees"."employeeNumber",
  "employees"."firstName",
  "employees"."lastName",
  "manager"."employeeNumber" AS "managerNumber",
  "manager"."firstName" AS "managerFirstName",
  "manager"."lastName" AS "managerLastName"
FROM "employees"
LEFT JOIN "manager" ON "employees"."reportsTo" = "manager"."employeeNumber"
LEFT JOIN "employees" AS "manager" ON "employees"."reportsTo" = "manager"."employeeNumber";
```

Reference SQL:
```
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

## Q29: Get orderdetails with product vendor

Status: DIFFERENT

Generated SQL:
```
SELECT
  "orderdetails"."orderNumber",
  "products"."productCode",
  "products"."productVendor",
  "orderdetails"."quantityOrdered",
  "orderdetails"."priceEach"
FROM "orderdetails"
JOIN "products" ON "orderdetails"."productCode" = "products"."productCode";
```

Reference SQL:
```
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

## Q30: Get payments with customer country

Status: DIFFERENT

Generated SQL:
```
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  "customers"."country",
  "payments"."paymentDate",
  "payments"."amount",
  COUNT(*) AS "count"
FROM "payments"
JOIN "customers" ON "payments"."customerNumber" = "customers"."customerNumber"
GROUP BY "customers"."customerNumber", "customers"."customerName", "customers"."country", "payments"."paymentDate", "payments"."amount";
```

Reference SQL:
```
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

## Q31: Count customers per country

Status: DIFFERENT

Generated SQL:
```
SELECT
  "customers"."country",
  "customers"."customerNumber",
  COUNT(*) AS "count"
FROM "customers"
GROUP BY "customers"."country", "customers"."customerNumber";
```

Reference SQL:
```
SELECT
  c."country",
  COUNT(*) AS "customerCount"
FROM customers AS c
GROUP BY c."country"
ORDER BY "customerCount" DESC, c."country";
```

## Q32: Total payments per customer

Status: DIFFERENT

Generated SQL:
```
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  SUM("payments"."amount") AS "sumValue"
FROM "customers"
JOIN "payments" ON "payments"."customerNumber" = "customers"."customerNumber"
GROUP BY "customers"."customerNumber", "customers"."customerName";
```

Reference SQL:
```
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

## Q33: Number of orders per status

Status: DIFFERENT

Generated SQL:
```
SELECT
  "orders"."status",
  "orders"."orderNumber",
  COUNT(*) AS "count"
FROM "orders"
GROUP BY "orders"."status", "orders"."orderNumber";
```

Reference SQL:
```
SELECT
  o."status",
  COUNT(*) AS "orderCount"
FROM orders AS o
GROUP BY o."status"
ORDER BY "orderCount" DESC, o."status";
```

## Q34: Products per product line

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productLine",
  "products"."productCode",
  COUNT(*) AS "count"
FROM "products"
GROUP BY "products"."productLine", "products"."productCode";
```

Reference SQL:
```
SELECT
  p."productLine",
  COUNT(*) AS "productCount"
FROM products AS p
GROUP BY p."productLine"
ORDER BY "productCount" DESC, p."productLine";
```

## Q35: Employees per office

Status: DIFFERENT

Generated SQL:
```
SELECT
  "offices"."officeCode",
  "offices"."city",
  "employees"."employeeNumber",
  COUNT(*) AS "count"
FROM "offices"
JOIN "employees" ON "offices"."officeCode" = "employees"."officeCode"
GROUP BY "offices"."officeCode", "offices"."city", "employees"."employeeNumber";
```

Reference SQL:
```
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

## Q36: Total stock per product vendor

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productVendor",
  SUM("products"."quantityInStock") AS "sumValue"
FROM "products"
GROUP BY "products"."productVendor";
```

Reference SQL:
```
SELECT
  p."productVendor",
  SUM(p."quantityInStock") AS "totalStock"
FROM products AS p
GROUP BY p."productVendor"
ORDER BY "totalStock" DESC, p."productVendor";
```

## Q37: Average buy price per product line

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productLine",
  AVG("products"."buyPrice") AS "avgValue"
FROM "products"
GROUP BY "products"."productLine";
```

Reference SQL:
```
SELECT
  p."productLine",
  AVG(p."buyPrice") AS "avgBuyPrice"
FROM products AS p
GROUP BY p."productLine"
ORDER BY "avgBuyPrice" DESC, p."productLine";
```

## Q38: Orders per customer

Status: DIFFERENT

Generated SQL:
```
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  "orders"."orderNumber",
  COUNT(*) AS "count"
FROM "customers"
JOIN "orders" ON "customers"."customerNumber" = "orders"."customerNumber"
GROUP BY "customers"."customerNumber", "customers"."customerName", "orders"."orderNumber";
```

Reference SQL:
```
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

## Q39: Max MSRP per product line

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productLine",
  MAX("products"."MSRP") AS "maxValue"
FROM "products"
GROUP BY "products"."productLine";
```

Reference SQL:
```
SELECT
  p."productLine",
  MAX(p."MSRP") AS "maxMsrp"
FROM products AS p
GROUP BY p."productLine"
ORDER BY "maxMsrp" DESC, p."productLine";
```

## Q40: Min buy price per vendor

Status: DIFFERENT

Generated SQL:
```
SELECT
  "products"."productVendor",
  MIN("products"."buyPrice") AS "minValue"
FROM "products"
GROUP BY "products"."productVendor";
```

Reference SQL:
```
SELECT
  p."productVendor",
  MIN(p."buyPrice") AS "minBuyPrice"
FROM products AS p
GROUP BY p."productVendor"
ORDER BY "minBuyPrice" ASC, p."productVendor";
```

## Q41: Total number of customers

Status: DIFFERENT

Generated SQL:
```
SELECT
  COUNT(*) AS "count"
FROM "customers";
```

Reference SQL:
```
SELECT
  COUNT(*) AS "totalCustomers"
FROM customers;
```

## Q42: Total number of products

Status: DIFFERENT

Generated SQL:
```
SELECT
  COUNT(*) AS "count"
FROM "products";
```

Reference SQL:
```
SELECT
  COUNT(*) AS "totalProducts"
FROM products;
```

## Q43: Total revenue from payments

Status: DIFFERENT

Generated SQL:
```
SELECT
  SUM("payments"."amount") AS "sumValue"
FROM "payments";
```

Reference SQL:
```
SELECT
  SUM(p."amount") AS "totalPaymentRevenue"
FROM payments AS p;
```

## Q44: Average product price

Status: DIFFERENT

Generated SQL:
```
SELECT
  AVG("products"."buyPrice") AS "avgValue"
FROM "products";
```

Reference SQL:
```
SELECT
  AVG(p."buyPrice") AS "avgBuyPrice"
FROM products AS p;
```

## Q45: Max payment amount

Status: DIFFERENT

Generated SQL:
```
SELECT
  MAX("payments"."amount") AS "maxValue"
FROM "payments";
```

Reference SQL:
```
SELECT
  MAX(p."amount") AS "maxPaymentAmount"
FROM payments AS p;
```

## Q46: Min payment amount

Status: DIFFERENT

Generated SQL:
```
SELECT
  MIN("payments"."amount") AS "minValue"
FROM "payments";
```

Reference SQL:
```
SELECT
  MIN(p."amount") AS "minPaymentAmount"
FROM payments AS p;
```

## Q47: Count total orders

Status: DIFFERENT

Generated SQL:
```
SELECT
  COUNT(*) AS "count"
FROM "orders";
```

Reference SQL:
```
SELECT
  COUNT(*) AS "totalOrders"
FROM orders;
```

## Q48: Total quantity in stock

Status: DIFFERENT

Generated SQL:
```
SELECT
  SUM("products"."quantityInStock") AS "sumValue"
FROM "products";
```

Reference SQL:
```
SELECT
  SUM(p."quantityInStock") AS "totalQuantityInStock"
FROM products AS p;
```

## Q49: Average MSRP

Status: DIFFERENT

Generated SQL:
```
SELECT
  AVG("products"."MSRP") AS "avgValue"
FROM "products";
```

Reference SQL:
```
SELECT
  AVG(p."MSRP") AS "avgMsrp"
FROM products AS p;
```

## Q50: Number of employees

Status: DIFFERENT

Generated SQL:
```
SELECT
  COUNT(*) AS "count"
FROM "employees";
```

Reference SQL:
```
SELECT
  COUNT(*) AS "totalEmployees"
FROM employees;
```
