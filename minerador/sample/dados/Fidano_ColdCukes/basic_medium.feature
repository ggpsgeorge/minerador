Feature: Validating a Date Range (250 ms)
In order to ensure good data in the system two dates for a date range must be validated (249 ms)
Scenario: User enters two valid dates of consecutive days (2 ms)
Given there are two fields available for dates (2 ms)
When I enter a valid date for the first date, and I enter a valid date for the second date, and the second date is the day after the first (1 ms)
Then it should be a valid date range. (0 ms)
Scenario: User enters two valid dates of exactly one year apart (5 ms)
Given there are two fields available for dates (5 ms)
When I enter a valid date for the first date, and I enter a valid date for the second date, and the second date is exactly one year after the first (2 ms)
Then it should be a valid date range. (1 ms)
Scenario: User enters two valid dates but the second date is before the first (4 ms)
Given there are two fields available for dates (3 ms)
When I enter a valid date for the first date, and I enter a valid date for the second date, but the second date is the day before the first (3 ms)
Then it should NOT be a valid date range. (2 ms)
Scenario: User enters two valid dates but the second date is the same as the first (26 ms)
Given there are two fields available for dates (26 ms)
When I enter a valid date for the first date, and I enter a valid date for the second date, but the second date is the same as the first (25 ms)
Then it should be a valid date range. (25 ms)
Scenario: User enters two valid dates in mm/dd/yyyy format (2 ms)
Given there are two fields available for dates (2 ms)
When I enter a valid date for the first date, and I enter a valid date for the second date, and both dates are in mm/dd/yyyy format and the second date is one month after the first (2 ms)
Then it should be a valid date range. (1 ms)
Scenario: User enters two valid dates but the second date is in the wrong format (210 ms)
Given there are two fields available for dates (210 ms)
When I enter a valid date for the first date, and I enter a valid date for the second date, but the second date is not in the specified format (209 ms)
Then it should NOT be a valid date range. (2 ms)