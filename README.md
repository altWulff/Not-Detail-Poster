# Not-Detail-Poster MVP
## Dependencies
`Python 3.X`, `PosgreSQL`

## Installation
`$ git clone git@github.com:altWulff/Not-Detail-Poster.git && cd Not-Detail-Poster`

`$ virtualenv venv`

`$ source venv/bin/activate`

`$ pip install -r requirements.txt`

`$ ./init_env.sh`

`$ flask run`

Base user and password `admin`

Local address `http://127.0.0.1:5000/`

Project demo https://not-detail-poster.herokuapp.com

# Description of the project
Simplified system of automation, analytics, and reports for a coffee shop.

## Features
- entry restriction
- daily reporting
- various transactions: expenditure of money, receipt of goods, movement of goods, and its write-off
- different user roles: administrator, moderator, user (employee/barista)
- site admin panel: administrator (create, edit, delete), for moderator only edit
- basic translation, depending on browser settings

## Login and Logout
`Name` and `Password`, a user without a name and password cannot enter the site.
After logging in, the user is redirected to the main page with the display of cards for coffee outlets.
To exit click on `Exit` in the popup menu.

## Display coffee shops
Are displayed in the list.
The card displays the name, address, amount of cash and cashless.
Displays employees working in a coffee shop. Clicking on the name redirects to the employee's profile description.
In unfolding fields
- description of equipment at the point
- stock balances
- current transactions of the coffee shop

## Reports
By clicking on the `Reports` link, the user is redirected to the list of daily reports with pagination.
Different selection depending on the role of the user, for the barista the last three, for the moderator, and the admin all reports.

The report displays the name of the coffee shop, who sent the report, the date in the dd.mm.YYYY format
The report is divided into three columns
- in the first: cash desk, expense for the day, balance of the day, cashless, cash balance, actual balance of the day (cash)
- in the second: global expenses per day, receipts from suppliers, movement of goods
- in the third: consumption of goods for the day, and their balance at the end of the shift


## Transactions
When creating a transaction, the user can select a coffee shop from the list on which he works, there are no restrictions for the administrator.
All transactions are realized through a modal window. About successful validation, flash message signals.

#### Expenses
There is a global expense checkbox, payment option, expense category(s), and its amount

#### Supply
Upon receipt, the choice of the incoming goods, quantity, payment option, amount.

### Selling by weight and writing off goods
Sale and write-off are implemented in the same way, write-off without the amount of the expense.

### Closing the shift
At the end of the shift, the barista creates a report by clicking on `Create report`, redirected to the form,
if the barista has not taken a salary, an information message will inform you about it.
The form contains information about the received
- Cashless per day (Z-report)
- Actual balance
- the rest of Arabica, blend, milk, panini, buns, and sausages.
- there are check-boxes of the cleaning of the coffee machine and coffee grinders

### Popup Menu for Administrator
Can create a coffee shop through the menu,
and add employee

## Admin Panel
Login via pop-up menu by clicking `Administration` (available for admin and moderator), exit by clicking on `Exit` in the top bar.
Here we are met by an overview of the created coffee houses.
For the admin, all expenses and receipts are visible, the moderator can see information only from the coffee houses where he works / moderates.

#### Coffee shops
Drop-down list of coffee shops, equipment, warehouses and their creation, editing, deletion.

#### Statistics
List of reports, filters for selection, sorting by date and their creation, editing, deletion.

#### Movement of goods
Creation, editing, removal of records about - receipts, weight, write-offs, movement of goods.

#### Cash
Creating, editing, deleting records about - expenses, depositing funds, and collection.

#### Employees
List of employees, creation and editing of their data.

#### Miscellaneous
Creation and editing of categories, as well as a list of roles and distribution of access rights to users.
