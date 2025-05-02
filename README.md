# RSS Tracker Service

![screenshot](https://github.com/user-attachments/assets/cf1eec9d-bdba-44d0-b82b-fcfb37fbab42)

Веб-сервис для мониторинга ключевых слов в RSS-лентах с сохранением результатов в БД

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

🔧 API Endpoints
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
[rss_tracker.log](https://github.com/user-attachments/files/20015142/rss_tracker.log)

📝 Лицензия
Проект распространяется под лицензией MIT. Полный текст доступен в файле LICENSE.
