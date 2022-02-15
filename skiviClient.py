import asyncio
import time
import socketio

loop = asyncio.get_event_loop()
sio = socketio.AsyncClient()

ROOMS_I_SUB_TO = []

async def send_room_list():
    await sio.emit('sub_to_rooms', data=ROOMS_I_SUB_TO)

async def put_data(key, value):
    await sio.emit('put_data', data={key: value})

async def del_data(key):
    await sio.emit('del_data', data=key)

async def update_data(key, value):
    await sio.emit('update_data', data={key:value})

async def get_data(key):
    await sio.emit('get_data', data=key)

@sio.event
async def connect():
    print('connected to server')
    print(sio.sid)
    await send_room_list()

async def start_server():
    await sio.connect('http://localhost:5000')
    await sio.wait()


if __name__ == '__main__':
    loop.run_until_complete(start_server())