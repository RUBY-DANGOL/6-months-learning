# SQL Question Decompositions

## 1) List all products
- Intent: Retrieve all products
- Tables: products
- Columns: productCode, productName, productLine, quantityInStock, buyPrice, MSRP
- Filters: None
- Joins: None

## 2) Get all customers
- Intent: Retrieve all customers
- Tables: customers
- Columns: customerNumber, customerName, contactLastName, contactFirstName, phone, addressLine1, addressLine2, city, state, postalCode, country, salesRepEmployeeNumber, creditLimit
- Filters: None
- Joins: None

## 3) Show all orders
- Intent: Retrieve all orders
- Tables: orders
- Columns: orderNumber, orderDate, requiredDate, shippedDate, status, comments, customerNumber
- Filters: None
- Joins: None

## 4) List all employees
- Intent: Retrieve all employees
- Tables: employees
- Columns: employeeNumber, lastName, firstName, extension, email, officeCode, reportsTo, jobTitle
- Filters: None
- Joins: None

## 5) Get all offices
- Intent: Retrieve all offices
- Tables: offices
- Columns: officeCode, city, phone, addressLine1, addressLine2, state, country, postalCode, territory
- Filters: None
- Joins: None

## 6) Show all product lines
- Intent: Retrieve all product lines
- Tables: productlines
- Columns: productLine, textDescription, htmlDescription, image
- Filters: None
- Joins: None

## 7) List all payments
- Intent: Retrieve all payments
- Tables: payments
- Columns: customerNumber, checkNumber, paymentDate, amount
- Filters: None
- Joins: None

## 8) Get product names and prices
- Intent: Retrieve product names and prices
- Tables: products
- Columns: productName, buyPrice, MSRP
- Filters: None
- Joins: None

## 9) Get customer names and cities
- Intent: Retrieve customer names and cities
- Tables: customers
- Columns: customerName, city
- Filters: None
- Joins: None

## 10) List employee first and last names
- Intent: Retrieve employee names
- Tables: employees
- Columns: firstName, lastName
- Filters: None
- Joins: None

## 11) Get all order dates
- Intent: Retrieve order dates
- Tables: orders
- Columns: orderDate
- Filters: None
- Joins: None

## 12) Show product vendor list
- Intent: Retrieve unique product vendors
- Tables: products
- Columns: productVendor
- Filters: None
- Joins: None

## 13) Get all product codes
- Intent: Retrieve product codes
- Tables: products
- Columns: productCode
- Filters: None
- Joins: None

## 14) List all countries from offices
- Intent: Retrieve unique office countries
- Tables: offices
- Columns: country
- Filters: None
- Joins: None

## 15) Show all order statuses
- Intent: Retrieve unique order statuses
- Tables: orders
- Columns: status
- Filters: None
- Joins: None

## 16) Get all payment amounts
- Intent: Retrieve payment amounts
- Tables: payments
- Columns: amount
- Filters: None
- Joins: None

## 17) List all job titles
- Intent: Retrieve unique job titles
- Tables: employees
- Columns: jobTitle
- Filters: None
- Joins: None

## 18) Get customer phone numbers
- Intent: Retrieve customer phone numbers
- Tables: customers
- Columns: customerName, phone
- Filters: None
- Joins: None

## 19) Show product MSRP values
- Intent: Retrieve product MSRP values
- Tables: products
- Columns: productName, MSRP
- Filters: None
- Joins: None

## 20) List order numbers
- Intent: Retrieve order numbers
- Tables: orders
- Columns: orderNumber
- Filters: None
- Joins: None

## 21) Get orders with customer names
- Intent: Retrieve orders with customer names
- Tables: orders, customers
- Columns: orderNumber, orderDate, status, customerName
- Filters: None
- Joins: orders.customerNumber = customers.customerNumber

## 22) Get employees with office city
- Intent: Retrieve employees with office city
- Tables: employees, offices
- Columns: employeeNumber, firstName, lastName, office city
- Filters: None
- Joins: employees.officeCode = offices.officeCode

## 23) Get payments with customer names
- Intent: Retrieve payments with customer names
- Tables: payments, customers
- Columns: customerNumber, customerName, checkNumber, paymentDate, amount
- Filters: None
- Joins: payments.customerNumber = customers.customerNumber

## 24) Get order details with product names
- Intent: Retrieve order details with product names
- Tables: orderdetails, products
- Columns: orderNumber, productCode, productName, quantityOrdered, priceEach, orderLineNumber
- Filters: None
- Joins: orderdetails.productCode = products.productCode

