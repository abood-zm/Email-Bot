import smtplib
import imapclient
import email.message
import pyzmail as pm
import time
from config import *
import sys

def imap_init():
    """
    Initializing IMAP Connection
    """
    print("Connecting to IMAP...", end="")
    global mail
    mail = imapclient.IMAPClient(imap_server)
    client = mail.login(radr, pwd)
    mail.select_folder("INBOX", readonly=True)
    print("IMAP Connection Successful")

def smtp_init():
    """
    Initializing SMTP Connection
    """
    global sender
    sender = smtplib.SMTP(smtp_server, smtp_port)

    # Returning the status code
    status = sender.starttls()[0]

    if status != 220:
        raise Exception(f"Starting TLS has Failed: {status}")
    
    status = sender.login(radr, pwd)[0]
    if status != 235:
        raise Exception(f"Starting Login has Failed: {status}")
    print("SMTP Connection Successful.")


def get_unread():
    """
    Fetching Unread Messages.
    """

    # Search for unseen messages
    uids = mail.search(["UNSEEN"])
    if not uids:
        return None
    else:
        print("Found %s Unseen Messages" % len(uids))
        return mail.fetch(uids, ['BODY[]', 'FLAGS'])

def analyze_message(raws, id):
    """
    Analyze the message, and determine if the sender and command match.
    """
    print(f"Analyzing message with {id} ID")

    # Fetch the raw email with UID
    msg = pm.PyzMessage.factory(raws[id][b'BODY[]'])
    # global sender
    sender = msg.get_addresses('from')
    
    if sender[0][1] != sadr:
        print("Unread message from %s <%s>. Message will be skipped." % (sender[0][0], sender[0][1]))

        return None
    global subject
    subject = msg.get_subject()
    if not subject.startswith("Re"):
        subject = "Re: " + msg.get_subject()
    print("Subject is ", subject)
    if msg.text_part is None:
        print("No text part. Cannot Parse.")
        return None
    text = msg.text_part.get_payload().decode(msg.text_part.charset)
    cmds = text.replace('\r', '').split('\n')
    cmds[0] = cmds[0].lower()
    if cmds[0] not in commands:
        print("Command {} is not in commands".format(cmds[0]))
        return False
    else:
        return cmds
    
def send_email(text):
    """
    Print an email to console, then send it
    """
    print("This email will be sent: ")
    print(text)
    
    # Create an instance of EmailMessage
    msg = email.message.EmailMessage()
    global subject
    msg["From"] = radr
    msg["To"] = sadr
    msg["Subject"] = subject
    msg.set_content(text)
    result = sender.send_message(msg)
    print("The message has been sent. ", result)


imap_init()
smtp_init()

while True:
    try:
        print()
        msgs = get_unread()
        while msgs is None:
            time.sleep(check_freq)
            msgs = get_unread()

        for a in msgs.keys():
            if type(a) is not int:
                continue

            cmds = analyze_message(msgs, a)
            if cmds is None:
                continue
            elif cmds is False:  # Invalid Command
                prompt = "The command is invalid. The commands are: \n"
                for key in commands.keys():
                    prompt += str(key) + '\n'

                mail(prompt)
                continue
            else:
                print("Command Received: \n{}".format(cmds))
                r = commands[cmds[0]](cmds)
                send_email(str(r))
                print("Command Successfully Completed.")

    except KeyboardInterrupt:
        mail.logout()
        sender.quit()
        break

    except (OSError, smtplib.SMTPServerDisconnected):
        # Log the exception for debugging
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"Exception Type: {exc_type}")
        print(f"Exception Value: {exc_value}")
        print("Traceback:")
        traceback.print_tb(exc_traceback)

        # Add a delay before retrying to avoid continuous retries
        time.sleep(30)

        # Re-initialize the email client
        imap_init()
        smtp_init()

    except Exception as e:
        # Catch other exceptions for debugging
        print("Unexpected exception:", e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"Exception Type: {exc_type}")
        print(f"Exception Value: {exc_value}")
        print("Traceback:")
        traceback.print_tb(exc_traceback)

    finally:
        mail.logout()
        sender.quit()