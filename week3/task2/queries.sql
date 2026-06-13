-- Q1: List all products
SELECT
  p."productCode",
  p."productName",
  p."productLine",
  p."quantityInStock",
  p."buyPrice",
  p."MSRP"
FROM products AS p;

-- Q2: Get all customers
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

-- Q3: Show all orders
SELECT
  o."orderNumber",
  o."orderDate",
  o."requiredDate",
  o."shippedDate",
  o."status",
  o."comments",
  o."customerNumber"
FROM orders AS o;

-- Q4: List all employees
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

-- Q5: Get all offices
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

-- Q6: Show all product lines
SELECT
  pl."productLine",
  pl."textDescription",
  pl."htmlDescription",
  pl."image"
FROM productlines AS pl;

-- Q7: List all payments
SELECT
  p."customerNumber",
  p."checkNumber",
  p."paymentDate",
  p."amount"
FROM payments AS p;

-- Q8: Get product names and prices
SELECT
  p."productName",
  p."buyPrice",
  p."MSRP"
FROM products AS p;

-- Q9: Get customer names and cities
SELECT
  c."customerName",
  c."city"
FROM customers AS c;

-- Q10: List employee first and last names
SELECT
  e."firstName",
  e."lastName"
FROM employees AS e;

-- Q11: Get all order dates
SELECT
  o."orderDate"
FROM orders AS o;

-- Q12: Show product vendor list
SELECT DISTINCT
  p."productVendor"
FROM products AS p
ORDER BY p."productVendor";

-- Q13: Get all product codes
SELECT
  p."productCode"
FROM products AS p;

-- Q14: List all countries from offices
SELECT DISTINCT
  o."country"
FROM offices AS o
ORDER BY o."country";

-- Q15: Show all order statuses
SELECT DISTINCT
  o."status"
FROM orders AS o
ORDER BY o."status";

-- Q16: Get all payment amounts
SELECT
  p."amount"
FROM payments AS p;

-- Q17: List all job titles
SELECT DISTINCT
  e."jobTitle"
FROM employees AS e
ORDER BY e."jobTitle";

-- Q18: Get customer phone numbers
SELECT
  c."customerName",
  c."phone"
FROM customers AS c;

-- Q19: Show product MSRP values
SELECT
  p."productName",
  p."MSRP"
FROM products AS p;

-- Q20: List order numbers
SELECT
  o."orderNumber"
FROM orders AS o;

-- Q21: Get orders with customer names
SELECT
  o."orderNumber",
  o."orderDate",
  o."status",
  c."customerName"
FROM orders AS o
JOIN customers AS c
  ON c."customerNumber" = o."customerNumber";

-- Q22: Get employees with office city
SELECT
  e."employeeNumber",
  e."firstName",
  e."lastName",
  o."city" AS "officeCity"
FROM employees AS e
JOIN offices AS o
  ON o."officeCode" = e."officeCode";

-- Q23: Get payments with customer names
SELECT
  p."customerNumber",
  c."customerName",
  p."checkNumber",
  p."paymentDate",
  p."amount"
FROM payments AS p
JOIN customers AS c
  ON c."customerNumber" = p."customerNumber";

-- Q24: Get order details with product names
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

-- Q25: Get products with product line description
SELECT
  p."productCode",
  p."productName",
  p."productLine",
  pl."textDescription"
FROM products AS p
JOIN productlines AS pl
  ON pl."productLine" = p."productLine";

-- Q26: Get customers with sales rep names
SELECT
  c."customerNumber",
  c."customerName",
  c."salesRepEmployeeNumber",
  e."firstName" AS "salesRepFirstName",
  e."lastName" AS "salesRepLastName"
FROM customers AS c
LEFT JOIN employees AS e
  ON e."employeeNumber" = c."salesRepEmployeeNumber";

-- Q27: Get orders with customer city
SELECT
  o."orderNumber",
  o."orderDate",
  o."status",
  c."customerName",
  c."city"
FROM orders AS o
JOIN customers AS c
  ON c."customerNumber" = o."customerNumber";

-- Q28: Get employees and their manager
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

-- Q29: Get orderdetails with product vendor
SELECT
  od."orderNumber",
  od."productCode",
  p."productVendor",
  od."quantityOrdered",
  od."priceEach"
