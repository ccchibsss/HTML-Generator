import os
import sys
import json
from flask import Flask, render_template_string, request, jsonify
from bs4 import BeautifulSoup

# ==========================================
# 1. КОНФИГУРАЦИЯ И ЗАГРУЗКА ФАЙЛА
# ==========================================
# По умолчанию скрипт ищет файл 'upload.html' в папке со скриптом.
# Вы можете указать путь к файлу при запуске: python inspector.py путь/к/вашему.html
INPUT_HTML_FILE = "upload.html"
if len(sys.argv) > 1:
    INPUT_HTML_FILE = sys.argv[1]

# ==========================================
# 2. ФУНКЦИЯ ПАРСИНГА (ЗАМЕНИТЕ НА ВАШУ)
# ==========================================
def extract_and_wrap_blocks(html_content):
    """
    Эта функция принимает ваш монолитный HTML.
    Она должна найти каждый блок и обернуть его в div с data-block-id.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    blocks_data = []
    
    # ==========================================
    # ВАЖНО: Вставьте сюда ваш алгоритм разбиения на блоки.
    # На скриншоте у вас есть блоки с классами block-desc и block-meta.
    # Я написал пример поиска всех прямых дочерних элементов внутри body.
    # Если ваши блоки заканчиваются тегами, используйте свой парсер.
    # ==========================================
    
    # Ищем корневой контейнер. Чаще всего это body.
    container = soup.body
    if not container:
        container = soup.find('div', class_='main-container') # Если есть обертка
    
    # ПРИМЕР: Поиск всех блоков с вашим классом (замените на ваш реальный селектор!)
    # Если ваши блоки это <div class="block-desc">, ищите по нему:
    block_elements = container.find_all('div', class_='block-desc', recursive=False)
    
    # Если не нашли по классу (для теста скрипта), берем все прямые дочерние элементы body
    if not block_elements:
        block_elements = [child for child in container.find_all(recursive=False) if child.name]

    # ==========================================
    # Оборачиваем найденные элементы в интерактивные блоки
    # ==========================================
    for index, element in enumerate(block_elements):
        block_id = index + 1
        
        # Сохраняем оригинальный HTML этого конкретного блока
        raw_html = str(element)
        
        # Создаем обертку с уникальным ID
        wrapper = soup.new_tag('div')
        wrapper['class'] = 'block-wrapper'
        wrapper['data-block-id'] = str(block_id)
        # Для облегчения отладки можно записать имя:
        wrapper['data-block-name'] = f'Блок #{block_id}'
        
        # Оборачиваем элемент в нашу обертку (DOM манипуляция)
        element.wrap(wrapper)
        
        # Добавляем данные в список для передачи в JavaScript
        blocks_data.append({
            'id': block_id,
            'html': raw_html,
            'name': f'Блок #{block_id}'
        })

    # Возвращаем модифицированный HTML и JSON с данными
    return str(soup), blocks_data

# ==========================================
# 3. ШАБЛОН HTML (С CSS И JS ИНТЕРАКТИВНОСТЬЮ)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Инспектор HTML блоков</title>
    <style>
        /* Сброс базовых отступов браузера */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        /* Настройка главного окна на весь экран */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #f8f9fa;
            height: 100vh;
            overflow: hidden;
        }
        
        #preview-container {
            width: 100%;
            height: 100vh;
            overflow-y: auto; /* Прокрутка страницы внутри */
            padding: 30px;
            background: #ffffff;
            position: relative;
        }

        /* Стиль обертки: при наведении - синяя рамка */
        .block-wrapper {
            display: block;         /* Чтобы рамка охватывала весь блок */
            position: relative;
            cursor: pointer;
            transition: outline 0.15s ease-in-out, background-color 0.15s ease-in-out;
            border-radius: 3px;
        }

        .block-wrapper:hover {
            outline: 3px solid #3b82f6; /* Синяя рамка как в DevTools */
            outline-offset: -3px;
            background-color: rgba(59, 130, 246, 0.05); /* Легкий синий фон при наведении */
            z-index: 10;
        }
        
        /* Стили модального окна с кодом */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            z-index: 9999;
            justify-content: center;
            align-items: center;
        }
        
        .modal-overlay.active {
            display: flex;
        }

        .modal-box {
            background: #ffffff;
            border-radius: 16px;
            width: 90%;
            max-width: 900px;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            overflow: hidden;
            animation: modalSlide 0.2s ease-out;
        }

        @keyframes modalSlide {
            from { opacity: 0; transform: translateY(-20px) scale(0.95); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* Шапка модалки */
        .modal-header {
            padding: 20px 24px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f9fafb;
        }

        .modal-header h2 {
            font-size: 20px;
            font-weight: 600;
            color: #111827;
            margin: 0;
        }

        .modal-close {
            background: none;
            border: none;
            font-size: 28px;
            cursor: pointer;
            color: #6b7280;
            padding: 4px 12px;
            border-radius: 6px;
            transition: background 0.2s;
        }

        .modal-close:hover {
            background: #e5e7eb;
            color: #111827;
        }

        /* Тело модалки (Код) */
        .modal-body {
            padding: 20px 24px;
            overflow-y: auto;
            flex: 1;
            background: #f8fafc;
        }

        .modal-body pre {
            background: #1e293b;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.6;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            margin: 0;
            white-space: pre-wrap;
            word-break: break-all;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Подвал модалки (Кнопки) */
        .modal-footer {
            padding: 16px 24px 24px 24px;
            border-top: 1px solid #e5e7eb;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            background: #f9fafb;
        }

        .modal-btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            letter-spacing: 0.3px;
        }

        /* Кнопка Улучшить - красная (как на скрине) */
        .modal-btn.improve {
            background: #ef4444;
            color: white;
        }
        .modal-btn.improve:hover { background: #dc2626; transform: translateY(-1px); }

        /* Кнопка ChatGPT - зеленая */
        .modal-btn.chatgpt {
            background: #10a37f;
            color: white;
        }
        .modal-btn.chatgpt:hover { background: #0e8b6b; transform: translateY(-1px); }

        /* Кнопка Копировать - серая */
        .modal-btn.copy {
            background: #e5e7eb;
            color: #374151;
        }
        .modal-btn.copy:hover { background: #d1d5db; }

        /* Кнопка Закрыть - прозрачная */
        .modal-btn.cancel {
            margin-left: auto;
            background: transparent;
            color: #6b7280;
        }
        .modal-btn.cancel:hover { background: #f3f4f6; }
        
        /* Тост-уведомления */
        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: #1f2937;
            color: white;
            padding: 14px 28px;
            border-radius: 10px;
            font-size: 15px;
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: 99999;
            pointer-events: none;
        }
        .toast.show { opacity: 1; }
    </style>
</head>
<body>
    <!-- 1. ОБЛАСТЬ ПРЕДПРОСМОТРА -->
    <div id="preview-container">
        {{ GENERATED_HTML | safe }}
    </div>

    <!-- 2. МОДАЛЬНОЕ ОКНО -->
    <div id="modal-overlay" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h2 id="modal-title">Информация о блоке</h2>
                <button id="modal-close" class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <pre id="modal-code"></pre>
            </div>
            <div class="modal-footer">
                <button id="btn-improve" class="modal-btn improve">🤖 Улучшить через ИИ</button>
                <button id="btn-chatgpt" class="modal-btn chatgpt">📤 Отправить в ChatGPT</button>
                <button id="btn-copy" class="modal-btn copy">📋 Копировать</button>
                <button id="modal-close-btn2" class="modal-btn cancel">Закрыть</button>
            </div>
        </div>
    </div>

    <!-- 3. TOAST УВЕДОМЛЕНИЕ -->
    <div id="toast" class="toast">Готово!</div>

    <!-- 4. JAVASCRIPT (ОБРАБОТЧИКИ) -->
    <script>
        // Получаем данные блоков из Python (передано как JSON)
        const blocksData = {{ BLOCKS_JSON | safe }};
        let currentBlockId = null;

        const previewContainer = document.getElementById('preview-container');
        const modalOverlay = document.getElementById('modal-overlay');
        const modalTitle = document.getElementById('modal-title');
        const modalCode = document.getElementById('modal-code');
        const toast = document.getElementById('toast');

        // 1. ДЕЛЕГИРОВАНИЕ СОБЫТИЯ КЛИКА НА ВСЕЙ СТРАНИЦЕ
        previewContainer.addEventListener('click', function(e) {
            // Находим ближайший родительский элемент с классом .block-wrapper
            const blockWrapper = e.target.closest('.block-wrapper');
            if (blockWrapper) {
                const blockId = parseInt(blockWrapper.getAttribute('data-block-id'));
                const block = blocksData.find(b => b.id === blockId);
                if (block) {
                    openBlockModal(block);
                }
            }
        });

        // 2. ФУНКЦИЯ ОТКРЫТИЯ МОДАЛЬНОГО ОКНА
        function openBlockModal(block) {
            currentBlockId = block.id;
            modalTitle.textContent = `${block.name} (ID: ${block.id})`;
            modalCode.textContent = block.html;
            modalOverlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // Запрещаем скролл страницы сзади
        }

        // 3. ФУНКЦИЯ ЗАКРЫТИЯ МОДАЛЬНОГО ОКНА
        function closeBlockModal() {
            modalOverlay.classList.remove('active');
            document.body.style.overflow = ''; // Возвращаем скролл
            currentBlockId = null;
        }

        // Закрытие по крестику
        document.getElementById('modal-close').addEventListener('click', closeBlockModal);
        document.getElementById('modal-close-btn2').addEventListener('click', closeBlockModal);
        
        // Закрытие по клику на пустое место (фон)
        modalOverlay.addEventListener('click', function(e) {
            if (e.target === modalOverlay) {
                closeBlockModal();
            }
        });

        // Закрытие по нажатию Escape
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modalOverlay.classList.contains('active')) {
                closeBlockModal();
            }
        });

        // 4. КНОПКА "КОПИРОВАТЬ"
        document.getElementById('btn-copy').addEventListener('click', function() {
            const code = modalCode.textContent;
            if (navigator.clipboard) {
                navigator.clipboard.writeText(code).then(() => {
                    showToast('✅ Код скопирован в буфер обмена!');
                }).catch(() => {
                    fallbackCopyMethod(code);
                });
            } else {
                fallbackCopyMethod(code);
            }
        });

        // Запасной метод копирования (для старых браузеров)
        function fallbackCopyMethod(text) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                showToast('✅ Код скопирован в буфер обмена!');
            } catch (err) {
                showToast('❌ Ошибка копирования');
            }
            document.body.removeChild(textArea);
        }

        // 5. ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ УВЕДОМЛЕНИЙ (Toast)
        function showToast(message) {
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2500);
        }

        // 6. КНОПКА "УЛУЧШИТЬ ЧЕРЕЗ ИИ" (Запрос на сервер)
        document.getElementById('btn-improve').addEventListener('click', function() {
            const block = blocksData.find(b => b.id === currentBlockId);
            if (!block) return;
            
            fetch('/action/improve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: block.id, code: block.html })
            })
            .then(response => response.json())
            .then(data => {
                showToast('🚀 ' + (data.message || 'Запрос на улучшение отправлен!'));
            })
            .catch(() => {
                showToast('❌ Ошибка соединения с модулем улучшения ИИ');
            });
        });

        // 7. КНОПКА "ОТПРАВИТЬ В CHATGPT" (Запрос на сервер)
        document.getElementById('btn-chatgpt').addEventListener('click', function() {
            const block = blocksData.find(b => b.id === currentBlockId);
            if (!block) return;

            fetch('/action/chatgpt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: block.id, code: block.html })
            })
            .then(response => response.json())
            .then(data => {
                showToast('📤 ' + (data.message || 'Отправлено в ChatGPT'));
            })
            .catch(() => {
                showToast('❌ Ошибка отправки в ChatGPT');
            });
        });
    </script>
</body>
</html>
"""

