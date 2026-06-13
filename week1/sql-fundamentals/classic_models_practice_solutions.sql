USE classicmodels;

-- 1. Show all the customers whose creditLimit is greater than 20000
SELECT *
FROM customers
WHERE creditLimit > 20000;

-- 2. Show the employees who report to VP Sales.
SELECT e.*
FROM employees e
JOIN employees vp ON e.reportsTo = vp.employeeNumber
WHERE vp.jobTitle = 'VP Sales';

-- 3. Find all the customers who have set their state while filling the forms and Lives in USA
--    and credit limit is between 100000 and 200000.
SELECT *
FROM customers
WHERE state IS NOT NULL
  AND country = 'USA'
  AND creditLimit BETWEEN 100000 AND 200000;

-- 4. Find all the employees who report to Sales Managers of all types.
SELECT e.*
FROM employees e
JOIN employees m ON e.reportsTo = m.employeeNumber
WHERE m.jobTitle LIKE '%Sales Manager%'
   OR m.jobTitle LIKE '%Sale Manager%';

-- 5. Find the average credit limit of customers of each country.
SELECT country, AVG(creditLimit) AS averageCreditLimit
FROM customers
GROUP BY country;

-- 6. Find the total no. of orders for each date and customer.
--    Show only dates with total number of orders greater than 10 for date and customer.
SELECT orderDate, customerNumber, COUNT(*) AS totalOrders
FROM orders
GROUP BY orderDate, customerNumber
HAVING COUNT(*) > 10;

-- 7. Find the name of the supervisor, job title of supervisor and total no. of supervisee
--    using subquery. (Without using Join operation)
SELECT
  CONCAT(firstName, ' ', lastName) AS supervisorName,
  jobTitle AS supervisorJobTitle,
  (SELECT COUNT(*)
   FROM employees e
   WHERE e.reportsTo = s.employeeNumber) AS totalSupervisee
FROM employees s
WHERE EXISTS (
  SELECT 1
  FROM employees e
  WHERE e.reportsTo = s.employeeNumber
);

-- 8. Find the name of the supervisor, job title of supervisor and total no. of supervisee
--    using subquery. (With using Join operation)
SELECT
  CONCAT(s.firstName, ' ', s.lastName) AS supervisorName,
  s.jobTitle AS supervisorJobTitle,
  COUNT(e.employeeNumber) AS totalSupervisee
FROM employees s
JOIN employees e ON e.reportsTo = s.employeeNumber
GROUP BY s.employeeNumber, s.firstName, s.lastName, s.jobTitle;

-- 9. Find all customers with a credit limit greater than average credit limit using WITH Clause.
WITH avg_credit AS (
  SELECT AVG(creditLimit) AS avgCreditLimit
  FROM customers
)
SELECT c.*
FROM customers c
CROSS JOIN avg_credit a
WHERE c.creditLimit > a.avgCreditLimit;

-- 10. Find the rank of customer. Then, find the customer with the third highest credit limit.
WITH ranked_customers AS (
  SELECT
    customerNumber,
    customerName,
    creditLimit,
    RANK() OVER (ORDER BY creditLimit DESC) AS credit_rank
  FROM customers
)
SELECT *
FROM ranked_customers
ORDER BY credit_rank, customerName;

WITH ranked_customers AS (
  SELECT
    customerNumber,
    customerName,
    creditLimit,
    DENSE_RANK() OVER (ORDER BY creditLimit DESC) AS credit_rank
  FROM customers
)
SELECT *
FROM ranked_customers
WHERE credit_rank = 3;

-- 11. Generate a report that shows total no. of employees working in each office.
SELECT officeCode, COUNT(*) AS totalEmployees
FROM employees
GROUP BY officeCode;

