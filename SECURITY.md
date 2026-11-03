# Security

## Reporting

Report a vulnerability privately through GitHub: **Security → Report a vulnerability** on
this repository. Do not open a public issue for it. We answer within a few working days.

Report, for example:

- a real credential, token, card number or personal data that slipped into the repository;
- a way for `sign.py` or `validate.py` to print or leak a secret, or to run code from a
  payload;
- a note, example or checklist item that would lead an integration to accept unsigned or
  forged callbacks.

A wrong contract fact that is not a security problem is a normal issue; use the "Wrong
contract fact" template.

## What the tools do

- They read secrets only from environment variables and print them as `<SECRET>`.
- They make no network requests and write no files.
- They use only the Python standard library.

## Using the skills safely

- Give agents sandbox keys, not production keys. Never paste a production secret into a
  chat.
- Keep vendor test cards and codes in tests and fixtures only.
- Verify every provider callback signature over the raw body with a constant-time compare.
