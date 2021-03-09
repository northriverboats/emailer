# emailer
Email Factory Helper

This is able to burst email address, when `MAIL_TO` looks like `Bob Jones <bob@example.com>,John Q. Public <john@example.com>`

```
import os
from emailer.email import Email

mail_results(subject, body):
    mFrom = os.getenv('MAIL_FROM')
    mTo = os.getenv('MAIL_TO')
    m = Email(os.getenv('MAIL_SERVER'))
    m.setFrom(mFrom)
    for email in mTo.split(','):
      m.addRecipient(email)
    # m.addCC(os.getenv('MAIL_FROM'))

    m.setSubject(subject)
    m.setTextBody("You should not see this text in a MIME aware reader")
    m.setHtmlBody(body)
    m.send()
```
