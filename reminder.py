import socket
import sys
from thread import *
import time
from pync import Notifier
import operator


class Event:
    time = 0
    message = ''

    def __init__(self, t, m):
        self.time = t + time.time()
        self.message = m


# the events queue
events = []


# function to actually deliver notification to osx
def check_and_notify():
    while True:
        time.sleep(30)
        if len(events) == 0:
            continue

        if time.time() < events[0].time:
            continue

        next_event = events.pop(0)
        Notifier.notify(next_event.message, title='Marley')


def convert_to_seconds(unit):
    unit = unit.lower()

    if unit in ('days', 'day', 'd'):
        return 24 * 60 * 60
    elif unit in ('hours', 'hour', 'h'):
        return 60 * 60
    elif unit in ('minutes', 'minute', 'mins', 'min', 'm'):
        return 60
    elif unit in ('seconds', 'second', 'sec', 's'):
        return 1
    else:
        raise Exception('wtf you are passing in')


#Function for handling connections. This will be used to create threads
def accept_event(conn):
    # Receiving from client
    data = conn.recv(1024)
    tokens = data.strip().split()
    operation = tokens.pop(0)

    # add an event in queue
    if operation == 'remind':
        time_in_future = 0  # in seconds
        message = ''
        while tokens:
            token = tokens.pop(0)
            if token == 'todo':
                message = ' '.join(tokens)
                break
            elif token.isdigit():
                unit = tokens.pop(0)
                time_in_future += int(token) * convert_to_seconds(unit)
        # print('created an event %s in %s seconds' % (message, str(time_in_future)))
        events.append(Event(time_in_future, message))
        events.sort(key=operator.attrgetter('time'))
    # print out all queued reminders
    elif operation == 'list':
        for event in events:
            conn.send(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(event.time)) + ' ToDo: ' + event.message + '\n')
    else:
        # let the client know we don't support this operation yet
        conn.send('sorry, we don\'t support this operation %s yet' % operation)
    #came out of loop
    conn.close()


HOST = ''    # Symbolic name meaning all available interfaces
PORT = 60102  # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

#Start listening on socket
s.listen(10)

start_new_thread(check_and_notify, ())
#now keep talking with the client
while True:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(accept_event, (conn, ))

s.close()