FROM orderdetails AS od
JOIN products AS p
  ON p."productCode" = od."productCode";

-- Q30: Get payments with customer country
SELECT
  p."customerNumber",
  c."customerName",
  c."country",
  p."paymentDate",
  p."amount"
FROM payments AS p
JOIN customers AS c
  ON c."customerNumber" = p."customerNumber";

-- Q31: Count customers per country
SELECT
  c."country",
  COUNT(*) AS "customerCount"
FROM customers AS c
GROUP BY c."country"
ORDER BY "customerCount" DESC, c."country";

-- Q32: Total payments per customer
SELECT
  c."customerNumber",
  c."customerName",
  SUM(p."amount") AS "totalPayments"
FROM customers AS c
JOIN payments AS p
  ON p."customerNumber" = c."customerNumber"
GROUP BY c."customerNumber", c."customerName"
ORDER BY "totalPayments" DESC;

-- Q33: Number of orders per status
SELECT
  o."status",
  COUNT(*) AS "orderCount"
FROM orders AS o
GROUP BY o."status"
ORDER BY "orderCount" DESC, o."status";

-- Q34: Products per product line
SELECT
  p."productLine",
  COUNT(*) AS "productCount"
FROM products AS p
GROUP BY p."productLine"
ORDER BY "productCount" DESC, p."productLine";

-- Q35: Employees per office
SELECT
  o."officeCode",
  o."city",
  COUNT(e."employeeNumber") AS "employeeCount"
FROM offices AS o
LEFT JOIN employees AS e
  ON e."officeCode" = o."officeCode"
GROUP BY o."officeCode", o."city"
ORDER BY "employeeCount" DESC, o."officeCode";

-- Q36: Total stock per product vendor
SELECT
  p."productVendor",
  SUM(p."quantityInStock") AS "totalStock"
FROM products AS p
GROUP BY p."productVendor"
ORDER BY "totalStock" DESC, p."productVendor";

-- Q37: Average buy price per product line
SELECT
  p."productLine",
  AVG(p."buyPrice") AS "avgBuyPrice"
FROM products AS p
GROUP BY p."productLine"
ORDER BY "avgBuyPrice" DESC, p."productLine";

-- Q38: Orders per customer
SELECT
  c."customerNumber",
  c."customerName",
  COUNT(o."orderNumber") AS "orderCount"
FROM customers AS c
LEFT JOIN orders AS o
  ON o."customerNumber" = c."customerNumber"
GROUP BY c."customerNumber", c."customerName"
ORDER BY "orderCount" DESC, c."customerNumber";

-- Q39: Max MSRP per product line
SELECT
  p."productLine",
  MAX(p."MSRP") AS "maxMsrp"
FROM products AS p
GROUP BY p."productLine"
ORDER BY "maxMsrp" DESC, p."productLine";

-- Q40: Min buy price per vendor
SELECT
  p."productVendor",
  MIN(p."buyPrice") AS "minBuyPrice"
FROM products AS p
GROUP BY p."productVendor"
ORDER BY "minBuyPrice" ASC, p."productVendor";

-- Q41: Total number of customers
SELECT
  COUNT(*) AS "totalCustomers"
FROM customers;

-- Q42: Total number of products
SELECT
  COUNT(*) AS "totalProducts"
FROM products;

-- Q43: Total revenue from payments
SELECT
  SUM(p."amount") AS "totalPaymentRevenue"
FROM payments AS p;

-- Q44: Average product price
SELECT
  AVG(p."buyPrice") AS "avgBuyPrice"
FROM products AS p;

-- Q45: Max payment amount
SELECT
  MAX(p."amount") AS "maxPaymentAmount"
FROM payments AS p;

-- Q46: Min payment amount
SELECT
  MIN(p."amount") AS "minPaymentAmount"
FROM payments AS p;

-- Q47: Count total orders
SELECT
  COUNT(*) AS "totalOrders"
FROM orders;

-- Q48: Total quantity in stock
SELECT
  SUM(p."quantityInStock") AS "totalQuantityInStock"
FROM products AS p;

-- Q49: Average MSRP
SELECT
  AVG(p."MSRP") AS "avgMsrp"
FROM products AS p;

-- Q50: Number of employees
SELECT
  COUNT(*) AS "totalEmployees"
FROM employees;
