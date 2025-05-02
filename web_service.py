import sqlite3
from flask import Flask, request, jsonify, render_template_string
import feedparser
from datetime import datetime
import threading
import time
import urllib.parse
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('rss_tracker.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def init_db():
    conn = sqlite3.connect('rss_tracker.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS feeds
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 url TEXT UNIQUE,
                 enabled BOOLEAN DEFAULT 1,
                 last_checked TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS keywords
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 keyword TEXT UNIQUE,
                 enabled BOOLEAN DEFAULT 1)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS news
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 feed_id INTEGER,
                 title TEXT,
                 description TEXT,
                 link TEXT UNIQUE,
                 pub_date TEXT,
                 found_date TEXT,
                 FOREIGN KEY(feed_id) REFERENCES feeds(id))''')
    
    try:
        c.execute("SELECT last_checked FROM feeds LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE feeds ADD COLUMN last_checked TEXT")
    
    conn.commit()
    conn.close()

def db_query(query, args=(), one=False):
    conn = sqlite3.connect('rss_tracker.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def check_news():
    while True:
        try:
            feeds = db_query("SELECT id, url FROM feeds WHERE enabled = 1")
            keywords = [row['keyword'].lower() for row in db_query("SELECT keyword FROM keywords WHERE enabled = 1")]
            
            if not keywords:
                time.sleep(60)
                continue
            
            for feed in feeds:
                try:
                    encoded_url = urllib.parse.quote(feed['url'], safe='/:')
                    feed_data = feedparser.parse(encoded_url)
                    
                    for entry in feed_data.entries:
                        title = getattr(entry, 'title', '')
                        description = getattr(entry, 'description', '')
                        link = getattr(entry, 'link', '')
                        pub_date = getattr(entry, 'published', datetime.now().isoformat())
                        
                        content = f"{title} {description}".lower()
                        if any(keyword in content for keyword in keywords):
                            exists = db_query("SELECT id FROM news WHERE link = ?", (link,), one=True)
                            if not exists:
                                db_query('''INSERT INTO news 
                                          (feed_id, title, description, link, pub_date, found_date) 
                                          VALUES (?, ?, ?, ?, ?, ?)''',
                                        (feed['id'], title, description, link, pub_date, datetime.now().isoformat()))
                                
                                logging.info(
                                    f"Найдена новость: {title}\n"
                                    f"Описание: {description[:200]}...\n"
                                    f"Источник: {feed['url']}\n"
                                    f"Ссылка: {link}\n"
                                    f"Дата публикации: {pub_date}\n"
                                    f"Ключевые слова: {', '.join(k for k in keywords if k in content.lower())}\n"
                                    "----------------------------------------"
                                )
                    
                    db_query("UPDATE feeds SET last_checked = ? WHERE id = ?", 
                            (datetime.now().isoformat(), feed['id']))
                
                except Exception as e:
                    logging.error(f"Ошибка при обработке ленты {feed['url']}: {str(e)}")
        
        except Exception as e:
            logging.error(f"Ошибка в основном цикле проверки новостей: {str(e)}")
        
        time.sleep(300)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RSS Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; background-color: #f8f9fa; font-family: Arial, sans-serif; }
        .news-container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
        .news-item { padding: 15px; margin-bottom: 15px; border-bottom: 1px solid #eee; }
        .news-title { color: #0d6efd; font-size: 1.2rem; margin-bottom: 10px; }
        .news-meta { font-size: 0.8rem; color: #666; margin-top: 10px; }
        .control-panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .section-title { color: #333; font-size: 1.3rem; margin-bottom: 15px; padding-bottom: 5px; border-bottom: 2px solid #0d6efd; }
        .list-item { padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
        .form-control { margin-bottom: 10px; }
        .news-container {
            max-width: 100%;
            overflow-x: hidden;
            word-wrap: break-word;
        }

        .news-item {
            max-width: 100%;
            overflow: hidden;
        }

        .news-title, .news-description {
            max-width: 100%;
            overflow-wrap: break-word;
            word-break: break-word;
        }

        .news-description img {
            max-width: 100%;
            height: auto;
        }

        table {
            width: 100%;
            table-layout: fixed;
        }

        td {
            word-wrap: break-word;
            max-width: 0;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">RSS Монитор</h1>
        
        <div class="row">
            <div class="col-md-8">
                <div class="news-container">
                    <h2 class="section-title">Последние новости</h2>
                    <div id="news-content">
                        {% for item in news %}
                        <div class="news-item">
                            <h3 class="news-title">
                                <a href="{{ item.link }}" target="_blank">{{ item.title }}</a>
                            </h3>
                            <div class="news-description">{{ item.description|safe }}</div>
                            <div class="news-meta">
                                <span>Источник: {{ item.url }}</span>
                                <span class="float-end">Найдено: {{ item.found_date }}</span>
                            </div>
                        </div>
                        {% else %}
                        <p>Новостей не найдено</p>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="control-panel">
                    <h2 class="section-title">Управление</h2>
                    
                    <div class="mb-4">
                        <h3>RSS-ленты</h3>
                        <div class="input-group mb-3">
                            <input type="text" id="feed-url" class="form-control" placeholder="URL RSS-ленты">
                            <button class="btn btn-primary" onclick="addFeed()">Добавить</button>
                        </div>
                        
                        <div id="feeds-list">
                            {% for feed in feeds %}
                            <div class="list-item d-flex justify-content-between align-items-center">
                                <div>
                                    <div>{{ feed.url }}</div>
                                    {% if feed.last_checked %}
                                    <div class="text-muted small">Проверено: {{ feed.last_checked }}</div>
                                    {% endif %}
                                </div>
                                <div>
                                    <div class="form-check form-switch d-inline-block me-2">
                                        <input class="form-check-input" type="checkbox" 
                                            {% if feed.enabled %}checked{% endif %}
                                            onchange="toggleFeed({{ feed.id }}, this.checked)">
                                    </div>
                                    <button class="btn btn-sm btn-danger" onclick="deleteFeed({{ feed.id }})">
                                        Удалить
                                    </button>
                                </div>
                            </div>
                            {% else %}
                            <p>Нет RSS-лент</p>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="mb-4">
                        <h3>Ключевые слова</h3>
                        <div class="input-group mb-3">
                            <input type="text" id="keyword-input" class="form-control" placeholder="Ключевое слово">
                            <button class="btn btn-primary" onclick="addKeyword()">Добавить</button>
                        </div>
                        
                        <div id="keywords-list">
                            {% for keyword in keywords %}
                            <div class="list-item d-flex justify-content-between align-items-center">
                                <span>{{ keyword.keyword }}</span>
                                <div>
                                    <div class="form-check form-switch d-inline-block me-2">
                                        <input class="form-check-input" type="checkbox" 
                                            {% if keyword.enabled %}checked{% endif %}
                                            onchange="toggleKeyword({{ keyword.id }}, this.checked)">
                                    </div>
                                    <button class="btn btn-sm btn-danger" onclick="deleteKeyword({{ keyword.id }})">
                                        Удалить
                                    </button>
                                </div>
                            </div>
                            {% else %}
                            <p>Нет ключевых слов</p>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function addFeed() {
            const url = document.getElementById('feed-url').value.trim();
            if (!url) {
                alert('Пожалуйста, введите URL RSS-ленты');
                return;
            }
            
            fetch('/api/feeds', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            }).then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Ошибка при добавлении RSS-ленты');
                }
            }).catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка');
            });
        }
        
        function deleteFeed(id) {
            if (!confirm('Вы уверены, что хотите удалить эту RSS-ленту?')) return;
            
            fetch('/api/feeds', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id })
            }).then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Ошибка при удалении RSS-ленты');
                }
            });
        }
        
        function toggleFeed(id, enabled) {
            fetch(`/api/toggle/feed/${id}`, { method: 'POST' });
        }
        
        function addKeyword() {
            const keyword = document.getElementById('keyword-input').value.trim();
            if (!keyword) {
                alert('Пожалуйста, введите ключевое слово');
                return;
            }
            
            fetch('/api/keywords', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ keyword: keyword })
            }).then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Ошибка при добавлении ключевого слова');
                }
            });
        }
        
        function deleteKeyword(id) {
            if (!confirm('Вы уверены, что хотите удалить это ключевое слово?')) return;
            
            fetch('/api/keywords', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: id })
            }).then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Ошибка при удалении ключевого слова');
                }
            });
        }
        
        function toggleKeyword(id, enabled) {
            fetch(`/api/toggle/keyword/${id}`, { method: 'POST' });
        }
        
        // Автообновление страницы каждые 5 минут
        setTimeout(() => location.reload(), 300000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    news = db_query('''SELECT n.id, f.url, n.title, n.description, n.link, 
                      n.pub_date, n.found_date 
                      FROM news n JOIN feeds f ON n.feed_id = f.id 
                      ORDER BY n.found_date DESC LIMIT 50''')
    
    feeds = db_query("SELECT id, url, enabled, last_checked FROM feeds ORDER BY id")
    keywords = db_query("SELECT id, keyword, enabled FROM keywords ORDER BY id")
    
    return render_template_string(HTML_TEMPLATE, news=news, feeds=feeds, keywords=keywords)

@app.route('/api/feeds', methods=['GET', 'POST', 'DELETE'])
def manage_feeds():
    if request.method == 'GET':
        feeds = db_query("SELECT id, url, enabled, last_checked FROM feeds ORDER BY id")
        return jsonify([dict(row) for row in feeds])
    
    elif request.method == 'POST':
        url = request.json.get('url')
        if url:
            try:
                encoded_url = urllib.parse.quote(url, safe='/:')
                db_query("INSERT OR IGNORE INTO feeds (url, enabled) VALUES (?, 1)", (encoded_url,))
                return jsonify({'status': 'success'}), 201
            except Exception as e:
                print(f"Ошибка при добавлении ленты: {e}")
                return jsonify({'status': 'error'}), 400
        return jsonify({'status': 'error'}), 400
    
    elif request.method == 'DELETE':
        feed_id = request.json.get('id')
        if feed_id:
            try:
                db_query("DELETE FROM news WHERE feed_id = ?", (feed_id,))
                db_query("DELETE FROM feeds WHERE id = ?", (feed_id,))
                return jsonify({'status': 'success'})
            except:
                return jsonify({'status': 'error'}), 400
        return jsonify({'status': 'error'}), 400

@app.route('/api/keywords', methods=['GET', 'POST', 'DELETE'])
def manage_keywords():
    if request.method == 'GET':
        keywords = db_query("SELECT id, keyword, enabled FROM keywords ORDER BY id")
        return jsonify([dict(row) for row in keywords])
    
    elif request.method == 'POST':
        keyword = request.json.get('keyword')
        if keyword:
            try:
                db_query("INSERT OR IGNORE INTO keywords (keyword, enabled) VALUES (?, 1)", (keyword,))
                return jsonify({'status': 'success'}), 201
            except:
                return jsonify({'status': 'error'}), 400
        return jsonify({'status': 'error'}), 400
    
    elif request.method == 'DELETE':
        keyword_id = request.json.get('id')
        if keyword_id:
            try:
                db_query("DELETE FROM keywords WHERE id = ?", (keyword_id,))
                return jsonify({'status': 'success'})
            except:
                return jsonify({'status': 'error'}), 400
        return jsonify({'status': 'error'}), 400

@app.route('/api/toggle/<string:type>/<int:id>', methods=['POST'])
def toggle_status(type, id):
    if type not in ['feed', 'keyword']:
        return jsonify({'status': 'error', 'message': 'Invalid type'}), 400
    
    table = 'feeds' if type == 'feed' else 'keywords'
    db_query(f"UPDATE {table} SET enabled = NOT enabled WHERE id = ?", (id,))
    return jsonify({'status': 'success'})

@app.route('/api/news', methods=['GET'])
def get_news():
    limit = request.args.get('limit', default=50, type=int)
    news = db_query('''SELECT n.id, f.url, n.title, n.description, n.link, 
                      n.pub_date, n.found_date 
                      FROM news n JOIN feeds f ON n.feed_id = f.id 
                      ORDER BY n.found_date DESC LIMIT ?''', (limit,))
    return jsonify([dict(row) for row in news])

@app.route('/debug/db')
def debug_db():
    conn = sqlite3.connect('rss_tracker.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    tables = {
        'feeds': c.execute("SELECT * FROM feeds").fetchall(),
        'keywords': c.execute("SELECT * FROM keywords").fetchall(),
        'news': c.execute("SELECT * FROM news ORDER BY found_date DESC LIMIT 20").fetchall()
    }
    conn.close()
    
    return jsonify({k: [dict(row) for row in v] for k, v in tables.items()})

def migrate_urls():
    conn = sqlite3.connect('rss_tracker.db')
    c = conn.cursor()
    c.execute("SELECT id, url FROM feeds")
    feeds = c.fetchall()
    
    for feed_id, url in feeds:
        if ' ' in url:
            encoded_url = urllib.parse.quote(url, safe='/:')
            c.execute("UPDATE feeds SET url = ? WHERE id = ?", (encoded_url, feed_id))
    
    conn.commit()
    conn.close()



if __name__ == '__main__':
    init_db()
    
    if not db_query("SELECT id FROM feeds LIMIT 1", one=True):
        default_feeds = [
            'https://www.goha.ru/rss/news',
            'https://www.goha.ru/rss/articles',
            'https://www.goha.ru/rss/videogames'
        ]
        for feed in default_feeds:
            db_query("INSERT OR IGNORE INTO feeds (url, enabled) VALUES (?, 1)", (feed,))
        
        default_keywords = ['игра', 'NVIDIA', 'киберспорт', 'аниме']
        for keyword in default_keywords:
            db_query("INSERT OR IGNORE INTO keywords (keyword, enabled) VALUES (?, 1)", (keyword,))
    
    thread = threading.Thread(target=check_news)
    thread.daemon = True
    thread.start()

    migrate_urls()
    app.run(host='0.0.0.0', port=5000, debug=False)