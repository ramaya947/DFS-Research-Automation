import eventlet, socketio, test
from waiting import wait
import time
import sys

sio = socketio.Server(async_mode='eventlet', cors_allowed_origins='*', logger=False, ping_timeout=600000)
app = socketio.WSGIApp(sio)
response = None
testIns = test.Test()

@sio.event
def connect(sid, environ):
    print('Connected')

@sio.event
def disconnect(sid):
    print('Disconnected')
    sys.exit()

@sio.on('Message to Server')
def receiveMessage(sid, data):
    print("\nReceived Message:", data)

@sio.on("Answer to Question")
def receiveAnswer(sid, data):
    global response, testIns

    response = data
    print("Received response: {}".format(response))
    testIns.setResponse(data)

@sio.on('Run Program')
def run(sid):
    print("Preparing to run the service")
    global testIns
    testIns.setSio(sio)

    testIns.run()
    #TEST
    #global response

    #print("A")
    #sio.emit('Message to Client', { "message": "How much wood would a wood chuck chuck?", "isQuestion": "true"})
    #while (response == None):
    #    eventlet.sleep(1)
    #response = None
    #print("B")

def waitingFunc():
    global response

    while response == None:
        continue

if __name__ == '__main__':
    print('Starting server...')
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)