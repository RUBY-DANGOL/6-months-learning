-- Q1: List all products
SELECT
  "products"."productCode",
  "products"."productName",
  "products"."productLine",
  "products"."quantityInStock",
  "products"."buyPrice",
  "products"."MSRP"
FROM "products";

-- Q2: Get all customers
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

-- Q3: Show all orders
SELECT
  "orders"."orderNumber",
  "orders"."orderDate",
  "orders"."requiredDate",
  "orders"."shippedDate",
  "orders"."status",
  "orders"."comments",
  "orders"."customerNumber"
FROM "orders";

-- Q4: List all employees
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

-- Q5: Get all offices
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

-- Q6: Show all product lines
SELECT
  "productlines"."productLine",
  "productlines"."textDescription",
  "productlines"."htmlDescription",
  "productlines"."image"
FROM "productlines";

-- Q7: List all payments
SELECT
  "payments"."customerNumber",
  "payments"."checkNumber",
  "payments"."paymentDate",
  "payments"."amount"
FROM "payments";

-- Q8: Get product names and prices
SELECT
  "products"."productName",
  "products"."buyPrice",
  "products"."MSRP"
FROM "products";

-- Q9: Get customer names and cities
SELECT
  "customers"."customerName",
  "customers"."city"
FROM "customers";

-- Q10: List employee first and last names
SELECT
  "employees"."firstName",
  "employees"."lastName"
FROM "employees";

-- Q11: Get all order dates
SELECT
  "orders"."orderDate"
FROM "orders";

-- Q12: Show product vendor list
SELECT DISTINCT
  "products"."productVendor"
FROM "products";

-- Q13: Get all product codes
SELECT
  "products"."productCode"
FROM "products";

-- Q14: List all countries from offices
SELECT DISTINCT
  COUNT(*) AS "count"
FROM "offices";

-- Q15: Show all order statuses
SELECT DISTINCT
  "orders"."status"
FROM "orders";

-- Q16: Get all payment amounts
SELECT
  "payments"."amount"
FROM "payments";

-- Q17: List all job titles
SELECT DISTINCT
  "employees"."jobTitle"
FROM "employees";

-- Q18: Get customer phone numbers
SELECT
  "customers"."customerName",
  "customers"."phone"
FROM "customers";

-- Q19: Show product MSRP values
SELECT
  "products"."productName",
  "products"."MSRP"
FROM "products";

-- Q20: List order numbers
SELECT
  "orders"."orderNumber"
FROM "orders";

-- Q21: Get orders with customer names
SELECT
  "orders"."orderNumber",
  "orders"."orderDate",
  "orders"."status",
  "customers"."customerName"
FROM "orders"
JOIN "customers" ON "orders"."customerNumber" = "customers"."customerNumber";

-- Q22: Get employees with office city
SELECT
  "employees"."employeeNumber",
  "employees"."firstName",
  "employees"."lastName",
  "employees"."city"
FROM "employees"
JOIN "offices" ON "employees"."officeCode" = "offices"."officeCode";

-- Q23: Get payments with customer names
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  "payments"."checkNumber",
  "payments"."paymentDate",
  "payments"."amount"
FROM "payments"
JOIN "customers" ON "payments"."customerNumber" = "customers"."customerNumber";

-- Q24: Get order details with product names
SELECT
  "orderdetails"."orderNumber",
  "products"."productCode",
  "products"."productName",
  "orderdetails"."quantityOrdered",
  "orderdetails"."priceEach",
  "orderdetails"."orderLineNumber"
FROM "orderdetails"
JOIN "products" ON "orderdetails"."productCode" = "products"."productCode";

-- Q25: Get products with product line description
SELECT
  "products"."productCode",
  "products"."productName",
  "products"."productLine",
  "productlines"."textDescription"
FROM "products"
JOIN "productlines" ON "products"."productLine" = "productlines"."productLine";

-- Q26: Get customers with sales rep names
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  "customers"."salesRepEmployeeNumber",
  "employees"."firstName" AS "salesRepFirstName",
  "employees"."lastName" AS "salesRepLastName"
FROM "customers"
LEFT JOIN "employees" ON "customers"."salesRepEmployeeNumber" = "employees"."employeeNumber";

