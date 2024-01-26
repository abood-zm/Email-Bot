import getpass

# Addresses to check and send from
radr = input("Addresses to log in to: ")

# The IMAP Server Domain
imap_server = input("Enter your IMAP Server Domain: ")

# The SMTP Server Domain
smtp_server = input("Enter your SMTP Server Domain: ")

# The SMTP Port
smtp_port = int(input("Enter your SMTP Port: "))

# GetPass to get the password and hide it
pwd = getpass.getpass("Account Password: ")

# Addresses to receive commands from. Set trusted email that is the only one commands will be accepted from.
sadr = input("Trusted Addresses to Receive From: ")

check_freq = 5 

# Defining commands here
def hello_world(lines):
    return "Hello"


commands = {"hello": hello_world}