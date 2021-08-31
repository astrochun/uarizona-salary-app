TITLE = 'University of Arizona Salary Data'  # Full title of app

CURRENCY_NORM = True  # Normalize to $1,000

# Commonly used DataFrame column names
SALARY_COLUMN = 'Annual Salary at Full FTE'
EMPLOYMENT_COLUMN = 'Annual Salary at Employment FTE'

STR_N_EMPLOYEES = 'Number of Employees'
COLLEGE_NAME = 'College Name'

# Choose between annual/hourly conversion
PAY_CONVERSION = ['Annual', 'Hourly']

# List of fiscal years
FY_LIST = [
    'FY2019-20', 'FY2018-19', 'FY2017-18',
    'FY2016-17 (NEW)', 'FY2014-15 (NEW)',
    'FY2013-14 (NEW)', 'FY2011-12 (NEW)',
]

# Number of fiscal hours per fiscal year
FISCAL_HOURS = {
    'FY2019-20': 2096,
    'FY2018-19': 2080,
    'FY2017-18': 2080,
    'FY2016-17': 2088,
    'FY2015-16': 2096,
    'FY2014-15': 2088,
    'FY2013-14': 2088,
    'FY2011-12': 2088,
}

DATA_VIEWS = [
    'About', 'Individual Search (NEW)', 'Trends', 'Salary Summary',
    'Highest Earners', 'College/Division Data', 'Department Data',
    'Wage Growth (NEW)',
]

# This is for the Trends page
TRENDS_LIST = ['General', 'Income Bracket']

# This is for Individual Search page
INDIVIDUAL_COLUMNS = [
    SALARY_COLUMN, '%', 'FTE', 'Annual Salary at Employment FTE',
    'Primary Title', 'Department', COLLEGE_NAME, 'State Fund Ratio',
]
