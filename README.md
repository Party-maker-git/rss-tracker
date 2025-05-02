# RSS Tracker Service
1. Главный интерфейс - просмотр новостей

![screenshot](https://github.com/user-attachments/assets/cf1eec9d-bdba-44d0-b82b-fcfb37fbab42)

3. Панель управления RSS-лентами

![Снимок экрана 2025-05-02 084318](https://github.com/user-attachments/assets/305dac35-e014-4450-9f30-b7a01d8861cc)
![Снимок экрана 2025-05-02 084035](https://github.com/user-attachments/assets/2be29b67-a55e-4468-9a32-d5ecad0922a4)

Веб-сервис для мониторинга ключевых слов в RSS-лентах с сохранением результатов в БД

![Снимок экрана 2025-05-02 085342](https://github.com/user-attachments/assets/bf4d5d0b-1e04-42fa-a136-39ca8d342805)
![Снимок экрана 2025-05-02 085438](https://github.com/user-attachments/assets/17a2e34a-fc44-42fd-b8d2-03d2ab7f42cd)

## 📌 Задание

Сервис состоит из двух частей:
1. Модуль сбора данных с RSS-лент
2. Веб-интерфейс для управления и просмотра результатов

**Функционал:**
- Отслеживание появления ключевых слов в новостях
- Сохранение результатов в SQLite БД
- Веб-интерфейс с таблицей найденных новостей
- Управление RSS-источниками и ключевыми словами

## 🚀 Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/Party-maker-git/rss-tracker.git
cd rss-tracker
```
2. Установите зависимости:
```bash

pip install -r requirements.txt
```

3. Запустите сервис:
```bash

python rss_tracker.py
```
4. Откройте в браузере:
http://localhost:5000

5. Откройте в браузере, что бы увидеть БД:
http://localhost:5000/debug/db

## 🔧 API Endpoints
### API Endpoints
| Метод | Endpoint | Описание | Пример тела запроса |
|-------|----------|----------|---------------------|
| GET | `/api/feeds` | Список RSS-лент | - |
| POST | `/api/feeds` | Добавить RSS-ленту | `{"url": "https://..."}` |
| DELETE | `/api/feeds` | Удалить RSS-ленту | `{"id": 1}` |
| GET | `/api/keywords` | Список ключевых слов | - |
| POST | `/api/keywords` | Добавить ключевое слово | `{"keyword": "NVIDIA"}` |
| DELETE | `/api/keywords` | Удалить ключевое слово | `{"id": 1}` |
| GET | `/api/news` | Получить новости | - |

## 📊 Результаты работы

### Пример лога за 4 часа
![Снимок экрана 2025-05-02 185033](https://github.com/user-attachments/assets/c0ac5b42-1b02-4c62-9aa5-827b1a1cf3ca)
[rss_tracker.log](https://github.com/user-attachments/files/20015142/rss_tracker.log)

📝 Лицензия
Проект распространяется под лицензией MIT. Полный текст доступен в файле LICENSE.

