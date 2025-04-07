################################################################################
# Port Scanner
# Created by Aiden Seay, Spring 2025

################################################################################
# IMPORTS

import optparse
from socket import *
import threading

################################################################################
# MAIN FUNCTION

def main():
    
    # get args from the user
    parser = optparse.OptionParser("%prog -H <target host> -p <target port>")
    parser.add_option('-H', dest='tgtHost', type='string', 
                      help='specify target host')
    parser.add_option('-p', dest='tgtPort', type='string', 
                      help='specify target port[s] separated by comma')
    options, args = parser.parse_args()

    # identify a target host and port(s)
    tgtHost = options.tgtHost
    tgtPorts = str(options.tgtPort).split(',')

    # check if there are any args and exit if not
    if (tgtHost == None) | (tgtPorts[0] == None):
        print('[-] You must specify a target host and port[s].')
        exit(0)

    # execute port scan program
    portScan(tgtHost, tgtPorts)

################################################################################
# SUPPORTING FUNCTIONS

def connScan(tgtHost, tgtPort):

    try:
        # create a socket
        tcp_socket = socket(AF_INET, SOCK_STREAM)

        # connect to the target host and port
        tcp_socket.connect((tgtHost, tgtPort))
        print('[+] %d/tcp open'% tgtPort) 

        # send garbage data
        tcp_socket.send(b"Garbage Data\r\n")

        # TODO get results from sending garbage string
        results = tcp_socket.recv(1024)
        print('[+] ' + str(results))

        # close the socket
        tcp_socket.close()

    except:
        print('[-] %d/tcp closed'% tgtPort)

def portScan(tgtHost, tgtPorts):

    # try to get host by name
    try:
        tgtIP = gethostbyname(tgtHost)
    except:
        print("[-] Cannot resolve '%s': Unknown host" %tgtHost)
        return
    
    # try to get host by address
    try:
        tgtName = gethostbyaddr(tgtIP)
        print('\n[+] Scan Results for: ' + tgtName[0])
    except:
        print('\n[+] Scan Results for: ' + tgtIP)

    # set default timeout for 1 sec
    setdefaulttimeout(1)

    # iterate through all of the target ports
    thread_list = []
    for tgtPort in tgtPorts:

        # convert the target port into an integer
        tgtPort = int(tgtPort)
        print('Scanning port ' + str(tgtPort))

        # create a thread to run connScan on the target for efficiency
        thread = threading.Thread(target=connScan, args=(tgtHost, tgtPort))
        thread.start()
        thread_list.append(thread)

    # wait for all threads to join back
    for t in thread_list:
        t.join()

################################################################################
if __name__ == '__main__':
    main()

################################################################################
