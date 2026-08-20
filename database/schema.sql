CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE groups (
    group_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    group_name VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE group_memberships (
    membership_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,
    group_id UUID NOT NULL,

    username VARCHAR NOT NULL,

    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (group_id) REFERENCES groups(group_id),

    UNIQUE (user_id, group_id),
    UNIQUE (group_id, username)
);

CREATE TABLE expenses (
    expense_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    group_id UUID NOT NULL,
    created_by UUID NOT NULL,
    paid_by UUID NOT NULL,

    description VARCHAR NOT NULL,
    total_amount BIGINT NOT NULL,

    split_method VARCHAR NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (group_id) REFERENCES groups(group_id),

    FOREIGN KEY (created_by) REFERENCES users(user_id),

    FOREIGN KEY (paid_by) REFERENCES users(user_id),

    CHECK (total_amount > 0),

    CHECK (split_method IN ('EQUAL', 'UNEQUAL'))
);

CREATE TABLE expense_participants (
    expense_id UUID NOT NULL,
    user_id UUID NOT NULL,
    share BIGINT NOT NULL,

    PRIMARY KEY (expense_id, user_id),

    FOREIGN KEY (expense_id) REFERENCES expenses(expense_id),

    FOREIGN KEY (user_id) REFERENCES users(user_id),

    CHECK (share > 0)
);

CREATE TABLE settlements (
    settlement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    group_id UUID NOT NULL,
    payer_id UUID NOT NULL,
    receiver_id UUID NOT NULL,

    amount BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (group_id) REFERENCES groups(group_id),

    FOREIGN KEY (payer_id) REFERENCES users(user_id),

    FOREIGN KEY (receiver_id) REFERENCES users(user_id),

    CHECK (amount > 0),

    CHECK (payer_id <> receiver_id)
);

CREATE TABLE invitations (
    invitation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    group_id UUID NOT NULL,
    inviter_id UUID NOT NULL,

    recipient_email VARCHAR NOT NULL,

    expiration_date TIMESTAMPTZ NOT NULL,

    status VARCHAR NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (group_id) REFERENCES groups(group_id),

    FOREIGN KEY (inviter_id) REFERENCES users(user_id),

    CHECK (status IN ('PENDING', 'ACCEPTED'))
);

CREATE TABLE otp_verifications (
    otp_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    email_id VARCHAR NOT NULL,
    otp_hash VARCHAR NOT NULL,

    expires_at TIMESTAMPTZ NOT NULL,

    failed_attempts INTEGER NOT NULL DEFAULT 0,
    blocked_until TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMPTZ
);

CREATE INDEX idx_group_memberships_group_id
ON group_memberships(group_id);

CREATE INDEX idx_expenses_group_id
ON expenses(group_id);

CREATE INDEX idx_settlements_group_id
ON settlements(group_id);

CREATE INDEX idx_invitations_recipient_email
ON invitations(recipient_email);

CREATE INDEX idx_otp_verifications_email_id
ON otp_verifications(email_id);