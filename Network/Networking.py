import socket
import websockets
import asyncio
import traceback
import json
import os


from concurrent.futures import TimeoutError as ConnectionTimeOutError

HELLO_MY_NAME_IS = socket.gethostname()
print(HELLO_MY_NAME_IS)
# MY_IP = socket.gethostbyname(HELLO_MY_NAME_IS)
# print(MY_IP)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # UDP baglantisi
    s.connect(('8.8.8.8', 53))
    MY_IP = s.getsockname()[0]
    print(MY_IP)

CONNECTIONS = set()


class ConnectionHandler:
    websocket = None
    hostname = None
    uri = None
    state = 'Disconnect'

    async def send(self, message):
        try:
            data = json.dumps(message)
            await self.websocket.send(data)
        except:
            print("Continue...")

    async def recv(self):
        try:
            message = await self.websocket.recv()
            data = json.loads(message)
            return data
        except:
            traceback.print_exc()

    async def login(self):
      try:
        self.websocket = await asyncio.wait_for (websockets.connect(self.uri), timeout=3)
      except ConnectionTimeOutError:
          print(f"Connection timed out to {self.uri}")
          return
      except ConnectionRefusedError:
          print(f"Connection refused to {self.uri}")
          return
      except:
          return

      await self.send({'hostname': HELLO_MY_NAME_IS})

      challange = await self.recv()

      if 'challange' not in challange or 'hostname' not in challange:
          return
      if len(challange['challange']) > 1024 or len(challange['hostname']) > 1024:
          return

      self.hostname = challange['hostname']

      # Password hashing

      password = {'password': 'password'}

      await self.send(password)

      confirmation = await self.recv()

      confirmed = confirmation.get('connection')
      if confirmed =='authorized':
          self.state = 'Connected'
          print(f"Connected to {self.hostname}")
          return

    async def welcome(self) -> bool:
        greeting = await self.recv()
        if 'hostname' not in greeting: #Hostname i kontrol ettik
            return False
        if len(greeting['hostname']) >1024: #Hostname uzunluğunu sınırlıyoruz
            return False

        self.hostname = greeting['hostname']

        challange = {'challange': 'te', 'hostname': HELLO_MY_NAME_IS}
        await self.send(challange)

        password = await self.recv()

        if 'password' not in password:
            return False
        if len(password['password']) > 1024:
            return False

        # Actual password stuff
        if password['password'] =='password':
            await self.send({'connection': 'authorized'})
            self.state = 'Connected'
            print(f"New connection from {self.hostname}")
            asyncio.get_event_loop().create_task(self.listener())
            return True
        else:
            await self.send({'connection': 'unauthorized'})
            return False

    async def listener(self):
     try:
        async for message in self.websocket:
            data = json.loads(message)
            op_type = data.get('op_type')

            if op_type == 'status':
                print(f"{self.hostname} Status: {data['connections']} ")

            if op_type == 'request':
                print(f"{self.hostname} Requests File: {data['filename']}")

            if op_type == 'sending':
                print(f"{self.hostname} confirms sending file: {data['filename']}")

     except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed from {self.hostname}")
        await unregister(self)
     except:
        traceback.print_exc()
        await unregister(self)

    async def close(self):
        self.state = 'Disconnected'
        try:
            await self.websocket.close()
        except:
            traceback.print_exc()


class ServerHandler(ConnectionHandler):
    def __init__(self,websocket):
        self.websocket= websocket


class ClientHandler(ConnectionHandler):
    def __init__(self,uri):
        self.uri = uri


async def port_scan():
    if not MY_IP[:3] == '192' and not MY_IP[:3] == '10.' and not MY_IP[:3] == '172':  # Baska ipleri aramaması için
        print('Not a private network, SHUTTING DOWN!')
        exit()

    ip_range =MY_IP.split('.')  # ip adresini diziye atıyor
    ip_range.pop()  # Sondaki sayı sürekli değişeceği için siliyoruz
    ip_range = '.'.join(ip_range)
    print(ip_range)

    i = 31
    while i < 255:
        i += 1
        target_ip = f"{ip_range}.{i}"
        print(target_ip)
        uri = f"ws://{target_ip}:1111"  # Bağlanmak istediğimiz ip ve port
        connection = ClientHandler(uri)
        await connection.login()
        if connection.state == 'Connected':
            CONNECTIONS.add(connection)
            asyncio.get_event_loop().create_task(connection.listener())

        await asyncio.sleep(0)


async def register_client(websocket, _):
    connection = ServerHandler(websocket)
    done = False
    while True:
        if not done:
            if await connection.welcome():
                CONNECTIONS.add(connection)
                done = True

        await asyncio.sleep(0)


async def unregister(connection):
    await connection.close()
    try:
        CONNECTIONS.remove(connection)
    except:
        traceback.print_exc()


async def status_update():
    while True:
        print(f"Updating Status... {len(CONNECTIONS)}")
        connection_list = []
        for connection in CONNECTIONS:
            connection_list.append({'hostname': connection.hostname, 'uri': connection.uri})

        share_list = []
        with open('../data.txt') as json_file:
            data = json.load(json_file)
            for p in data['connections']:
                print('Name: ' + p['name'])
                print('Website: ' + p['website'])
                print('From: ' + p['from'])

        for connection in CONNECTIONS:
            if connection.state == 'Connected':
                await connection.send({'op_type':'status',
                                       'hostname': HELLO_MY_NAME_IS,
                                       'connections': len(CONNECTIONS)})

        await asyncio.sleep(10)

if __name__ == '__main__':
    start_server = websockets.serve(register_client, MY_IP, 1111)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().create_task(status_update())
    asyncio.get_event_loop().run_forever()