## 25) Get products with product line description
- Intent: Retrieve products with product line descriptions
- Tables: products, productlines
- Columns: productCode, productName, productLine, textDescription
- Filters: None
- Joins: products.productLine = productlines.productLine

## 26) Get customers with sales rep names
- Intent: Retrieve customers with sales rep names
- Tables: customers, employees
- Columns: customerNumber, customerName, salesRepEmployeeNumber, salesRepFirstName, salesRepLastName
- Filters: None
- Joins: customers.salesRepEmployeeNumber = employees.employeeNumber

## 27) Get orders with customer city
- Intent: Retrieve orders with customer city
- Tables: orders, customers
- Columns: orderNumber, orderDate, status, customerName, city
- Filters: None
- Joins: orders.customerNumber = customers.customerNumber

## 28) Get employees and their manager
- Intent: Retrieve employees with their manager
- Tables: employees (self-join)
- Columns: employeeNumber, firstName, lastName, managerNumber, managerFirstName, managerLastName
- Filters: None
- Joins: employees.reportsTo = manager.employeeNumber

## 29) Get orderdetails with product vendor
- Intent: Retrieve order details with product vendor
- Tables: orderdetails, products
- Columns: orderNumber, productCode, productVendor, quantityOrdered, priceEach
- Filters: None
- Joins: orderdetails.productCode = products.productCode

## 30) Get payments with customer country
- Intent: Retrieve payments with customer country
- Tables: payments, customers
- Columns: customerNumber, customerName, country, paymentDate, amount
- Filters: None
- Joins: payments.customerNumber = customers.customerNumber

## 31) Count customers per country
- Intent: Count customers grouped by country
- Tables: customers
- Columns: country, customerNumber
- Filters: None
- Joins: None

## 32) Total payments per customer
- Intent: Sum payments grouped by customer
- Tables: customers, payments
- Columns: customerNumber, customerName, amount
- Filters: None
- Joins: payments.customerNumber = customers.customerNumber

## 33) Number of orders per status
- Intent: Count orders grouped by status
- Tables: orders
- Columns: status, orderNumber
- Filters: None
- Joins: None

## 34) Products per product line
- Intent: Count products grouped by product line
- Tables: products
- Columns: productLine, productCode
- Filters: None
- Joins: None

## 35) Employees per office
- Intent: Count employees grouped by office
- Tables: offices, employees
- Columns: officeCode, city, employeeNumber
- Filters: None
- Joins: offices.officeCode = employees.officeCode

## 36) Total stock per product vendor
- Intent: Sum quantity in stock grouped by product vendor
- Tables: products
- Columns: productVendor, quantityInStock
- Filters: None
- Joins: None

## 37) Average buy price per product line
- Intent: Average buy price grouped by product line
- Tables: products
- Columns: productLine, buyPrice
- Filters: None
- Joins: None

## 38) Orders per customer
- Intent: Count orders grouped by customer
- Tables: customers, orders
- Columns: customerNumber, customerName, orderNumber
- Filters: None
- Joins: customers.customerNumber = orders.customerNumber

## 39) Max MSRP per product line
- Intent: Max MSRP grouped by product line
- Tables: products
- Columns: productLine, MSRP
- Filters: None
- Joins: None

## 40) Min buy price per vendor
- Intent: Min buy price grouped by vendor
- Tables: products
- Columns: productVendor, buyPrice
- Filters: None
- Joins: None

## 41) Total number of customers
- Intent: Count total customers
- Tables: customers
- Columns: customerNumber
- Filters: None
- Joins: None

## 42) Total number of products
- Intent: Count total products
- Tables: products
- Columns: productCode
- Filters: None
- Joins: None

## 43) Total revenue from payments
- Intent: Sum all payment amounts
- Tables: payments
- Columns: amount
- Filters: None
- Joins: None

## 44) Average product price
- Intent: Average product price
- Tables: products
- Columns: buyPrice
- Filters: None
- Joins: None

## 45) Max payment amount
- Intent: Max payment amount
- Tables: payments
- Columns: amount
- Filters: None
- Joins: None

## 46) Min payment amount
- Intent: Min payment amount
- Tables: payments
- Columns: amount
- Filters: None
- Joins: None

## 47) Count total orders
- Intent: Count total orders
- Tables: orders
- Columns: orderNumber
- Filters: None
- Joins: None

## 48) Total quantity in stock
- Intent: Sum quantity in stock
- Tables: products
- Columns: quantityInStock
- Filters: None
- Joins: None

## 49) Average MSRP
- Intent: Average MSRP
- Tables: products
- Columns: MSRP
- Filters: None
- Joins: None

## 50) Number of employees
- Intent: Count total employees
- Tables: employees
- Columns: employeeNumber
- Filters: None
- Joins: None