# ==========================================
# 5. ЗАПУСК ВЕБ-СЕРВЕРА (FLASK)
# ==========================================
app = Flask(__name__)

@app.route('/')
def main_page():
    try:
        # Читаем ваш монолитный HTML файл
        with open(INPUT_HTML_FILE, 'r', encoding='utf-8') as file:
            raw_html = file.read()
        
        # Передаем его в функцию парсинга
        processed_html, blocks_list = extract_and_wrap_blocks(raw_html)
        
        # Встраиваем сгенерированный HTML и JSON-данные в шаблон
        final_page = HTML_TEMPLATE.replace('{{ GENERATED_HTML | safe }}', processed_html)\
                                  .replace('{{ BLOCKS_JSON | safe }}', json.dumps(blocks_list))
        return final_page
        
    except FileNotFoundError:
        return f"""
        <div style="padding:50px; font-family:sans-serif;">
            <h1>❌ Ошибка: Файл не найден</h1>
            <p>Скрипт не смог найти файл: <b>{INPUT_HTML_FILE}</b></p>
            <p>Запустите скрипт с указанием пути к вашему HTML файлу:</p>
            <pre>python inspector.py путь_к_вашему_файлу.html</pre>
        </div>
        """

# Обработчики кнопок (заглушки для интеграции с AI API)
@app.route('/action/improve', methods=['POST'])
def api_improve():
    data = request.json
    print(f"[СЕРВЕР] Получен запрос на улучшение блока #{data.get('id')}")
    # ВСТАВЬТЕ СЮДА ВАШУ ЛОГИКУ РАБОТЫ С OpenAI / Gemini / YandexGPT
    return jsonify({'status': 'ok', 'message': 'ИИ начал обработку (заглушка)'})

@app.route('/action/chatgpt', methods=['POST'])
def api_chatgpt():
    data = request.json
    print(f"[СЕРВЕР] Получен запрос на отправку в ChatGPT блока #{data.get('id')}")
    # ВСТАВЬТЕ СЮДА ВАШУ ЛОГИКУ ОТПРАВКИ В ChatGPT API
    return jsonify({'status': 'ok', 'message': 'Блок передан в ChatGPT (заглушка)'})

if __name__ == '__main__':
    print("="*60)
    print("🚀 ЗАПУСК ИНТЕРАКТИВНОГО ИНСПЕКТОРА HTML")
    print(f"📁 Загружаемый файл: {os.path.abspath(INPUT_HTML_FILE)}")
    print("🌐 Откройте в браузере: http://127.0.0.1:5000")
    print("="*60)
    print("⚠️  ВАЖНО: В функции extract_and_wrap_blocks замените поиск")
    print("   'div class=\"block-desc\"' на ваш личный алгоритм разбиения.")
    print("="*60)
    app.run(debug=True, port=5000, host='127.0.0.1')
