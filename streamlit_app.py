import streamlit as st
import re
import json
import base64
from pathlib import Path
import random
from datetime import datetime
import time
import requests
import os
from PIL import Image
import io

# ===== НАСТРОЙКА СТРАНИЦЫ =====
st.set_page_config(
    page_title="HTML Конструктор PRO — Полная версия",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CSS ДЛЯ УЛУЧШЕННОГО ВИДА =====
st.markdown("""
<style>
    /* Основные стили */
    .main-header {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #ff5a1e 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    
    /* Карточки блоков */
    .block-card {
        background: var(--bg-card, #f8f9fa);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border-left: 4px solid #ff5a1e;
        cursor: pointer;
        transition: all 0.25s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .block-card:hover {
        transform: translateX(6px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        border-left-color: #8b5cf6;
    }
    .block-card.selected {
        border-left-color: #8b5cf6;
        background: #f3f0ff;
        box-shadow: 0 4px 12px rgba(139,92,246,0.15);
    }
    .block-label {
        font-weight: 700;
        font-size: 0.95rem;
        color: #1a1a2e;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .block-desc {
        font-size: 0.8rem;
        color: #6c757d;
        margin: 4px 0;
        font-style: italic;
    }
    .block-meta {
        font-size: 0.7rem;
        color: #adb5bd;
        margin-top: 4px;
    }
    .block-preview-code {
        font-size: 0.65rem;
        font-family: 'JetBrains Mono', monospace;
        background: white;
        padding: 8px 10px;
        border-radius: 6px;
        border: 1px solid #e9ecef;
        max-height: 60px;
        overflow: hidden;
        white-space: pre-wrap;
        word-break: break-all;
        color: #1a1a2e;
        margin-top: 6px;
    }
    
    /* Бейджи и статусы */
    .badge-count {
        display: inline-block;
        background: #e9ecef;
        padding: 2px 12px;
        border-radius: 99px;
        font-size: 0.7rem;
        font-weight: 600;
        color: #495057;
    }
    .badge-improved {
        background: #10b981;
        color: white;
        padding: 2px 12px;
        border-radius: 99px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-ai {
        background: linear-gradient(135deg, #ff5a1e, #8b5cf6);
        color: white;
        padding: 2px 12px;
        border-radius: 99px;
        font-size: 0.65rem;
        font-weight: 700;
    }
    
    /* Кнопки */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .ai-button-main {
        background: linear-gradient(135deg, #ff5a1e, #8b5cf6) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
    }
    .ai-button-main:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 20px rgba(255,90,30,0.35) !important;
    }
    
    /* Текстовые области */
    .stTextArea > div > textarea {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        border-radius: 10px !important;
        line-height: 1.6 !important;
    }
    
    /* Боксы информации */
    .info-box {
        background: #dbeafe;
        border-radius: 10px;
        padding: 14px 18px;
        border-left: 4px solid #3b82f6;
        margin: 8px 0;
    }
    .success-box {
        background: #d1fae5;
        border-radius: 10px;
        padding: 14px 18px;
        border-left: 4px solid #10b981;
        margin: 8px 0;
    }
    .warning-box {
        background: #fef3c7;
        border-radius: 10px;
        padding: 14px 18px;
        border-left: 4px solid #f59e0b;
        margin: 8px 0;
    }
    
    /* Дашборд */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e9ecef;
        text-align: center;
        transition: all 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #1a1a2e;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #6c757d;
        font-weight: 500;
    }
    .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 4px;
    }
    
    /* Редактор стилей */
    .style-editor {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 14px;
        border: 1px solid #e9ecef;
    }
    .style-editor label {
        font-weight: 600;
        font-size: 0.85rem;
        color: #1a1a2e;
    }
    
    /* Генератор кода */
    .generator-box {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 12px;
        padding: 16px;
        border: 2px dashed #dee2e6;
    }
    
    /* Адаптивность */
    @media (max-width: 768px) {
        .main-header { font-size: 1.8rem; }
        .metric-value { font-size: 1.4rem; }
    }
    
    /* Тёмная тема (автоматическая) */
    @media (prefers-color-scheme: dark) {
        .block-card { background: #2d2d3d; border-left-color: #ff6b35; }
        .block-card.selected { background: #3d3d5d; }
        .block-label { color: #f0f0f0; }
        .block-preview-code { background: #1a1a2e; color: #e0e0e0; }
        .metric-card { background: #2d2d3d; border-color: #3d3d5d; }
        .metric-value { color: #f0f0f0; }
        .style-editor { background: #2d2d3d; border-color: #3d3d5d; }
        .generator-box { background: #2d2d3d; border-color: #3d3d5d; }
        .info-box { background: #1e2a4a; border-left-color: #3b82f6; }
        .success-box { background: #1a3a2a; border-left-color: #10b981; }
        .warning-box { background: #3a2a1a; border-left-color: #f59e0b; }
    }
    
    /* Анимации */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeInUp 0.4s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ===== ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ =====
if 'blocks' not in st.session_state:
    st.session_state.blocks = []
if 'original_html' not in st.session_state:
    st.session_state.original_html = ''
if 'selected_index' not in st.session_state:
    st.session_state.selected_index = -1
if 'undo_history' not in st.session_state:
    st.session_state.undo_history = []
if 'ai_improved_blocks' not in st.session_state:
    st.session_state.ai_improved_blocks = set()
if 'style_config' not in st.session_state:
    st.session_state.style_config = {
        'primary_color': '#ff5a1e',
        'secondary_color': '#8b5cf6',
        'font_family': 'Inter, system-ui, sans-serif',
        'border_radius': '12px',
        'shadow_intensity': '0.08'
    }
if 'generated_blocks' not in st.session_state:
    st.session_state.generated_blocks = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'api_provider' not in st.session_state:
    st.session_state.api_provider = 'OpenAI'
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = {}

# ===== ФУНКЦИИ =====

def parse_blocks(html):
    """Разбивает HTML на блоки с описаниями и метаданными"""
    blocks = []
    
    patterns = [
        {
            'name': 'Строка таблицы',
            'pattern': r'<tr[^>]*>[\s\S]*?<\/tr>',
            'description': 'Одна строка в таблице. Содержит данные одного товара, заказа или записи. Состоит из ячеек <td>.',
            'icon': '📊',
            'category': 'Таблицы'
        },
        {
            'name': 'Карточка',
            'pattern': r'<div[^>]*class="[^"]*card[^"]*"[^>]*>[\s\S]*?<\/div>',
            'description': 'Карточка товара или элемента. Содержит изображение, заголовок, цену, кнопку.',
            'icon': '🃏',
            'category': 'Карточки'
        },
        {
            'name': 'Секция',
            'pattern': r'<section[^>]*>[\s\S]*?<\/section>',
            'description': 'Крупный блок страницы: шапка, футер, основной контент.',
            'icon': '📐',
            'category': 'Секции'
        },
        {
            'name': 'Product-блок',
            'pattern': r'<div[^>]*class="[^"]*product[^"]*"[^>]*>[\s\S]*?<\/div>',
            'description': 'Блок товара с ценой, артикулом, кнопкой "Купить".',
            'icon': '🛍️',
            'category': 'Товары'
        },
        {
            'name': 'Элемент списка',
            'pattern': r'<li[^>]*>[\s\S]*?<\/li>',
            'description': 'Пункт списка <ul> или <ol>. Используется для меню, категорий.',
            'icon': '📋',
            'category': 'Списки'
        },
        {
            'name': 'Кнопка',
            'pattern': r'<button[^>]*>[\s\S]*?<\/button>',
            'description': 'Интерактивная кнопка для действий: "Купить", "Добавить", "Отправить".',
            'icon': '🔘',
            'category': 'Интерактив'
        },
        {
            'name': 'Блок с изображением',
            'pattern': r'<img[^>]*>',
            'description': 'Изображение. Содержит атрибуты src (ссылка) и alt (описание).',
            'icon': '🖼️',
            'category': 'Медиа'
        },
        {
            'name': 'Форма',
            'pattern': r'<form[^>]*>[\s\S]*?<\/form>',
            'description': 'Форма ввода данных. Содержит поля, кнопки отправки.',
            'icon': '📝',
            'category': 'Формы'
        },
        {
            'name': 'Навигация',
            'pattern': r'<nav[^>]*>[\s\S]*?<\/nav>',
            'description': 'Навигационный блок. Содержит ссылки на разделы сайта.',
            'icon': '🧭',
            'category': 'Навигация'
        },
        {
            'name': 'Footer',
            'pattern': r'<footer[^>]*>[\s\S]*?<\/footer>',
            'description': 'Подвал страницы. Содержит контактную информацию, копирайт.',
            'icon': '📌',
            'category': 'Структура'
        },
    ]
    
    all_matches = []
    for p in patterns:
        try:
            matches = re.finditer(p['pattern'], html, re.IGNORECASE | re.DOTALL)
            for match in matches:
                all_matches.append({
                    'name': p['name'],
                    'content': match.group(0),
                    'start': match.start(),
                    'description': p['description'],
                    'icon': p['icon'],
                    'category': p['category']
                })
        except:
            continue
    
    # Сортируем по позиции
    all_matches.sort(key=lambda x: x['start'])
    
    # Удаляем дубликаты
    unique = []
    seen = set()
    for m in all_matches:
        key = m['content'][:100]
        if key not in seen:
            seen.add(key)
            unique.append(m)
    
    for i, m in enumerate(unique):
        blocks.append({
            'id': i,
            'name': f"{m['icon']} {m['name']} #{i+1}",
            'content': m['content'],
            'original': m['content'],
            'description': m['description'],
            'icon': m['icon'],
            'category': m['category'],
            'size': len(m['content']),
            'lines': m['content'].count('\n') + 1,
            'tags': extract_tags(m['content']),
            'is_improved': False
        })
    
    if not blocks:
        blocks.append({
            'id': 0,
            'name': '📄 Весь HTML (файл целиком)',
            'content': html,
            'original': html,
            'description': 'Полный HTML-документ. Содержит все секции, стили, скрипты.',
            'icon': '📄',
            'category': 'Документ',
            'size': len(html),
            'lines': html.count('\n') + 1,
            'tags': [],
            'is_improved': False
        })
    
    return blocks

def extract_tags(content):
    """Извлекает теги из HTML-блока для аналитики"""
    tags = re.findall(r'<(\w+)', content)
    return list(set(tags))[:10]

def improve_block_with_ai(content, description, block_type, provider='OpenAI', api_key=''):
    """Улучшает блок через API ИИ или встроенную логику"""
    
    # Если нет API-ключа, используем встроенную логику
    if not api_key:
        return improve_block_local(content, description, block_type)
    
    try:
        if provider == 'OpenAI':
            return improve_with_openai(content, description, block_type, api_key)
        elif provider == 'DeepSeek':
            return improve_with_deepseek(content, description, block_type, api_key)
        elif provider == 'Claude (Anthropic)':
            return improve_with_claude(content, description, block_type, api_key)
        else:
            return improve_block_local(content, description, block_type)
    except Exception as e:
        st.warning(f"Ошибка API: {e}. Использую встроенный ИИ.")
        return improve_block_local(content, description, block_type)

def improve_with_openai(content, description, block_type, api_key):
    """Улучшение через OpenAI API"""
    import openai
    openai.api_key = api_key
    
    prompt = f"""Ты — эксперт по HTML-вёрстке. Улучши этот {description}.

Требования:
1. Добавь современные CSS-классы (Tailwind-подобные)
2. Добавь атрибуты доступности (aria-*, role)
3. Если есть таблица — добавь заголовки
4. Если есть карточка — добавь hover-эффекты и тени
5. Добавь микроразметку Schema.org (для товаров)
6. Сохрани структуру и плейсхолдеры

Выдай ТОЛЬКО HTML-код без пояснений:

{content}"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def improve_with_deepseek(content, description, block_type, api_key):
    """Улучшение через DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Ты — эксперт по HTML-вёрстке. Улучши этот {description}.

Требования:
1. Добавь современные CSS-классы
2. Добавь атрибуты доступности
3. Улучши структуру
4. Добавь hover-эффекты и тени
5. Добавь микроразметку Schema.org

Выдай ТОЛЬКО HTML-код без пояснений:

{content}"""

    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        raise Exception(f"DeepSeek API error: {response.status_code}")

def improve_with_claude(content, description, block_type, api_key):
    """Улучшение через Claude API (Anthropic)"""
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Ты — эксперт по HTML-вёрстке. Улучши этот {description}.

Требования:
1. Добавь современные CSS-классы
2. Добавь атрибуты доступности
3. Улучши структуру
4. Добавь hover-эффекты и тени
5. Добавь микроразметку Schema.org

Выдай ТОЛЬКО HTML-код без пояснений:

{content}"""

    data = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        return response.json()['content'][0]['text']
    else:
        raise Exception(f"Claude API error: {response.status_code}")

def improve_block_local(content, description, block_type):
    """Встроенная логика улучшения (без API)"""
    if not content or '<' not in content:
        return content
    
    improved = content
    
    # 1. Добавляем классы
    if 'class="' in improved and 'improved' not in improved:
        improved = improved.replace('class="', 'class="improved ')
    
    # 2. Добавляем aria-атрибуты для доступности
    if 'aria-label' not in improved and '<button' in improved:
        improved = improved.replace('<button', '<button aria-label="Кнопка"')
    if 'alt="' not in improved and '<img' in improved:
        improved = improved.replace('<img', '<img alt="Изображение"')
    if 'aria-label' not in improved and '<input' in improved:
        improved = improved.replace('<input', '<input aria-label="Поле ввода"')
    
    # 3. Улучшаем таблицы
    if '<tr' in improved and '<td' in improved:
        lines = improved.split('\n')
        for i, line in enumerate(lines):
            if '<tr' in line and '<td' in line and '<th' not in line:
                lines[i] = line.replace('<td', '<th').replace('</td>', '</th>')
                break
        improved = '\n'.join(lines)
    
    # 4. Добавляем hover-эффекты
    if 'hover:' not in improved:
        improved = improved.replace('class="', 'class="hover:shadow-lg transition-all duration-300 ')
    
    # 5. Улучшаем карточки
    if 'card' in improved.lower() or 'product' in improved.lower():
        if 'transform' not in improved:
            improved = improved.replace('class="', 'class="transform hover:scale-105 ')
        if 'shadow' not in improved:
            improved = improved.replace('class="', 'class="shadow-md hover:shadow-xl ')
        if 'rounded' not in improved:
            improved = improved.replace('class="', 'class="rounded-xl ')
    
    # 6. Семантические теги
    if '<div' in improved and ('Секция' in block_type or 'section' in improved.lower()):
        improved = improved.replace('<div', '<section').replace('</div>', '</section>')
    if '<div' in improved and ('Карточка' in block_type or 'card' in improved.lower()):
        improved = improved.replace('<div', '<article').replace('</div>', '</article>')
    
    # 7. Микроразметка Schema.org
    if 'itemscope' not in improved and ('Карточка' in block_type or 'Product' in block_type):
        improved = improved.replace('<article', '<article itemscope itemtype="https://schema.org/Product"')
        if 'itemprop="name"' not in improved:
            improved = improved.replace('<h3', '<h3 itemprop="name"')
        if 'itemprop="price"' not in improved:
            improved = improved.replace('class="price"', 'class="price" itemprop="price"')
        if 'itemprop="brand"' not in improved:
            improved = improved.replace('<div class="brand"', '<div class="brand" itemprop="brand"')
    
    # 8. Добавляем комментарии
    if '<!--' not in improved:
        improved = f'<!-- {description} (улучшено встроенным ИИ) -->\n{improved}'
    
    # 9. Добавляем стили для улучшения внешнего вида
    if 'style="' not in improved and 'style=' not in improved:
        improved = improved.replace('class="', 'style="' + get_style_from_config() + '" class="')
    
    return improved

def get_style_from_config():
    """Получает стили из конфигурации пользователя"""
    config = st.session_state.style_config
    return f"color:{config.get('primary_color', '#ff5a1e')};border-radius:{config.get('border_radius', '12px')};font-family:{config.get('font_family', 'Inter, sans-serif')}"

def generate_block_from_description(description):
    """Генерирует HTML-блок по текстовому описанию"""
    templates = {
        'карточка': '''
<div class="card hover:shadow-xl transition-all duration-300 transform hover:scale-105 rounded-xl p-6 bg-white border border-gray-200">
    <img src="https://via.placeholder.com/300x200" alt="Изображение товара" class="w-full h-48 object-cover rounded-lg">
    <h3 class="text-xl font-bold mt-4">Название товара</h3>
    <p class="text-gray-600 mt-2">Описание товара. Здесь может быть краткая информация.</p>
    <div class="flex items-center justify-between mt-4">
        <span class="text-2xl font-bold text-orange-500">1 299 ₽</span>
        <button class="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg font-semibold transition">Купить</button>
    </div>
</div>''',
        'таблица': '''
<table class="w-full border-collapse rounded-xl overflow-hidden shadow-md">
    <thead class="bg-gray-800 text-white">
        <tr>
            <th class="px-4 py-3 text-left">Артикул</th>
            <th class="px-4 py-3 text-left">Название</th>
            <th class="px-4 py-3 text-left">Цена</th>
            <th class="px-4 py-3 text-left">Статус</th>
        </tr>
    </thead>
    <tbody class="bg-white divide-y divide-gray-200">
        <tr class="hover:bg-gray-50 transition">
            <td class="px-4 py-3 font-mono">ART-001</td>
            <td class="px-4 py-3">Товар 1</td>
            <td class="px-4 py-3 font-semibold text-green-600">1 299 ₽</td>
            <td class="px-4 py-3"><span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">В наличии</span></td>
        </tr>
        <tr class="hover:bg-gray-50 transition">
            <td class="px-4 py-3 font-mono">ART-002</td>
            <td class="px-4 py-3">Товар 2</td>
            <td class="px-4 py-3 font-semibold text-green-600">2 499 ₽</td>
            <td class="px-4 py-3"><span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">Под заказ</span></td>
        </tr>
    </tbody>
</table>''',
        'кнопка': '''
<button class="bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-600 hover:to-purple-700 text-white font-bold py-3 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
    🚀 Действие
</button>''',
        'форма': '''
<form class="bg-white p-6 rounded-xl shadow-lg max-w-md">
    <h3 class="text-xl font-bold mb-4">Форма обратной связи</h3>
    <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Имя</label>
        <input type="text" placeholder="Введите имя" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent">
    </div>
    <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
        <input type="email" placeholder="email@example.com" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent">
    </div>
    <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Сообщение</label>
        <textarea rows="3" placeholder="Ваше сообщение..." class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"></textarea>
    </div>
    <button type="submit" class="w-full bg-orange-500 hover:bg-orange-600 text-white font-bold py-2 rounded-lg transition">Отправить</button>
</form>''',
        'секция': '''
<section class="py-12 px-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl">
    <div class="max-w-6xl mx-auto">
        <h2 class="text-3xl font-extrabold text-center mb-4">Заголовок секции</h2>
        <p class="text-gray-600 text-center max-w-2xl mx-auto mb-8">Описание секции. Здесь может быть важная информация для пользователей.</p>
        <div class="grid md:grid-cols-3 gap-6">
            <div class="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition">
                <div class="text-4xl mb-3">📊</div>
                <h3 class="font-bold text-lg">Пункт 1</h3>
                <p class="text-gray-600 text-sm">Описание пункта 1</p>
            </div>
            <div class="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition">
                <div class="text-4xl mb-3">🚀</div>
                <h3 class="font-bold text-lg">Пункт 2</h3>
                <p class="text-gray-600 text-sm">Описание пункта 2</p>
            </div>
            <div class="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition">
                <div class="text-4xl mb-3">🎯</div>
                <h3 class="font-bold text-lg">Пункт 3</h3>
                <p class="text-gray-600 text-sm">Описание пункта 3</p>
            </div>
        </div>
    </div>
</section>''',
        'навигация': '''
<nav class="bg-white shadow-md rounded-xl px-6 py-4">
    <div class="flex items-center justify-between max-w-6xl mx-auto">
        <div class="text-2xl font-extrabold text-orange-500">Логотип</div>
        <div class="flex gap-8">
            <a href="#" class="text-gray-700 hover:text-orange-500 font-medium transition">Главная</a>
            <a href="#" class="text-gray-700 hover:text-orange-500 font-medium transition">Каталог</a>
            <a href="#" class="text-gray-700 hover:text-orange-500 font-medium transition">О нас</a>
            <a href="#" class="text-gray-700 hover:text-orange-500 font-medium transition">Контакты</a>
        </div>
        <button class="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg font-semibold transition">Войти</button>
    </div>
</nav>'''
    }
    
    # Ищем ключевые слова в описании
    for key, template in templates.items():
        if key in description.lower():
            return template
    
    # Если ничего не найдено — возвращаем карточку по умолчанию
    return templates['карточка']

def analyze_blocks(blocks):
    """Анализирует блоки и возвращает статистику"""
    if not blocks:
        return {}
    
    analysis = {
        'total': len(blocks),
        'by_category': {},
        'by_tag': {},
        'total_size': sum(b.get('size', 0) for b in blocks),
        'total_lines': sum(b.get('lines', 0) for b in blocks),
        'improved_count': sum(1 for b in blocks if b.get('is_improved', False)),
        'largest_block': max(blocks, key=lambda x: x.get('size', 0)) if blocks else None,
        'smallest_block': min(blocks, key=lambda x: x.get('size', 0)) if blocks else None,
        'categories': {}
    }
    
    for block in blocks:
        category = block.get('category', 'Другое')
        analysis['by_category'][category] = analysis['by_category'].get(category, 0) + 1
        
        tags = block.get('tags', [])
        for tag in tags[:5]:
            analysis['by_tag'][tag] = analysis['by_tag'].get(tag, 0) + 1
    
    return analysis

def apply_style_to_html(html, style_config):
    """Применяет стили к HTML-коду"""
    if not html:
        return html
    
    # Добавляем глобальные стили если их нет
    if '<style' not in html:
        style_tag = f'''
<style>
    * {{ transition: all 0.2s ease; }}
    .primary-color {{ color: {style_config.get('primary_color', '#ff5a1e')}; }}
    .secondary-color {{ color: {style_config.get('secondary_color', '#8b5cf6')}; }}
    .rounded-custom {{ border-radius: {style_config.get('border_radius', '12px')}; }}
</style>
'''
        html = html.replace('</head>', style_tag + '</head>')
    
    return html

def get_download_link(content, filename, label):
    """Создаёт ссылку для скачивания"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}" style="text-decoration:none;background:linear-gradient(135deg,#ff5a1e,#8b5cf6);color:white;padding:10px 20px;border-radius:10px;font-weight:600;display:inline-block;">{label}</a>'
    return href

# ===== ЗАГОЛОВОК =====
st.markdown('<h1 class="main-header">🚀 HTML Конструктор PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Загрузите HTML, выберите блок, улучшите через ИИ и пересоберите — полная версия с аналитикой и генератором</p>', unsafe_allow_html=True)

# ===== САЙДБАР =====
with st.sidebar:
    st.markdown("### 📂 Управление")
    
    # Загрузка HTML
    uploaded_file = st.file_uploader("Загрузить HTML-файл", type=['html', 'htm'])
    if uploaded_file is not None:
        content = uploaded_file.read().decode('utf-8')
        st.session_state.original_html = content
        st.session_state.blocks = parse_blocks(content)
        st.session_state.selected_index = -1
        st.session_state.undo_history = []
        st.session_state.ai_improved_blocks = set()
        st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
        st.success(f"✅ Загружено! Найдено блоков: {len(st.session_state.blocks)}")
    
    st.divider()
    
    # ===== НАСТРОЙКА API =====
    st.markdown("### 🔗 API ИИ")
    
    api_provider = st.selectbox(
        "Выберите провайдера",
        ['Встроенный ИИ (без API)', 'OpenAI', 'DeepSeek', 'Claude (Anthropic)'],
        index=0
    )
    st.session_state.api_provider = api_provider
    
    if api_provider != 'Встроенный ИИ (без API)':
        api_key = st.text_input(
            f"API-ключ {api_provider}",
            type="password",
            placeholder=f"Введите {api_provider} API ключ...",
            value=st.session_state.api_key
        )
        st.session_state.api_key = api_key
        
        if api_key:
            st.success("✅ API-ключ сохранён")
        else:
            st.warning("⚠️ Введите API-ключ для использования внешнего ИИ")
    
    st.divider()
    
    # ===== КНОПКИ УПРАВЛЕНИЯ =====
    st.markdown("### 🛠️ Действия")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Сохранить", use_container_width=True):
            if st.session_state.blocks:
                result = st.session_state.original_html
                for b in st.session_state.blocks:
                    try:
                        escaped = re.escape(b['original'])
                        result = re.sub(escaped, b['content'], result, flags=re.DOTALL)
                    except:
                        pass
                
                filename = f"improved_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
                st.download_button(
                    label="📥 Скачать",
                    data=result,
                    file_name=filename,
                    mime="text/html",
                    use_container_width=True
                )
            else:
                st.warning("Нет данных")
    
    with col2:
        if st.button("🗑 Очистить", use_container_width=True):
            st.session_state.blocks = []
            st.session_state.original_html = ''
            st.session_state.selected_index = -1
            st.session_state.undo_history = []
            st.session_state.ai_improved_blocks = set()
            st.session_state.analysis_data = {}
            st.rerun()
    
    st.divider()
    
    # ===== ЭКСПОРТ/ИМПОРТ =====
    st.markdown("### 📤 Экспорт/Импорт")
    
    if st.button("📤 Экспорт JSON", use_container_width=True):
        if st.session_state.blocks:
            data = {
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'blocks': st.session_state.blocks,
                'original_html': st.session_state.original_html,
                'style_config': st.session_state.style_config
            }
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Скачать JSON",
                data=json_str,
                file_name="project_blocks.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.warning("Нет данных")
    
    uploaded_json = st.file_uploader("Импортировать JSON", type=['json'])
    if uploaded_json is not None:
        try:
            data = json.load(uploaded_json)
            st.session_state.blocks = data.get('blocks', [])
            st.session_state.original_html = data.get('original_html', '')
            st.session_state.selected_index = -1
            st.session_state.undo_history = []
            if 'style_config' in data:
                st.session_state.style_config = data['style_config']
            st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
            st.success(f"✅ Импортировано! Блоков: {len(st.session_state.blocks)}")
        except Exception as e:
            st.error(f"Ошибка: {e}")

# ===== ОСНОВНАЯ ОБЛАСТЬ =====
if not st.session_state.blocks:
    st.info("👈 Загрузите HTML-файл через боковую панель, чтобы начать работу")
    
    # Показываем демо-блоки
    st.markdown("### 🎯 Быстрый старт")
    col_demo1, col_demo2, col_demo3 = st.columns(3)
    
    with col_demo1:
        st.markdown("""
        <div class="info-box">
            <strong>📖 Загрузите HTML</strong><br>
            <small>Любой HTML-файл будет разбит на блоки автоматически</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col_demo2:
        st.markdown("""
        <div class="success-box">
            <strong>🤖 Улучшите через ИИ</strong><br>
            <small>Встроенный ИИ или API OpenAI/DeepSeek/Claude</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col_demo3:
        st.markdown("""
        <div class="warning-box">
            <strong>🚀 Скачайте результат</strong><br>
            <small>Пересоберите HTML со всеми улучшениями за 1 клик</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ===== ГЕНЕРАТОР КОДА =====
    st.markdown("### 📝 Генератор HTML-блоков")
    st.markdown("Опишите, какой блок нужен, и ИИ создаст его")
    
    col_gen1, col_gen2 = st.columns([2, 1])
    
    with col_gen1:
        block_description = st.text_area(
            "Опишите блок",
            placeholder="Например: карточка товара с ценой и кнопкой, таблица с артикулами, форма обратной связи...",
            height=80
        )
    
    with col_gen2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🎨 Сгенерировать блок", use_container_width=True, type="primary"):
            if block_description:
                generated = generate_block_from_description(block_description)
                st.session_state.generated_blocks.append({
                    'description': block_description,
                    'html': generated,
                    'timestamp': datetime.now().isoformat()
                })
                st.success("✅ Блок сгенерирован! Выберите его в списке ниже")
                st.rerun()
            else:
                st.warning("Введите описание")
    
    # Отображение сгенерированных блоков
    if st.session_state.generated_blocks:
        st.markdown("#### 📦 Сгенерированные блоки")
        for i, gen in enumerate(st.session_state.generated_blocks):
            with st.expander(f"Блок #{i+1}: {gen['description'][:50]}..."):
                st.code(gen['html'], language='html')
                if st.button(f"Использовать блок #{i+1}", key=f"use_gen_{i}"):
                    # Добавляем как обычный блок
                    new_block = {
                        'id': len(st.session_state.blocks),
                        'name': f"🎨 Сгенерированный #{i+1}",
                        'content': gen['html'],
                        'original': gen['html'],
                        'description': gen['description'],
                        'icon': '🎨',
                        'category': 'Сгенерированные',
                        'size': len(gen['html']),
                        'lines': gen['html'].count('\n') + 1,
                        'tags': extract_tags(gen['html']),
                        'is_improved': False
                    }
                    st.session_state.blocks.append(new_block)
                    st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                    st.success("✅ Блок добавлен!")
                    st.rerun()
    
    st.divider()
    
    # ===== НАСТРОЙКА СТИЛЕЙ =====
    st.markdown("### 🎨 Настройка стилей")
    st.markdown("Настройте глобальные стили для всех блоков")
    
    col_style1, col_style2, col_style3 = st.columns(3)
    
    with col_style1:
        st.session_state.style_config['primary_color'] = st.color_picker(
            "Основной цвет",
            value=st.session_state.style_config.get('primary_color', '#ff5a1e')
        )
    
    with col_style2:
        st.session_state.style_config['secondary_color'] = st.color_picker(
            "Вторичный цвет",
            value=st.session_state.style_config.get('secondary_color', '#8b5cf6')
        )
    
    with col_style3:
        st.session_state.style_config['border_radius'] = st.select_slider(
            "Скругление",
            options=['0px', '4px', '8px', '12px', '16px', '24px', '50px'],
            value=st.session_state.style_config.get('border_radius', '12px')
        )
    
    st.session_state.style_config['font_family'] = st.selectbox(
        "Шрифт",
        ['Inter, system-ui, sans-serif', 'Roboto, sans-serif', 'Arial, sans-serif', 
         'JetBrains Mono, monospace', 'Georgia, serif'],
        index=0
    )

else:
    # ===== ДАШБОРД АНАЛИТИКИ =====
    st.markdown("### 📊 Дашборд аналитики")
    
    analysis = st.session_state.analysis_data
    if analysis:
        col_metric1, col_metric2, col_metric3, col_metric4, col_metric5 = st.columns(5)
        
        with col_metric1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📦</div>
                <div class="metric-value">{analysis.get('total', 0)}</div>
                <div class="metric-label">Всего блоков</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_metric2:
            improved = analysis.get('improved_count', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">✨</div>
                <div class="metric-value">{improved}</div>
                <div class="metric-label">Улучшено ИИ</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_metric3:
            total_size = analysis.get('total_size', 0)
            size_kb = round(total_size / 1024, 1)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📄</div>
                <div class="metric-value">{size_kb} KB</div>
                <div class="metric-label">Общий размер</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_metric4:
            total_lines = analysis.get('total_lines', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📏</div>
                <div class="metric-value">{total_lines}</div>
                <div class="metric-label">Всего строк</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_metric5:
            categories = len(analysis.get('by_category', {}))
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">🏷️</div>
                <div class="metric-value">{categories}</div>
                <div class="metric-label">Типов блоков</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Детальная аналитика
        with st.expander("📊 Детальная аналитика", expanded=False):
            col_anal1, col_anal2 = st.columns(2)
            
            with col_anal1:
                st.markdown("**📂 Распределение по категориям**")
                if analysis.get('by_category'):
                    for cat, count in analysis['by_category'].items():
                        st.progress(count / analysis['total'], text=f"{cat}: {count}")
            
            with col_anal2:
                st.markdown("**🏷️ Частота тегов**")
                if analysis.get('by_tag'):
                    sorted_tags = sorted(analysis['by_tag'].items(), key=lambda x: x[1], reverse=True)[:10]
                    for tag, count in sorted_tags:
                        st.progress(min(count / 10, 1.0), text=f"&lt;{tag}&gt;: {count}")
            
            if analysis.get('largest_block'):
                lb = analysis['largest_block']
                st.info(f"🔺 Самый большой блок: **{lb.get('name', 'Неизвестно')}** ({lb.get('size', 0)} символов)")
            
            if analysis.get('smallest_block'):
                sb = analysis['smallest_block']
                st.info(f"🔻 Самый маленький блок: **{sb.get('name', 'Неизвестно')}** ({sb.get('size', 0)} символов)")
    
    st.divider()
    
    # ===== ТРИ КОЛОНКИ =====
    col1, col2, col3 = st.columns([1, 1, 1], gap="medium")
    
    # === КОЛОНКА 1: СПИСОК БЛОКОВ ===
    with col1:
        st.markdown("### 📦 Блоки")
        
        # Фильтры
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            search = st.text_input("🔍 Поиск", placeholder="Название...", key="search_blocks")
        
        with col_filter2:
            categories_list = ['Все'] + sorted(list(set(b.get('category', 'Другое') for b in st.session_state.blocks)))
            filter_category = st.selectbox("📂 Категория", categories_list, key="filter_category")
        
        # Фильтрация
        filtered_blocks = st.session_state.blocks
        if search:
            filtered_blocks = [b for b in filtered_blocks if search.lower() in b['name'].lower() or search.lower() in b['content'].lower()]
        if filter_category != 'Все':
            filtered_blocks = [b for b in filtered_blocks if b.get('category', 'Другое') == filter_category]
        
        # Отображение
        for i, block in enumerate(filtered_blocks):
            original_index = st.session_state.blocks.index(block)
            is_selected = original_index == st.session_state.selected_index
            is_improved = block.get('is_improved', False)
            
            # Карточка блока
            card_class = "block-card selected" if is_selected else "block-card"
            improved_badge = '<span class="badge-improved">✨ Улучшен</span>' if is_improved else ''
            
            # Используем HTML для красивого отображения
            block_html = f"""
            <div class="{card_class}">
                <div class="block-label">
                    <span>{block['name']}</span>
                    <span>
                        {improved_badge}
                        <span class="badge-count">{block.get('size', 0)}</span>
                    </span>
                </div>
                <div class="block-desc">{block.get('description', '')[:80]}...</div>
                <div class="block-meta">📂 {block.get('category', 'Другое')} • {block.get('lines', 0)} строк • {len(block.get('tags', []))} тегов</div>
            </div>
            """
            st.markdown(block_html, unsafe_allow_html=True)
            
            # ===== ИСПРАВЛЕННАЯ КНОПКА ВЫБОРА (без style) =====
            # Делаем видимую кнопку "Выбрать" вместо скрытой
            if st.button(f"📌 Выбрать {block['name']}", key=f"select_block_{i}", use_container_width=True):
                st.session_state.selected_index = original_index
                st.rerun()
            
            # Кнопки быстрых действий
            col_action1, col_action2 = st.columns(2)
            with col_action1:
                if st.button(f"🤖 Улучшить", key=f"quick_improve_{i}", use_container_width=True):
                    st.session_state.selected_index = original_index
                    block = st.session_state.blocks[original_index]
                    with st.spinner("🔄 ИИ улучшает блок..."):
                        improved = improve_block_with_ai(
                            block['content'],
                            block['description'],
                            block['name'],
                            st.session_state.api_provider,
                            st.session_state.api_key
                        )
                        st.session_state.undo_history.append({
                            'index': original_index,
                            'content': block['content']
                        })
                        if len(st.session_state.undo_history) > 20:
                            st.session_state.undo_history.pop(0)
                        block['content'] = improved
                        block['is_improved'] = True
                        st.session_state.ai_improved_blocks.add(original_index)
                        st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                        st.success("✅ Блок улучшен!")
                        st.rerun()
            
            with col_action2:
                if st.button(f"📋 Копировать", key=f"quick_copy_{i}", use_container_width=True):
                    st.code(block['content'], language='html')
                    st.success("📋 Блок скопирован!")
            
            st.divider()
    
    # === КОЛОНКА 2: РЕДАКТОР ===
    with col2:
        st.markdown("### ✏️ Редактор")
        
        if st.session_state.selected_index >= 0 and st.session_state.selected_index < len(st.session_state.blocks):
            block = st.session_state.blocks[st.session_state.selected_index]
            
            # Информация о блоке
            st.info(f"📌 {block.get('description', '')}")
            st.caption(f"Категория: {block.get('category', 'Другое')} • Размер: {block.get('size', 0)} символов • Строк: {block.get('lines', 0)}")
            
            # Редактор
            new_content = st.text_area(
                "Содержимое блока",
                value=block['content'],
                height=350,
                key="block_editor_main",
                help="Редактируйте HTML-код блока здесь"
            )
            
            # Кнопки
            col_buttons1, col_buttons2, col_buttons3, col_buttons4 = st.columns(4)
            
            with col_buttons1:
                if st.button("🔄 Обновить", use_container_width=True):
                    st.session_state.undo_history.append({
                        'index': st.session_state.selected_index,
                        'content': block['content']
                    })
                    if len(st.session_state.undo_history) > 20:
                        st.session_state.undo_history.pop(0)
                    block['content'] = new_content
                    block['is_improved'] = True
                    st.session_state.ai_improved_blocks.add(st.session_state.selected_index)
                    st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                    st.success("✅ Блок обновлён!")
                    st.rerun()
            
            with col_buttons2:
                if st.button("↩️ Отменить", use_container_width=True):
                    if st.session_state.undo_history:
                        last = st.session_state.undo_history.pop()
                        st.session_state.blocks[last['index']]['content'] = last['content']
                        st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                        st.success("↩️ Отменено!")
                        st.rerun()
                    else:
                        st.warning("Нет действий")
            
            with col_buttons3:
                if st.button("📋 Копировать", use_container_width=True):
                    st.code(block['content'], language='html')
                    st.success("📋 Скопировано!")
            
            with col_buttons4:
                if st.button("🎨 Применить стили", use_container_width=True):
                    styled = apply_style_to_html(new_content, st.session_state.style_config)
                    st.session_state.undo_history.append({
                        'index': st.session_state.selected_index,
                        'content': block['content']
                    })
                    block['content'] = styled
                    block['is_improved'] = True
                    st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                    st.success("✅ Стили применены!")
                    st.rerun()
            
            st.divider()
            
            # ===== КНОПКИ ИИ =====
            st.markdown("### 🤖 Улучшение через ИИ")
            
            col_ai1, col_ai2 = st.columns(2)
            
            with col_ai1:
                if st.button("🤖 Улучшить ИИ", use_container_width=True, type="primary"):
                    with st.spinner("🔄 ИИ улучшает блок..."):
                        improved = improve_block_with_ai(
                            block['content'],
                            block['description'],
                            block['name'],
                            st.session_state.api_provider,
                            st.session_state.api_key
                        )
                        st.session_state.undo_history.append({
                            'index': st.session_state.selected_index,
                            'content': block['content']
                        })
                        if len(st.session_state.undo_history) > 20:
                            st.session_state.undo_history.pop(0)
                        block['content'] = improved
                        block['is_improved'] = True
                        st.session_state.ai_improved_blocks.add(st.session_state.selected_index)
                        st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                        st.success("✅ Блок улучшен ИИ!")
                        st.rerun()
            
            with col_ai2:
                if st.button("📤 Отправить в ChatGPT", use_container_width=True):
                    prompt = f"Улучши этот {block['description']}. Добавь современные стили, сделай код чище, добавь недостающие атрибуты, улучши доступность. Сохрани структуру. Выдай только HTML-код без пояснений.\n\n{block['content']}"
                    
                    # Копируем в буфер через JavaScript
                    st.code(block['content'], language='html')
                    
                    # Ссылка на ChatGPT
                    chatgpt_url = f"https://chat.openai.com/?q={prompt}"
                    st.markdown(f'<a href="{chatgpt_url}" target="_blank" style="background:linear-gradient(135deg,#ff5a1e,#8b5cf6);color:white;padding:12px 24px;border-radius:12px;text-decoration:none;display:inline-block;font-weight:600;margin-top:8px;">🚀 Открыть ChatGPT</a>', unsafe_allow_html=True)
            
            # Показываем теги блока
            if block.get('tags'):
                st.markdown("**🏷️ Теги блока:**")
                tag_cols = st.columns(min(len(block['tags']), 5))
                for idx, tag in enumerate(block['tags'][:5]):
                    with tag_cols[idx % 5]:
                        st.markdown(f'<span class="badge-count">&lt;{tag}&gt;</span>', unsafe_allow_html=True)
        
        else:
            st.info("👈 Выберите блок слева для редактирования")
    
    # === КОЛОНКА 3: ПРЕВЬЮ И СБОРКА ===
    with col3:
        st.markdown("### 🖼️ Превью")
        
        if st.session_state.selected_index >= 0 and st.session_state.selected_index < len(st.session_state.blocks):
            block = st.session_state.blocks[st.session_state.selected_index]
            
            # Визуальное превью
            st.markdown("**Визуальное отображение:**")
            st.markdown("---")
            st.components.v1.html(block['content'], height=300, scrolling=True)
            st.markdown("---")
            
            # Код блока
            with st.expander("📄 Исходный код", expanded=False):
                st.code(block['content'], language='html')
            
            st.divider()
            
            # ===== СБОРКА HTML =====
            st.markdown("### 🚀 Пересобрать HTML")
            
            if st.button("🚀 Пересобрать и скачать", use_container_width=True, type="primary"):
                result = st.session_state.original_html
                for b in st.session_state.blocks:
                    try:
                        escaped = re.escape(b['original'])
                        result = re.sub(escaped, b['content'], result, flags=re.DOTALL)
                    except:
                        pass
                
                # Применяем глобальные стили
                result = apply_style_to_html(result, st.session_state.style_config)
                
                filename = f"improved_{datetime.now().strftime('%Y%m%d_%H%M')}.html"
                
                st.download_button(
                    label="📥 Скачать HTML",
                    data=result,
                    file_name=filename,
                    mime="text/html",
                    use_container_width=True
                )
                
                st.success("✅ HTML готов к скачиванию!")
            
            # Информация
            st.divider()
            st.markdown("### 📊 Информация о блоке")
            st.markdown(f"**Название:** {block['name']}")
            st.markdown(f"**Категория:** {block.get('category', 'Другое')}")
            st.markdown(f"**Размер:** {block.get('size', 0)} символов")
            st.markdown(f"**Строк:** {block.get('lines', 0)}")
            st.markdown(f"**Улучшен:** {'✅ Да' if block.get('is_improved', False) else '❌ Нет'}")
            
            if block.get('is_improved', False):
                st.markdown('<span class="badge-improved">✨ Улучшен ИИ</span>', unsafe_allow_html=True)
        
        else:
            st.info("👈 Выберите блок для превью")
            
            # Инструкция
            st.divider()
            st.markdown("### 📖 Инструкция")
            st.markdown("""
            1. **Загрузите HTML** через боковую панель
            2. **Выберите блок** из списка слева
            3. **Улучшите блок**:
               - Нажмите "Улучшить ИИ" для автоматического улучшения
               - Или скопируйте блок → улучшите в ChatGPT → вставьте обратно
            4. **Обновите блок** и **пересоберите HTML**
            5. **Скачайте** готовый файл
            """)
            
            # Дополнительная информация
            st.markdown("""
            <div class="info-box">
                <strong>💡 Советы:</strong><br>
                • Используйте встроенный ИИ для быстрого улучшения<br>
                • Настройте API-ключ для более качественных улучшений<br>
                • Экспортируйте проект в JSON для переноса<br>
                • Используйте генератор для создания новых блоков
            </div>
            """, unsafe_allow_html=True)

# ===== ФУТЕР =====
st.divider()
st.markdown("""
<div style="text-align:center;color:#6c757d;font-size:0.8rem;padding:1rem 0;">
    🚀 HTML Конструктор PRO • Полная версия с ИИ, аналитикой и генератором<br>
    <span style="font-size:0.7rem;">Поддерживает: OpenAI, DeepSeek, Claude • Авто-улучшение • Дашборд • Генератор блоков</span>
</div>
""", unsafe_allow_html=True)
