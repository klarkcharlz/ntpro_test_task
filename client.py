#!/usr/bin/python3

from sys import argv
import socket
from datetime import datetime
from uuid import uuid1
import json


# информационное сообщение
help_mess = """
Hello. Commands available to you: 
1.Deposit - account replenishment operation for the amount.
Attributes: client, amount, description.
Example:
deposit --client="John Jones" --amount=100 --description="ATM Deposit"
2.withdraw - withdrawal operation.
Attributes: client, amount, description.
Example: 
withdraw --client="John Jones" --amount=100 --description="ATM Withdrawal"
3.show_bank_statement - displaying the account statement for the period.
Attributes: client, since, till.
Example: 
show_bank_statement --client="John Jones" --since="2021-01-01 00:00:00" --till="2021-02-01 00:00:00"
Please adhere strictly to the message format as in the examples. 
To disconnect the connection, enter: --exit.
To re-display the message, enter: --help. 
"""


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


class ClientError(Exception):
    """Класс ошибки клиента"""
    def __init__(self, text: str):
        self.text = text

    def __str__(self):
        return self.text


class Client:
    """Класс клиента"""
    def __init__(self, host: str, port: int, timeout=None):
        self.uid = str(uuid1())  # создаем уникальный id для пользователя на время сесии
        self.host = host  # адрес
        self.port = port  # порт
        self.timeout = timeout  # таймаут на подключение
        self.sep = '!!!%!!!'  # сложный разделитель uid и data нужен для сервера
        try:  # пробуем подключиться
            self.sock = socket.create_connection((host, port), timeout)
        except socket.error:  # если не получилось
            raise ClientError("no connection.")

    def close(self):
        """Закрытие соединение"""
        try:
            self.sock.close()
        except socket.error:
            raise ClientError("Close connection Error")

    @staticmethod
    def create_table(data: str):
        """Рисуем таблицу"""
        data = json.loads(data.replace("'", "\""))  # иначе ошибка

        max_len_date, max_len_description, max_len_withdrawals = 4, 11, 11
        max_len_deposits, max_len_balance = 8, 7
        total_withdrawals = 0
        total_deposits = 0
        total_balance = 0
        for d in data:
            # определяем максимальную длину полей
            if d['Withdrawals']:
                total_balance -= int(d['Withdrawals'][1:])
                total_withdrawals += int(d['Withdrawals'][1:])
            if d['Deposits']:
                total_balance += int(d['Deposits'][1:])
                total_deposits += int(d['Deposits'][1:])
            if len(d['Date']) > max_len_date:
                max_len_date = len(d['Date'])
            if len(d['Description']) > max_len_description:
                max_len_description = len(d['Description'])
            if len(d['Withdrawals']) > max_len_withdrawals:
                max_len_withdrawals = len(d['Withdrawals'])
            if len(d['Deposits']) > max_len_deposits:
                max_len_deposits = len(d['Deposits'])
            if len(d['Balance']) > max_len_balance:
                max_len_balance = len(d['Balance'])

        separation = "_" * \
                     (max_len_date + max_len_description + max_len_withdrawals + max_len_deposits + max_len_balance + 11)
        print('|Date' + " " * (max_len_date - 3) + "|Description" + " " * (
                    max_len_description - 10) + "|Withdrawals" + " " * (
                          max_len_withdrawals - 10) + "|Deposits" + " " * (max_len_deposits - 7) + "|Balance" + " " * (
                          max_len_balance - 6) + "|")
        print(separation)
        for d in data:
            print(f"|{d['Date']}" + " " * (max_len_date - len(d['Date']) + 1) + f"|{d['Description']}" + " " * (
                    max_len_description - len(d['Description']) + 1) + f"|{d['Withdrawals']}" + " " * (
                          max_len_withdrawals - len(d['Withdrawals']) + 1) + f"|{d['Deposits']}" +
                  " " * (max_len_deposits - len(d['Deposits']) + 1) +
                  f"|{d['Balance']}" + " " * (
                          max_len_balance - len(d['Balance']) + 1) + "|")
        print(separation)
        print("|" + " " * (max_len_date + 1) + "|Totals" + " " * (max_len_description - 5) + f"|${total_withdrawals}"
              + " " * (max_len_withdrawals - len(str(total_withdrawals))) + f"|${total_deposits}"
              + " " * (max_len_deposits - len(str(total_deposits))) + f"|${total_balance}"
              + " " * (max_len_balance - len(str(total_balance))) + "|")

    def send_data(self, data: str):
        """Отправка сообщения серверу"""
        try:
            print(f"{datetime.now()} - Send data: {data}.")  # фиксируем то что отправили
            # сообщение должно отправляться в виде строки байтов
            self.sock.sendall(self.uid.encode("utf8") + self.sep.encode("utf8") + data.encode("utf8"))
        except socket.error:  # возникновение проблем при отправке
            raise ClientError("Connection problems.")
        else:  # если всё отправилось, теперь считываем ответное сообщение
            data = b""  # так как данные получаются в бинарном виде
            while not data.endswith(b"\n\n"):  # считываем пока не встретим признак конца ответного сообщения
                try:
                    data += self.sock.recv(1024)  # считываем байты
                    if not data:  # если данные не приходят разрываем соединение
                        raise socket.error
                except socket.error:
                    raise ClientError("Connection problems.")
            data = data.decode()  # преобразуем в str
            if data.startswith("table"):  # если был запрос show_bank_statement будем рисовать таблицу
                self.create_table(data[5:].rstrip())
            else:
                print(f"{datetime.now()} - Received data: {data.rstrip()}.")  # фиксируем принятое сообщение


if __name__ == "__main__":
    port = port_definition()  # определяем порт
    client = Client("127.0.0.1", port, timeout=2)  # создаем объект клиента
    print(f"{datetime.now()}: Server connection established.")  # фиксируем фремя соединения с сервером
    print(help_mess)  # выводим информационное сообщение
    try:
        while True:  # начниаем ссесию, бесконечно опрашиваем пользователя пока он не решит разорвать соединение
            message = input("Pls write command:\n")  # просим ввести команду для отправки
            if message == "--exit":  # выходим из ссесии
                break
            elif message == "--help":  # повторно выводим информационное сообщение
                print(help_mess)
            else:
                client.send_data(message)  # отправляем сообщение серверу
    except Exception as err:  # при проблемах в соединение выводим ошибку
        print(err)
    print(f"{datetime.now()}: The connection to the server has been dropped.")  # фиксируем время разрыва соединения
    client.close()  # в случае выхода из сесии или при возникновении проблем закрываем соединение
