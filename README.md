# TipAssistant

## Purpose

Given a roster of employees and the number of hours they worked in a given timeframe, as well as the number of bills and coins given as tips in that timeframe, this program computes the tips each employee should get and what denominations the pay-outs should be given in. Also computed are the denomination exchanges needed to successfully accomplish the pay-outs.

## Assumptions

- This is for Canadian currency, so there are no pennies. There are loonies and toonies.
- Highest denomination considered is twenties. No fifties/hundreds.
- Denominations can be broken down arbitrarily into smaller bills or coins.
- Rolls of 40 quarters, 50 dimes, or 20 nickels, can be exchanged for two fives, one five, or loonies, respectively.
- Sometimes finer exchanges needed to be made, to avoid giving out lots of dimes and nickels. Therefore, non-rolled units of 4 quarters and 10 dimes can be exchanged for loonies.
- No limit is put on loonies paid out. Some people don't like them, but tough.

## Input

Two text files: *money.txt* and *roster.txt*.

*money.txt* should consist of only eight integers, separated by newlines. These integers represent the number of twenties, tens, fives, toonies, loonies, quarters, dimes, and nickels that have been given as tips.

*roster.txt* is more complicated. The first line should contain the period start date in yyyy/mm/dd format. The second line should contain the period end date in same format. The third, fifth, etc. lines should contain employee names. The fourth, sixth, etc. lines should contain hours each respective employee worked. It is assumed that hours are floats up to two decimal places. For example:

```
2020/1/1
2020/1/14
Bob
3.14
Sue
2.72
Billy-joe
111.1
```

## Output

The deliverable is a report that is printed to screen as well as saved as a file with the name 'REPORT_YYYYMMDD_YYYYMMDD_YYYYMMDD.txt', where the three dates are report, period start, and period end dates.

The report contains:
- The relevant dates
- The total hours worked for all employees
- Total value of tips
- For each employee:
	- The total amount they earn
	- The number of bills/coins of each denomination they should be given
- For each denomination, the number of bills/coins should be exchanged or obtained