# Database Design

## Entities

### 1. User

Represents a registered user.

* User ID
* Email

### 2. Group

Represents an expense-sharing group.

* Group ID
* Group name

### 3. Group Membership

Represents a user's membership in a group.

* User
* Group
* Group specific username

A user can have different usernames in different groups.

### 4. Expense

Represents an expense added to a group.

* Expense ID
* Group
* Created by
* Payer
* Description
* Total amount
* Split method

### 5. Expense Participant

Represents a user's participation and share in an expense.

* Expense
* User
* Share

### 6. Settlement

Represents a payment from one group member to another.

* Settlement ID
* Group
* Payer
* Receiver
* Amount

### 7. Invitation

Represents an invitation to join a group.

* Invitation ID
* Group
* Inviter
* Recipient email
* Expiration date
* Status

### 8. OTP Verification

Represents a temporary OTP issued to authenticate a user's email address.

* OTP Verification ID
* Email
* OTP hash
* Expiration time
* Number of failed verification attempts
* Blocked until
* Creation time
* Verification time

### 9. Session
Represents a logged in user's active state.

* session id
* user
* expires at
* created at
* revoked at

---
## Relationships

### User ↔ Group
* A user can belong to many groups.
* A group can have many users.
* This relationship is represented through Group Membership.

### Group → Expense
* A group can have many expenses.
* Each expense belongs to exactly one group.

### User → Expense (Creator)
* A user can create many expenses.
* Each expense has exactly one creator.

### User → Expense (Payer)
* A user can pay for many expenses.
* Each expense has exactly one payer.

### Expense → Expense Participant
* An expense can have many participants.
* Each Expense Participant belongs to exactly one expense.

### User → Expense Participant
* A user can participate in many expenses.
* Each Expense Participant belongs to exactly one user.

### Group → Settlement
* A group can have many settlements.
* Each settlement belongs to exactly one group.

### User → Settlement
* A user can be the payer in many settlements.
* A user can be the receiver in many settlements.
* Each settlement has exactly one payer and one receiver.

### Group → Invitation
* A group can have many invitations.
* Each invitation belongs to exactly one group.

### User → Invitation
* A user can send many invitations.
* Each invitation has exactly one inviter.

### Email → OTP Verification
* An email address can have multiple OTP verification records over time.
* Each OTP verification record belongs to exactly one email address.
* OTP verification is performed against the email address used when the OTP was requested.

### User → Session
* A user can have multiple active session (like on multiple devices)
---

## Attributes
### User
* PK user_id
* email_id

### Group
* PK group_id
* group_name

### Group Membership
* PK membership_id
* FK user_id
* FK group_id
* username

### Expense
* PK expense_id
* FK group_id
* FK created_by
* FK paid_by
* description
* total_amount
* split_method

### Expense Participant
* PK (expense_id, user_id)
* FK expense_id
* FK user_id
* share

### Settlement
* PK settlement_id
* FK group_id
* FK payer_id(user)
* FK receiver_id(user)
* amount

### Invitation
* PK invitation_id
* FK group_id
* FK inviter_id
* recipient_email
* expiration_date
* status → Pending / Accepted

### OTP Verification
* PK otp_id
* email_id
* otp_hash
* expires_at
* failed_attempts
* blocked_until
* created_at
* verified_at

### Session
* PK session_id
* FK 
* expires_at
* created_at
* revoked_at
---
## Data Types

### Monetary Values

All monetary values are stored as integer values representing paise in the database.

Examples:
* ₹100.00 → 10000 paise
* ₹100.50 → 10050 paise
* ₹33.33 → 3333 paise

### User
* `user_id` → UUID
* `email_id` → VARCHAR
* `created_at` → TIMESTAMPTZ

### Group
* `group_id` → UUID
* `group_name` → VARCHAR
* `created_at` → TIMESTAMPTZ

### Group Membership
* `membership_id` → UUID
* `user_id` → UUID
* `group_id` → UUID
* `username` → VARCHAR

