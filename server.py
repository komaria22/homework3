#
# Серверное приложение для соединений
# выполнила Козадаева Маша
#
import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport
    all_users: list = []
    history: list = []

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        print(data)

        decoded = data.decode()

        if self.login is not None:
            self.send_message(decoded)
        else:
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r\n", "")
            else:
                self.transport.write("Неправильный логин\n".encode())
            if self.login in self.all_users:
                self.transport.write(
                    f"Логин {self.login} занят, попробуйте другой\n".encode())
            else:
                self.all_users.append(self.login)
                self.transport.write(
                    f"Привет, {self.login}!\n".encode()
                )
            self.send_history()

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Клиент вышел")

    def send_message(self, content: str):
        message = f"{self.login}: {content}"
        self.history.append(content)
        for user in self.server.clients:
            user.transport.write(message.encode())

    def send_history(self):
        self.transport.write(
            f"10 сообщений {self.history[0:11]}!\n".encode()
        )

class Server:
    clients: list

    def __init__(self):
        self.clients = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()

process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