-- Q27: Get orders with customer city
SELECT
  "orders"."orderNumber",
  "orders"."orderDate",
  "orders"."status",
  "customers"."customerName",
  "customers"."city"
FROM "orders"
JOIN "customers" ON "orders"."customerNumber" = "customers"."customerNumber";

-- Q28: Get employees and their manager
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

-- Q29: Get orderdetails with product vendor
SELECT
  "orderdetails"."orderNumber",
  "products"."productCode",
  "products"."productVendor",
  "orderdetails"."quantityOrdered",
  "orderdetails"."priceEach"
FROM "orderdetails"
JOIN "products" ON "orderdetails"."productCode" = "products"."productCode";

-- Q30: Get payments with customer country
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

-- Q31: Count customers per country
SELECT
  "customers"."country",
  "customers"."customerNumber",
  COUNT(*) AS "count"
FROM "customers"
GROUP BY "customers"."country", "customers"."customerNumber";

-- Q32: Total payments per customer
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  SUM("payments"."amount") AS "sumValue"
FROM "customers"
JOIN "payments" ON "payments"."customerNumber" = "customers"."customerNumber"
GROUP BY "customers"."customerNumber", "customers"."customerName";

-- Q33: Number of orders per status
SELECT
  "orders"."status",
  "orders"."orderNumber",
  COUNT(*) AS "count"
FROM "orders"
GROUP BY "orders"."status", "orders"."orderNumber";

-- Q34: Products per product line
SELECT
  "products"."productLine",
  "products"."productCode",
  COUNT(*) AS "count"
FROM "products"
GROUP BY "products"."productLine", "products"."productCode";

-- Q35: Employees per office
SELECT
  "offices"."officeCode",
  "offices"."city",
  "employees"."employeeNumber",
  COUNT(*) AS "count"
FROM "offices"
JOIN "employees" ON "offices"."officeCode" = "employees"."officeCode"
GROUP BY "offices"."officeCode", "offices"."city", "employees"."employeeNumber";

-- Q36: Total stock per product vendor
SELECT
  "products"."productVendor",
  SUM("products"."quantityInStock") AS "sumValue"
FROM "products"
GROUP BY "products"."productVendor";

-- Q37: Average buy price per product line
SELECT
  "products"."productLine",
  AVG("products"."buyPrice") AS "avgValue"
FROM "products"
GROUP BY "products"."productLine";

-- Q38: Orders per customer
SELECT
  "customers"."customerNumber",
  "customers"."customerName",
  "orders"."orderNumber",
  COUNT(*) AS "count"
FROM "customers"
JOIN "orders" ON "customers"."customerNumber" = "orders"."customerNumber"
GROUP BY "customers"."customerNumber", "customers"."customerName", "orders"."orderNumber";

-- Q39: Max MSRP per product line
SELECT
  "products"."productLine",
  MAX("products"."MSRP") AS "maxValue"
FROM "products"
GROUP BY "products"."productLine";

-- Q40: Min buy price per vendor
SELECT
  "products"."productVendor",
  MIN("products"."buyPrice") AS "minValue"
FROM "products"
GROUP BY "products"."productVendor";

-- Q41: Total number of customers
SELECT
  COUNT(*) AS "count"
FROM "customers";

-- Q42: Total number of products
SELECT
  COUNT(*) AS "count"
FROM "products";

-- Q43: Total revenue from payments
SELECT
  SUM("payments"."amount") AS "sumValue"
FROM "payments";

-- Q44: Average product price
SELECT
  AVG("products"."buyPrice") AS "avgValue"
FROM "products";

-- Q45: Max payment amount
SELECT
  MAX("payments"."amount") AS "maxValue"
FROM "payments";

-- Q46: Min payment amount
SELECT
  MIN("payments"."amount") AS "minValue"
FROM "payments";

-- Q47: Count total orders
SELECT
  COUNT(*) AS "count"
FROM "orders";

-- Q48: Total quantity in stock
SELECT
  SUM("products"."quantityInStock") AS "sumValue"
FROM "products";

-- Q49: Average MSRP
SELECT
  AVG("products"."MSRP") AS "avgValue"
FROM "products";

-- Q50: Number of employees
SELECT
  COUNT(*) AS "count"
FROM "employees";
