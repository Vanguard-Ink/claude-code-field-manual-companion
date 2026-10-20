# LAB-05 questions

Ask each in the same session, in order. Run A: ask directly. Run B: prefix with
`@agent-code-locator`. Record context % after each answer.

1. Where is the decision made that a viewer may export a report? I need the
   function that returns allow/deny and any feature flag it checks.
2. Which exceptions make a charge retry, and where is that list defined?
3. Where is the hour of the nightly invoice run set, and where is it used?
4. Where is the minimum late fee enforced?
5. What happens when someone requests a report id that doesn't exist? Trace it
   from the web handler down.
6. (Follow-up, unrelated) Write a one-line docstring for
   `ledgerline_shared.money.from_cents`. Record the cost of this turn alone.