### Expense
* `expense_id` → UUID
* `group_id` → UUID
* `created_by` → UUID
* `paid_by` → UUID
* `description` → VARCHAR
* `total_amount` → BIGINT
* `split_method` → VARCHAR
* `created_at` → TIMESTAMPTZ
* `updated_at` → TIMESTAMPTZ

### Expense Participant
* `expense_id` → UUID
* `user_id` → UUID
* `share` → BIGINT

### Settlement
* `settlement_id` → UUID
* `group_id` → UUID
* `payer_id` → UUID
* `receiver_id` → UUID
* `amount` → BIGINT
* `created_at` → TIMESTAMPTZ

### Invitation
* `invitation_id` → UUID
* `group_id` → UUID
* `inviter_id` → UUID
* `recipient_email` → VARCHAR
* `expiration_date` → TIMESTAMPTZ
* `status` → VARCHAR
* `created_at` → TIMESTAMPTZ

### OTP Verification
* `otp_id` → UUID
* `email_id` → VARCHAR
* `otp_hash` → VARCHAR
* `expires_at` → TIMESTAMPTZ
* `failed_attempts` → INTEGER
* `blocked_until` → TIMESTAMPTZ
* `created_at` → TIMESTAMPTZ
* `verified_at` → TIMESTAMPTZ

### Session
* `session_id` → UUID
* `user_id` → UUID
* `expires_at` → TIMESTAMPTZ
* `created_at` → TIMESTAMPTZ
* `revoked_at` → TIMESTAMPTZ

---
## Constraints

### User

* `user_id` is the primary key.
* `email_id` must be unique.
* `email_id` cannot be null.

### Group

* `group_id` is the primary key.
* `group_name` cannot be null.

### Group Membership

* `membership_id` is the primary key.
* `user_id` and `group_id` are foreign keys.
* `user_id`, `group_id`, and `username` cannot be null.
* `(user_id, group_id)` must be unique.
* `(group_id, username)` must be unique.

### Expense

* `expense_id` is the primary key.
* `group_id`, `created_by`, and `paid_by` are foreign keys.
* `group_id`, `created_by`, and `paid_by` cannot be null.
* `description` cannot be null.
* `total_amount` must be greater than 0.
* `split_method` must be either `EQUAL` or `UNEQUAL`.

### Expense Participant

* `(expense_id, user_id)` is the primary key.
* `expense_id` and `user_id` are foreign keys.
* `share` must be greater than 0.
* The sum of all participant shares must equal the expense total.
* Every participant must be a member of the expense's group.

### Settlement

* `settlement_id` is the primary key.
* `group_id`, `payer_id`, and `receiver_id` are foreign keys.
* `amount` must be greater than 0.
* `payer_id` and `receiver_id` must be different.

### Invitation

* `invitation_id` is the primary key.
* `group_id` and `inviter_id` are foreign keys.
* `recipient_email` cannot be null.
* `expiration_date` cannot be null.
* `status` must be either `PENDING` or `ACCEPTED`.

### OTP Verification

* `otp_id` is the primary key.
* `email_id` cannot be null.
* `otp_hash` cannot be null.
* `expires_at` cannot be null.
* `failed_attempts` cannot be null.
* `failed_attempts` must be greater than or equal to 0.
* `created_at` cannot be null.
* `verified_at` is null until the OTP is successfully verified.

### Session

* `session_id` is the primary key.
* `user_id` cannot be null.
* `expires_at` cannot be null.
* `created_at` cannot be null.
* `revoked_at` is null while the session is active
---
## Indexes

### Group Membership
* The unique constraint on `(user_id, group_id)` provides an index for efficiently finding a user's memberships.
* Index on `group_id` to efficiently find members of a group.

### Expense
* Index on `group_id` to efficiently find expenses belonging to a group.

### Settlement
* Index on `group_id` to efficiently find settlements belonging to a group.

### Invitation
* Index on `recipient_email` to efficiently find invitations for an email address.

### OTP Verification
* Index on `email_id` to efficiently find OTP verification records for an email address.