async_mode = None

from flask import Flask, render_template
import socketio
import eventlet
import json

sio = socketio.Server(async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# skivi is a open key-value store.
# each key has a value and a sub list stored in different dicts

vals = {} # of the form key: value
subs = {} # of form key: [sid, sid, sid ...]

def write_state():
    val = json.dumps(vals, indent = 4)
    sub = json.dumps(subs, indent = 4)
 
    with open("values.json", "w") as outfile:
        outfile.write(val)

    with open("subs.json", "w") as outfile:
        outfile.write(sub)
    

def read_state():
    with open("values.json", "r") as infile:
        global vals
        vals = json.load(infile)

    with open("subs.json", "r") as infile:
        global subs
        subs = json.load(infile)

def remove_inactive_sids():
    for key in subs:
        for sid in list(subs[key]):
            if sid not in sio.sockets:
                subs[key].remove(sid)    

@app.route('/')
def index():
    return render_template('latency.html')

@sio.event
def sub_to_rooms(sid, data):
    for room in data:
        subs[room].append(room)
        write_state()

@sio.event
def put_data(sid, data):
    # store key:val in vals
    # store key:sid in subs
    for key, value in data.items():
        vals[key] = value
        subs[key].append(sid)
        write_state()

@sio.event
def del_data(sid, data):
    # delete key:val from vals
    # delete key:sid from subs
    for key in data:
        del vals[key]
        subs[key].remove(sid)
        write_state()

@sio.event
def update_data(sid, data):
    # update key:val in vals
    for key, value in data.items():
        vals[key] = value
        write_state()
    # when a key is updated, all the sids that are subscribed to it should be notified
    for key in data:
        for sid in subs[key]:
            sio.emit('update_data', data={key:value}, room=sid)

@sio.event
def get_data(sid, data):
    # return key:val from vals
    for key in data:
        sio.emit('get_data', data={key:vals[key]}, room=sid)


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
