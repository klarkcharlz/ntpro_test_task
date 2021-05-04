#!/usr/bin/python3

from sys import argv
import asyncio
from datetime import datetime
from re import match

bills = {}
patterns = {"deposit":
                r'deposit --client="(\w+ \w+)" --amount=(\d+(.\d{1,2})?) --description="([\w\s]+)"',
            "withdraw":
                r'withdraw --client="(\w+ \w+)" --amount=(\d+(.\d{1,2})?) --description="([\w\s]+)"',
            "show_bank_statement":
                r'show_bank_statement --client="(\w+ \w+)" --since="(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})" --till="(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
            }


def port_definition():
    """определение порта"""
    if len(argv) == 1:
        return 8888
    if len(argv) == 2:
        try:
            return int(argv[1])
        except Exception as err:
            raise err("port is not number")
    if len(argv) > 2:
        raise ValueError("too many attributes")


class ClientServerProtocol(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.end_mess = "\n\n"  # символ конца передачи данных

    def connection_made(self, transport):
        self.transport = transport

    def deposit(self, uid: str, groups: tuple):
        """Сохраняем данные о пополнении"""
        client, amount, _, description = groups
        if uid in bills:
            if client in bills[uid]:
                bills[uid][client].append({
                    "Date": datetime.now(),
                    "Description": description,
                    "Withdrawals": "",
                    "Deposits": f"${amount}",
                    "Balance": f"${round((float(amount) + float(bills[uid][client][-1]['Balance'][1:])), 2)}"
                })
            else:
                bills[uid][client] = [{
                    "Date": datetime.now(),
                    "Description": description,
                    "Withdrawals": "",
                    "Deposits": f"${amount}",
                    "Balance": f"${amount}"
                }]
        else:
            bills[uid] = {client: [
                {
                    "Date": datetime.now(),
                    "Description": description,
                    "Withdrawals": "",
                    "Deposits": f"${amount}",
                    "Balance": f"${amount}"
                }
            ]}
        return "Deposit operation was successful!"

    def withdraw(self, uid: str, groups: tuple):
        """Сохраняем данные о списании"""
        client, amount, _, description = groups
        if uid in bills:
            withdraw = round((float(bills[uid][client][-1]['Balance'][1:]) - float(amount)), 2)
            if withdraw >= 0:
                if client in bills[uid]:
                    bills[uid][client].append({
                        "Date": datetime.now(),
                        "Description": description,
                        "Withdrawals": f"${amount}",
                        "Deposits": "",
                        "Balance": f"${withdraw}"
                    })
            else:
                return "Sorry, the operation is not possible, you do not have enough money!"
        else:
            return "Sorry you are not in base!"
        return "Withdrawal operation was successful!"

    def show_bank_statement(self, uid: str, groups: tuple):
        if uid not in bills:
            return "Empty operation history"
        """Отправка списка операций"""
        client, since, till = groups
        # преобразуем str в datetime
        since, till = datetime.strptime(since, '%Y-%m-%d %H:%M:%S'), datetime.strptime(till, '%Y-%m-%d %H:%M:%S')

        def filter_data(d: dict):
            """Производим фильтрацию по временному промежутку"""
            date = d['Date']
            nonlocal since
            nonlocal till
            if since <= date <= till:
                return True
            else:
                return False
        # подготавливаем список данных к отправке
        l = list(filter(filter_data, bills[uid][client]))[:]
        if not l:
            return "Sorry no data for the required time period"  # если данных за нужный промежуток нету
        for d in l:
            d['Date'] = d['Date'].strftime('%Y-%m-%d %H:%M:%S')
        return "table" + str(l)  # метка для клиента

    def process_data(self, data: tuple):
        """Создание ответного сообщения"""
        uid, pattern, groups = data  # достаем id сессии, шаблон и данные
        # обрабатываем соответствующую команду
        if pattern == "deposit":
            return self.deposit(uid, groups)
        elif pattern == "withdraw":
            return self.withdraw(uid, groups)
        elif pattern == "show_bank_statement":
            return self.show_bank_statement(uid, groups)

    def data_validations(self, data: str):
        """Валидируем принятые данные"""
        print(f"Data validations: {data}")
        uid, data = data.split('!!!%!!!')  # получаем данные
        if data == 'delete':  # разрыв сессии
            if uid in bills:  # если данные сесии имеются удаляем их
                del bills[uid]
                print(f"Deleted data for {uid}.")
                return 'Del'
        for pattern, raw in patterns.items():  # проверяем сообщение на соответствие шаблонам
            full_match = match(raw, data)
            if full_match:
                groups = full_match.groups()
                print(f"Validation status is OK : {pattern}.")
                return uid, pattern, groups  # вовзращаем id сессии, шаблон и данные
        else:  # не соответствует ни одному шаблону
            print("Validations fail!")
            return None

    def data_received(self, data: bytes):
        """Этот метод вызывается когда будут приняты данные от клиента"""
        print(f"Time: {datetime.now()} - Data received: {data.decode()}.")  # фиксируем принятые данные
        data = self.data_validations(data.decode())  # валидируем принятые данные
        if data == 'Del':  # ничего не отправляем обратно после удаления данных
            pass
        elif data:  # если валидация прошла
            response = self.process_data(data) + self.end_mess  # формируем ответное сообщение
            self.transport.write(response.encode())  # отправляем ответ
            print(f"Time: {datetime.now()} - Data transmit: {response.rstrip()}.")  # фиксируем отправленные данные
        else:  # валидация провалена
            self.transport.write("Incorrect data!".encode() + self.end_mess.encode())  # фиксируем неудачу


def run_server(host: str, port: int):
    """Запуск сервера"""
    loop = asyncio.get_event_loop()  # цикл обработчик сопрограмм
    coroutine = loop.create_server(
        ClientServerProtocol,
        host, port
    )  # представляет собой сопрограмму и возвращает объект Server
    server = loop.run_until_complete(coroutine)  # передаем сервер в цикл
    try:
        print(f"{datetime.now()}:Server started.")  # фиксируем время запуска сервера
        loop.run_forever()  # запускаем цикл
    except KeyboardInterrupt:  # если не получилось
        print(f"{datetime.now()}: Сonnection interrupted!")  # фиксируем неудачное соединение
    server.close()  # отстанавливаем сервер
    loop.run_until_complete(server.wait_closed())  # ждем прекращения работы сервера
    loop.close()  # останавливаем цикл


if __name__ == "__main__":
    port = port_definition()  # определяем порт
    run_server("127.0.0.1", port)  # запускаем сервер