-- 12. Generate a report that shows total no. of customers visited each office.
SELECT e.officeCode, COUNT(c.customerNumber) AS totalCustomers
FROM offices o
JOIN employees e ON o.officeCode = e.officeCode
LEFT JOIN customers c ON c.salesRepEmployeeNumber = e.employeeNumber
GROUP BY e.officeCode
ORDER BY e.officeCode;

-- 13. Generate a report that shows total payment received by each office using payment tables and essential tables.
SELECT
  o.officeCode,
  o.city AS officeName,
  o.state,
  o.country,
  SUM(p.amount) AS totalPaymentsReceived
FROM offices o
JOIN employees e ON e.officeCode = o.officeCode
JOIN customers c ON c.salesRepEmployeeNumber = e.employeeNumber
JOIN payments p ON p.customerNumber = c.customerNumber
GROUP BY o.officeCode, o.city, o.state, o.country
ORDER BY o.officeCode;

-- 14. Generate a report that shows total sales(in amount) by each office using order details table and other essential tables.
SELECT
  o.officeCode,
  o.city AS officeName,
  o.state,
  o.country,
  SUM(od.quantityOrdered * od.priceEach) AS totalSalesAmount
FROM offices o
JOIN employees e ON e.officeCode = o.officeCode
JOIN customers c ON c.salesRepEmployeeNumber = e.employeeNumber
JOIN orders ord ON ord.customerNumber = c.customerNumber
JOIN orderdetails od ON od.orderNumber = ord.orderNumber
GROUP BY o.officeCode, o.city, o.state, o.country
ORDER BY o.officeCode;

-- 15. Generate a report that shows total payment pending for each office.
WITH payments_by_customer AS (
  SELECT customerNumber, SUM(amount) AS totalPaid
  FROM payments
  GROUP BY customerNumber
),
sales_by_customer AS (
  SELECT customerNumber, SUM(quantityOrdered * priceEach) AS totalSales
  FROM orders ord
  JOIN orderdetails od ON od.orderNumber = ord.orderNumber
  GROUP BY customerNumber
)
SELECT
  o.officeCode,
  o.city AS officeName,
  o.state,
  o.country,
  SUM(COALESCE(s.totalSales, 0) - COALESCE(p.totalPaid, 0)) AS totalPaymentPending
FROM offices o
JOIN employees e ON e.officeCode = o.officeCode
JOIN customers c ON c.salesRepEmployeeNumber = e.employeeNumber
LEFT JOIN sales_by_customer s ON s.customerNumber = c.customerNumber
LEFT JOIN payments_by_customer p ON p.customerNumber = c.customerNumber
GROUP BY o.officeCode, o.city, o.state, o.country
ORDER BY o.officeCode;

-- 16. Find the creditLimit of each person, proportion of creditLimit of each person in each country.
SELECT
  customerNumber,
  customerName,
  country,
  creditLimit,
  creditLimit / SUM(creditLimit) OVER (PARTITION BY country) AS creditLimitProportion
FROM customers
ORDER BY country, customerName;

-- 17. Create a view showing the customer name, complete address, and their total number of orders.
CREATE OR REPLACE VIEW customer_order_summary AS
SELECT
  c.customerNumber,
  c.customerName,
  CONCAT_WS(', ', c.addressLine1, c.addressLine2, c.city, c.state, c.postalCode, c.country) AS completeAddress,
  COUNT(o.orderNumber) AS totalOrders
FROM customers c
LEFT JOIN orders o ON o.customerNumber = c.customerNumber
GROUP BY c.customerNumber, c.customerName, c.addressLine1, c.addressLine2, c.city, c.state, c.postalCode, c.country;

-- 18. Update the country of a customer (use any one record).
UPDATE customers
SET country = 'United States'
WHERE customerNumber = 103;

-- 19. Delete all payments below 20,000.
DELETE FROM payments
WHERE amount < 20000;

-- 20. Add new payments manually for an existing customer.
INSERT INTO payments (customerNumber, checkNumber, paymentDate, amount)
VALUES (103, 'NEW0001', '2026-05-04', 25000.00);