# coursework

## Создание виртуального окружения и установка зависимостей
```bash
git clone git@github.com:UnholyDk/coursework.git
cd coursework
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Скрипты
```bash
chmod +x start_cluster.sh stop_cluster.sh start_job.py
```
`sudo ./start_cluster.sh`  -- Запускает кластер с правами root, состоящий из агента в режиме сервера(127.0.0.1:4647) + 3 агента в режиме клиента(:5656, :5657, :5658). Процессы запускаются в фоновом режиме (command &) <br><br>
`sudo ./stop_cluster.sh` -- Останавливает кластер, убивая процессы nomad агентов. <br><br>
`pytest -vs` -- запустит тест, который описан в `test_nomad.py` -- тестирует кластер, проверяя что кластер запустился корректно -- у сервера статус `alive`, а у клиентов статус готовности `ready`. <br><br>
`./start_job.py` - Запускает задачу, описанную в `fibonacci.hcl`, проверяет ее статус каждые 5 сек сообщая об этом, дожидается ее завершения, после выводит результат скрипта.
