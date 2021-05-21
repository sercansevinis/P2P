from Network import Networking
import asyncio


async def client_things():
    await Networking.port_scan()


if __name__ == '__main__':
    Networking.HELLO_MY_NAME_IS = 'Client'
    asyncio.get_event_loop().create_task(client_things())
    asyncio.get_event_loop().create_task(Networking.status_update())
    asyncio.get_event_loop().run_forever()
