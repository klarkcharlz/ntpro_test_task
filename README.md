# ntpro_test_task
Задача:

Тестовое задание для Python разработчиков
Написать небольшой сервис на языке Python, имитирующий работу банка со счетами клиентов.

Требования к сервису:

работа с сервисом должна осуществляться через ​ Interactive CLI 

состояние счетов хранится только в рамках одной сессии у клиента может быть только один счет валюта у всех счетов одинаковая USD

поддерживаемые операции: 

deposit - операция пополнения счета на сумму, аргументы:  client, amount, description

withdraw - операция снятия со счета, аргументы: client, amount, description

show_bank_statement - вывод на экран выписки со счета за период, аргументы: client, since ,till

Реализация:

Тестировалось в терминале Linux. В каждом скрипте прописал shebang. Если хотите запускать скрипты на исполнение без указания интерпритатора не забудьте дать файлам права на исполнение:

chmod +x server.py

chmod +x client.py

После этого запускайте скрипты так:

./server.py 

./client.py 

Задачу реализовал в виде двух скриптов, клиент и сервер. Сервер написан на библиотеке asyncio что бы мог обслуживать одновременно большое количество клиентов. А клиент написан на библиотеке socket.

Оба скрипта по умалчанию запускаются на порту 8888, но если он у Вас уже занят Вы можете в качестве аргумента командной строки передать скриптам номер порта, сначала запускайте сервер, а потом клиент, и если Вы запустили сервер с другим портом не забудьте что с таким же портом нужно запустить и клиент, например:

./server.py 8889

./client.py 8889

Уникальность ссесии обеспечивается спомощью случайно генерируемого в начале подключения uid, что бы каждый клиент получал доступ к даннным созданым лишь в  течении ссесии.

В качестве атрибута amount передавать только целые числа. Понял что надо было сделать с float, но заметил это когда уже стал писать это описание, и боюсь переделывать да бы что нибудь не сломать и не затянуть сдачу задания.

В самом коде задокументирована почти каждая строка.

Если заметите какие то грубые ошибки, или если у Вас вдруг что то не работает буду крайне рад если дадите шанс исправить.

Спасибо!

Для быстрого тестирования можете использовать Ваши же примеры, только меняйте значения атрибутов:

deposit --client="John Jones" --amount=100 --description="ATM Deposit"

withdraw --client="John Jones" --amount=100 --description="ATM Withdrawal"

show_bank_statement --client="John Jones" --since="2021-01-01 00:00:00" --till="2021-05-02 00:00:00"


Пример работы из терминала:
![Снимок экрана от 2021-05-01 12-38-13](https://user-images.githubusercontent.com/71945221/116778376-2fd2ac80-aa7a-11eb-9091-532b7f9d3413.png)

