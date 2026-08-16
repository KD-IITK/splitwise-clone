### Expense & Settlement Rules

1. An expense cannot be added if its total amount is <= ₹0.
2. In case of unequal splitting, each participant's share must be > ₹0.
3. In case of unequal splitting, the sum of all participant shares must equal the total expense amount.
4. An edited expense must satisfy all expense validation rules before the changes are saved.
5. A settlement amount must be > ₹0.
6. If A owes B ₹x and B pays A ₹y, then A owes B ₹x + y.
7. If A owes B ₹x and A pays B ₹y where y > x, then B owes A ₹y - x.
8. In the balance view, relationships with a balance of ₹0 are not displayed.
9. In case of an equal split, the total expense is divided equally among all selected participants.
10. Each participant's final share is stored with exactly 2 decimal places.
11. The sum of all participant shares must always equal the total expense amount.
12. If equal splitting produces a rounding remainder, the remainder is assigned to exactly one participant. If the payer is a participant, the remainder is assigned to the payer. Otherwise, it is assigned according to a predefined deterministic rule.

### Balance Rules

13. For an expense, each participant is responsible for their calculated share of the expense.
14. If the payer is also a participant, the payer's own share is deducted from the amount they paid. Each other participant owes the payer an amount equal to their share.
15. If the payer is not a participant, each participant owes the payer an amount equal to their share.
16. The same balance calculation rules apply to both equal and unequal splits.
17. The total amount owed to the payer as a result of an expense must equal to ->  total amount paid - payer's own share
18. Suppose B owes A 500 in expense 1 and A owes B 400 in expense two, then we only show that B owes A 100.
19. The system should initially display pairwise net balances without performing multi-person debt simplification. Multi-person debt simplification will be implemented as a later feature.

### Group Rules
20. There is no admin role in a group. All group members have equal group-level permissions.
21. Any group member can invite any other user to the group.
22. A group becomes inactive when its last member leaves.
23. A user can leave a group only when their net balance with all other group members is ₹0.
24. Group members can see the usernames of other group members. Member email addresses are not displayed to other group members.
25. Each group must have unique usernames among its members.
26. The same user can have different usernames in different groups.
27. Different users can have the same username in different groups.

### Invitation Rules
28. An invitation remains valid for 7 days from the time it is sent. After 7 days, the invitation expires and cannot be accepted
29. A group member can invite another user only by providing their email address.
30. If the invited email address does not have an account, the invitation requires the user to create an account using the invited email address before they can view and accept the invitation.
31. If the invited email address already has an account, the user must authenticate using that email address and OTP before viewing and accepting the invitation.
32. If the invited user is already a member of the group, the invitation cannot be accepted and the user is informed that they are already a member.
33. The invitation can only be accepted by the account associated with the invited email address.


### Authentication Rules
34. An OTP is valid for 1 minute and consists of 6 numeric digits
35. If an OTP expires, the user can request a new OTP.
36. A user can make a maximum of 5 incorrect OTP verification attempts. After 5 incorrect attempts, OTP verification is blocked for 5 minutes.
37. A user can request a new OTP only after the currently active OTP has expired.
38. When a new OTP is generated, the previous OTP becomes invalid and cannot be used.
39. A successfully verified OTP can only be used once and becomes invalid immediately after successful verification.
40. The system should limit the number of OTP requests that can be made within a defined time period to prevent abuse.
41. If a user attempts to access an invitation using an email address different from the invited email address, the system must not reveal any group information and must not allow the invitation to be accepted.
42. An expense can only include participants who are members of the group.
43. A user cannot invite their own email address to a group.