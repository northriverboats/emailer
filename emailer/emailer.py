#!/usr/bin/python3

from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os
import re
import smtplib


class Email:
    """
    This class handles the creation and sending of email messages
    via SMTP.  This class also handles attachments and can send
    HTML messages.  The code comes from various places around
    the net and from my own brain.
    """
    def __init__(self, smtpServer):
        """
        Create a new empty email message object.

        @param smtpServer: The address of the SMTP server
        @type smtpServer: String
        """
        self._textBody = None
        self._htmlBody = None
        self._bcc = []
        self._cc = []
        self._port = 25
        self._subject = ""
        self._smtpServer = smtpServer
        self._tls = False
        self._reEmail = re.compile(
            "^([\\w \\._]+\\<[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\"
            ".[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:"
            "[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\"
            ".)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\"
            ">|[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\"
            ".[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:"
            "[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\"
            ".)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)$")
        self.clearRecipients()
        self.clearAttachments()

    def send(self):
        """
        Send the email message represented by this object.
        """
        # Validate message
        if self._textBody is None and self._htmlBody is None:
            raise Exception(
                "Error! Must specify at least one body type (HTML or Text)")
        if len(self._to) == 0:
            raise Exception("Must specify at least one recipient")

        # Create the message part
        if self._textBody is not None and self._htmlBody is None:
            msg = MIMEText(self._textBody, "plain")
        elif self._textBody is None and self._htmlBody is not None:
            msg = MIMEText(self._htmlBody, "html")
        else:
            msg = MIMEMultipart("alternative")
            msg.attach(MIMEText(self._textBody, "plain"))
            msg.attach(MIMEText(self._htmlBody, "html"))
        # Add attachments, if any
        if len(self._attach) != 0:
            tmpmsg = msg
            msg = MIMEMultipart()
            msg.attach(tmpmsg)
        for fname, attachname in self._attach:
            if not os.path.exists(fname):
                print("File '%s' does not exist.  Not attaching to email."
                      % fname)
                continue
            if not os.path.isfile(fname):
                print("Attachment '%s' is not a file.  Not attaching to email."
                      % fname)
                continue
            # Guess at encoding type
            ctype, encoding = mimetypes.guess_type(fname)
            if ctype is None or encoding is not None:
                # No guess could be made so use a binary type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                fp = open(fname)
                attach = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'image':
                fp = open(fname, 'rb')
                attach = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(fname, 'rb')
                attach = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(fname, 'rb')
                attach = MIMEBase(maintype, subtype)
                attach.set_payload(fp.read())
                fp.close()
                # Encode the payload using Base64
                encoders.encode_base64(attach)
            # Set the filename parameter
            if attachname is None:
                filename = os.path.basename(fname)
            else:
                filename = attachname
            attach.add_header('Content-Disposition',
                              'attachment',
                              filename=filename)
            msg.attach(attach)
        # Some header stuff
        msg['Subject'] = self._subject
        msg['From'] = self._from
        msg['To'] = ", ".join(self._to)
        msg['Cc'] = ", ".join(self._cc)
        msg.preamble = (
            "You need a MIME enabled mail reader to see this message")
        # Send message
        msg = msg.as_string()
        server = smtplib.SMTP(self._smtpServer, port=self._port)
        # server.set_debuglevel(True)

        if self._tls:
            server.ehlo()
            server.starttls()
            server.login(self._login, self._password)

        server.sendmail(self._from, self._to + self._cc + self._bcc, msg)
        server.quit()


    def setPort(self, port):
        """
        Set the SMTP port
        """
        self._port = port

    def setTLS(self, tls):
        """
        Set if TLS is used
        """
        self._tls = tls

    def setLogin(self, login):
        """
        Set user login name
        """
        self._login = login

    def setPassword(self, password):
        """
        Set login password
        """
        self._password = password

    def setSubject(self, subject):
        """
        Set the subject of the email message.
        """
        self._subject = subject

    def setFrom(self, address):
        """
        Set the email sender.
        """
        if not self.validateEmailAddress(address):
            raise Exception("Invalid email address '%s'" % address)
        self._from = address

    def clearRecipients(self):
        """
        Remove all currently defined recipients for
        the email message.
        """
        self._to = []
        self._cc = []
        self._bcc = []

    def addRecipient(self, address):
        """
        Add a new recipient to the email message.
        """
        if not self.validateEmailAddress(address):
            raise Exception("Invalid email address '%s'" % address)
        self._to.append(address)

    def addCC(self, address):
        """
        Add a new carbon copy recipient to the email message.
        """
        if not self.validateEmailAddress(address):
            raise Exception("Invalid cc email address '%s'" % address)
        self._cc.append(address)

    def addBCC(self, address):
        """
        Add a new blind carbon copy recipient to the email message.
        """
        if not self.validateEmailAddress(address):
            raise Exception("Invalid bcc email address '%s'" % address)
        self._bcc.append(address)

    def setTextBody(self, body):
        """
        Set the plain text body of the email message.
        """
        self._textBody = body

    def setHtmlBody(self, body):
        """
        Set the HTML portion of the email message.
        """
        self._htmlBody = body

    def clearAttachments(self):
        """
        Remove all file attachments.
        """
        self._attach = []

    def addAttachment(self, fname, attachname=None):
        """
        Add a file attachment to this email message.

        @param fname: The full path and file name of the file
                      to attach.
        @type fname: String
        @param attachname: This will be the name of the file in
                           the email message if set.  If not set
                           then the filename will be taken from
                           the fname parameter above.
        @type attachname: String
        """
        if fname is None:
            return
        self._attach.append((fname, attachname))

    def validateEmailAddress(self, address):
        """
        Validate the specified email address.

        @return: True if valid, False otherwise
        @rtype: Boolean
        """
        if self._reEmail.search(address) is None:
            return False
        return True


def mail_results(subject, html, text="", recipient="", attachment=""):
    """
    send email relying on env vars for server info

    @parm subject    the subject of the email
    @parm html       html formatted message (required)
    @parm text       text formatted message (optional)

    @return None
    """
    text = text or "You should not see this text in a MIME aware reader"

    mail = Email(os.getenv('MAIL_SERVER'))
    mail.setPort(os.getenv('MAIL_PORT'))
    mail.setTLS(os.getenv('MAIL_TLS'))
    mail.setLogin(os.getenv('MAIL_LOGIN'))
    mail.setPassword(os.getenv('MAIL_PASSWORD'))

    mail.setFrom(os.getenv('MAIL_FROM'))

    emails = recipient or os.getenv('MAIL_TO') or ""
    emails = [email for email in emails.split(',') if email]
    for email in emails:
        mail.addRecipient(email)

    ccs = [cc for cc in (os.getenv('MAIL_CC') or "").split(',') if cc] or []
    for cc in ccs:
        mail.addCC(os.getenv('MAIL_FROM'))

    mail.setSubject(subject)
    mail.setTextBody(text)
    mail.setHtmlBody(html)
    if (attachment):
        mail.addAttachment(attachment)
    mail.send()

if __name__ == "__main__":
    print("Tests go here...")

    # Run some tests
    mFrom = 'user1@example.com'
    mTo = "user2@example.com"
    m = Email('mail.example.com')
    m.setFrom(mFrom)
    m.addRecipient(mTo)
    m.addCC("user3@example.com")

    m.setSubject("Text and HTML Message with CC and BCC")
    m.setTextBody("You should not see this text in a MIME aware reader")
    m.setHtmlBody("The following should be <b>bold</b>. "
                  "If this works Will, you will be BCC'd on this.")
    m.addAttachment('/tmp/shot.png')
    m.send()
