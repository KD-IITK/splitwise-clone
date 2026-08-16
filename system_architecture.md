# System Architecture

## 1. Frontend

* Responsible for displaying the user interface
* Responsible for collecting user input
* Sends requests to the backend
* Receives responses from the backend and updates the UI
* Performs basic client-side validation

## 2. Backend

* Handles user registration and authentication using email and OTP
* Handles group creation and management.
* Handles group invitations.
* Handles adding, editing and deleting expenses.
* Implements equal and unequal expense splitting.
* Calculates user balances.
* Handles settlements.
* Generates CSV exports.
* Handles notifications.
* Performs server-side validation and authorization.

## 3. Database

The database stores persistent application data, including:

* Users
* Groups
* Group memberships
* Group-specific usernames
* Expenses
* Expense participants and their shares
* Settlements
* Invitations

Calculated balances may be derived from expenses and settlements.

## 4. External Services

* Email service for sending OTP and group invitation emails.
* Notification service, if required for the chosen notification mechanism.

## 5. Communication

* Frontend communicates with the backend through HTTP/HTTPS APIs.
* Backend communicates with the database.
* Backend communicates with external services such as the email service.