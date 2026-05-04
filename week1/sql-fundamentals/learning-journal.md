# Learning Journal

## Classic Models SQL Practice

- The employee hierarchy uses `employees.reportsTo` as a self-reference to `employees.employeeNumber`.
- One source row uses the typoed job title `Sale Manager (EMEA)`, so manager filters should use `LIKE '%Sales Manager%' OR LIKE '%Sale Manager%'`.
- `customers.state` is nullable, so filters for customers who filled in state must use `state IS NOT NULL`.
- For office-level payment and sales reports, the cleanest path is `offices -> employees -> customers -> payments/orders`.
- If ranking is needed, MySQL 8 window functions like `RANK()` and `SUM(...) OVER (...)` work well.

## Notes On Errors And Fixes

- No execution errors were captured in this workspace yet.
- If MySQL rejects the `WITH` or window-function queries, the server version is likely older than MySQL 8.
- If a report returns duplicate office rows, the grouping level should be checked against the selected columns.