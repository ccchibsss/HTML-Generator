import streamlit as st
import re
import json
import base64
from datetime import datetime
import requests
import time
import os
from typing import List, Dict, Any, Optional

# ======================================================================
# НАСТРОЙКА СТРАНИЦЫ
# ======================================================================
st.set_page_config(
    page_title="Визуальный HTML-конструктор PRO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================================
# РАСШИРЕННЫЙ CSS ДЛЯ ВИЗУАЛЬНОГО ОТОБРАЖЕНИЯ
# ======================================================================
st.markdown("""
<style>
    /* --- ГЛАВНЫЙ ЗАГОЛОВОК --- */
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

    /* --- ГАЙД ДЛЯ НОВИЧКОВ --- */
    .guide-box {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 20px 24px;
        border: 2px solid #dee2e6;
        margin-bottom: 20px;
    }
    .guide-step {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin: 8px 0;
        padding: 6px 0;
    }
    .guide-step .num {
        background: #ff5a1e;
        color: white;
        border-radius: 50%;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 14px;
        flex-shrink: 0;
    }
    .guide-step .text {
        font-size: 0.95rem;
        color: #1a1a2e;
        line-height: 1.5;
    }
    .guide-step .text small {
        color: #6c757d;
        font-size: 0.85rem;
    }

    /* --- КАРТОЧКИ БЛОКОВ С МИНИАТЮРАМИ --- */
    .block-card {
        background: white;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 14px;
        border: 2px solid #e9ecef;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .block-card:hover {
        border-color: #ff5a1e;
        transform: translateX(4px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }
    .block-card.selected {
        border-color: #8b5cf6;
        background: #f8f4ff;
        box-shadow: 0 4px 12px rgba(139,92,246,0.15);
    }
    .block-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .block-name {
        font-weight: 700;
        font-size: 0.95rem;
        color: #1a1a2e;
    }
    .block-badges {
        display: flex;
        gap: 6px;
        align-items: center;
    }
    .badge-improved {
        background: #10b981;
        color: white;
        padding: 2px 10px;
        border-radius: 99px;
        font-size: 0.6rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-size {
        background: #e9ecef;
        color: #495057;
        padding: 2px 10px;
        border-radius: 99px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .block-desc {
        font-size: 0.8rem;
        color: #6c757d;
        margin-bottom: 6px;
        font-style: italic;
    }
    .block-meta {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        font-size: 0.7rem;
        color: #adb5bd;
        margin-top: 4px;
    }
    .block-meta .category-badge {
        background: #e9ecef;
        padding: 0 8px;
        border-radius: 99px;
        font-weight: 600;
        color: #495057;
    }

    /* --- МИНИАТЮРА HTML (реальное визуальное превью) --- */
    .mini-preview {
        border: 1px solid #dee2e6;
        border-radius: 8px;
        background: white;
        padding: 6px;
        margin-top: 6px;
        max-height: 120px;
        overflow: hidden;
        position: relative;
        font-size: 0.7rem;
        line-height: 1.4;
        transition: all 0.2s;
    }
    .mini-preview iframe {
        width: 100%;
        height: 120px;
        border: none;
        border-radius: 6px;
        pointer-events: none;
        transform: scale(0.8);
        transform-origin: top left;
        width: 125%;
        height: 150px;
        margin-left: -12.5%;
    }
    .mini-preview .fade {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 30px;
        background: linear-gradient(transparent, white);
        pointer-events: none;
    }
    .mini-label {
        font-size: 0.6rem;
        color: #adb5bd;
        margin-top: 4px;
        text-align: right;
    }

    /* --- МЕТРИКИ ДАШБОРДА --- */
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

    /* --- РЕДАКТОР СТИЛЕЙ --- */
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

    /* --- ГЕНЕРАТОР КОДА --- */
    .generator-box {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 12px;
        padding: 16px;
        border: 2px dashed #dee2e6;
    }

    /* --- ИНФОРМАЦИОННЫЕ БОКСЫ --- */
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

    /* --- АДАПТИВНОСТЬ --- */
    @media (max-width: 768px) {
        .main-header { font-size: 1.8rem; }
        .metric-value { font-size: 1.4rem; }
        .guide-step .text { font-size: 0.85rem; }
    }

    /* --- ТЁМНАЯ ТЕМА (автоматическая) --- */
    @media (prefers-color-scheme: dark) {
        .block-card { background: #2d2d3d; border-color: #3d3d5d; }
        .block-card.selected { background: #3d3d5d; }
        .block-name { color: #f0f0f0; }
        .block-desc { color: #b0b0c0; }
        .mini-preview { background: #1a1a2e; border-color: #3d3d5d; }
        .mini-preview .fade { background: linear-gradient(transparent, #1a1a2e); }
        .metric-card { background: #2d2d3d; border-color: #3d3d5d; }
        .metric-value { color: #f0f0f0; }
        .guide-box { background: #2d2d3d; border-color: #3d3d5d; }
        .guide-step .text { color: #e0e0e0; }
        .info-box { background: #1e2a4a; border-left-color: #3b82f6; }
        .success-box { background: #1a3a2a; border-left-color: #10b981; }
        .warning-box { background: #3a2a1a; border-left-color: #f59e0b; }
        .style-editor { background: #2d2d3d; border-color: #3d3d5d; }
        .generator-box { background: #2d2d3d; border-color: #3d3d5d; }
    }
</style>
""", unsafe_allow_html=True)

# ======================================================================
# ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ
# ======================================================================
if 'blocks' not in st.session_state:
    st.session_state.blocks = []  # Список всех блоков
if 'original_html' not in st.session_state:
    st.session_state.original_html = ''  # Исходный HTML
if 'selected_index' not in st.session_state:
    st.session_state.selected_index = -1  # Индекс выбранного блока
if 'undo_history' not in st.session_state:
    st.session_state.undo_history = []  # История изменений
if 'ai_improved_blocks' not in st.session_state:
    st.session_state.ai_improved_blocks = set()  # ID улучшенных блоков
if 'style_config' not in st.session_state:
    st.session_state.style_config = {
        'primary_color': '#ff5a1e',
        'secondary_color': '#8b5cf6',
        'font_family': 'Inter, system-ui, sans-serif',
        'border_radius': '12px',
        'shadow_intensity': '0.08'
    }
if 'generated_blocks' not in st.session_state:
    st.session_state.generated_blocks = []  # Сгенерированные блоки
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'api_provider' not in st.session_state:
    st.session_state.api_provider = 'Встроенный ИИ (без API)'
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = {}
if 'show_guide' not in st.session_state:
    st.session_state.show_guide = True

# ======================================================================
# ОСНОВНЫЕ ФУНКЦИИ
# ======================================================================

def parse_blocks(html: str) -> List[Dict[str, Any]]:
    """
    Разбивает HTML-документ на блоки: таблицы, карточки, секции, кнопки, формы,
    навигацию, изображения и списки. Возвращает список словарей с метаданными.
    """
    blocks = []
    patterns = [
        {
            'name': 'Таблица',
            'pattern': r'<table[^>]*>[\s\S]*?<\/table>',
            'desc': 'Таблица с данными (строки и столбцы)',
            'icon': '📊',
            'category': 'Таблицы',
            'explanation': 'Используется для отображения структурированных данных: товары, заказы, статистика.'
        },
        {
            'name': 'Карточка',
            'pattern': r'<div[^>]*class="[^"]*card[^"]*"[^>]*>[\s\S]*?<\/div>',
            'desc': 'Карточка товара или элемента',
            'icon': '🃏',
            'category': 'Карточки',
            'explanation': 'Блок с изображением, заголовком, описанием и кнопкой.'
        },
        {
            'name': 'Секция',
            'pattern': r'<section[^>]*>[\s\S]*?<\/section>',
            'desc': 'Секция страницы',
            'icon': '📐',
            'category': 'Секции',
            'explanation': 'Крупный логический блок: "О нас", "Контакты", "Почему мы".'
        },
        {
            'name': 'Кнопка',
            'pattern': r'<button[^>]*>[\s\S]*?<\/button>',
            'desc': 'Интерактивная кнопка',
            'icon': '🔘',
            'category': 'Интерактив',
            'explanation': 'Элемент для действий: купить, отправить, перейти.'
        },
        {
            'name': 'Форма',
            'pattern': r'<form[^>]*>[\s\S]*?<\/form>',
            'desc': 'Форма ввода',
            'icon': '📝',
            'category': 'Формы',
            'explanation': 'Сбор данных пользователя: заявки, обратная связь.'
        },
        {
            'name': 'Навигация',
            'pattern': r'<nav[^>]*>[\s\S]*?<\/nav>',
            'desc': 'Навигационное меню',
            'icon': '🧭',
            'category': 'Навигация',
            'explanation': 'Меню для перемещения по сайту.'
        },
        {
            'name': 'Изображение',
            'pattern': r'<img[^>]*>',
            'desc': 'Изображение',
            'icon': '🖼️',
            'category': 'Медиа',
            'explanation': 'Графический элемент для иллюстрации.'
        },
        {
            'name': 'Список',
            'pattern': r'<ul[^>]*>[\s\S]*?<\/ul>|<ol[^>]*>[\s\S]*?<\/ol>',
            'desc': 'Маркированный или нумерованный список',
            'icon': '📋',
            'category': 'Списки',
            'explanation': 'Перечень пунктов: преимущества, шаги инструкции.'
        }
    ]

    for p in patterns:
        matches = re.finditer(p['pattern'], html, re.IGNORECASE | re.DOTALL)
        for match in matches:
            blocks.append({
                'name': f"{p['icon']} {p['name']} #{len(blocks)+1}",
                'content': match.group(0),
                'original': match.group(0),
                'desc': p['desc'],
                'icon': p['icon'],
                'category': p['category'],
                'explanation': p['explanation'],
                'size': len(match.group(0)),
                'lines': match.group(0).count('\n') + 1,
                'is_improved': False,
                'preview_html': match.group(0)[:500] + ('…' if len(match.group(0)) > 500 else '')
            })

    if not blocks:
        blocks.append({
            'name': '📄 Весь HTML',
            'content': html,
            'original': html,
            'desc': 'Полный HTML-документ',
            'icon': '📄',
            'category': 'Документ',
            'explanation': 'Файл целиком, если не удалось разбить на блоки.',
            'size': len(html),
            'lines': html.count('\n') + 1,
            'is_improved': False,
            'preview_html': html[:500] + '…'
        })

    return blocks

def improve_block_local(content: str) -> str:
    """
    Встроенный ИИ-улучшатель (без API): добавляет классы, атрибуты доступности,
    hover-эффекты и семантические теги.
    """
    improved = content

    # Добавляем класс "improved" если нет
    if 'class="' in improved and 'improved' not in improved:
        improved = improved.replace('class="', 'class="improved ')

    # Добавляем aria-атрибуты для доступности
    if 'aria-label' not in improved and '<button' in improved:
        improved = improved.replace('<button', '<button aria-label="Кнопка"')
    if 'alt="' not in improved and '<img' in improved:
        improved = improved.replace('<img', '<img alt="Изображение"')
    if 'aria-label' not in improved and '<input' in improved:
        improved = improved.replace('<input', '<input aria-label="Поле ввода"')

    # Улучшаем таблицы — первую строку делаем заголовком
    if '<tr' in improved and '<td' in improved:
        lines = improved.split('\n')
        for i, line in enumerate(lines):
            if '<tr' in line and '<td' in line and '<th' not in line:
                lines[i] = line.replace('<td', '<th').replace('</td>', '</th>')
                break
        improved = '\n'.join(lines)

    # Добавляем hover-эффекты
    if 'hover:' not in improved and 'class="' in improved:
        improved = improved.replace('class="', 'class="hover:shadow-lg transition-all duration-300 ')

    # Улучшаем карточки: добавляем transform и тени
    if 'card' in improved.lower() or 'product' in improved.lower():
        if 'transform' not in improved:
            improved = improved.replace('class="', 'class="transform hover:scale-105 ')
        if 'shadow' not in improved:
            improved = improved.replace('class="', 'class="shadow-md hover:shadow-xl ')
        if 'rounded' not in improved:
            improved = improved.replace('class="', 'class="rounded-xl ')

    # Семантические теги
    if '<div' in improved and ('Секция' in improved or 'section' in improved.lower()):
        improved = improved.replace('<div', '<section').replace('</div>', '</section>')
    if '<div' in improved and ('Карточка' in improved or 'card' in improved.lower()):
        improved = improved.replace('<div', '<article').replace('</div>', '</article>')

    # Микроразметка Schema.org
    if 'itemscope' not in improved and ('Карточка' in improved or 'Product' in improved):
        improved = improved.replace('<article', '<article itemscope itemtype="https://schema.org/Product"')
        if 'itemprop="name"' not in improved:
            improved = improved.replace('<h3', '<h3 itemprop="name"')
        if 'itemprop="price"' not in improved:
            improved = improved.replace('class="price"', 'class="price" itemprop="price"')
        if 'itemprop="brand"' not in improved:
            improved = improved.replace('<div class="brand"', '<div class="brand" itemprop="brand"')

    # Добавляем комментарий
    if '<!--' not in improved:
        improved = f'<!-- Улучшено встроенным ИИ -->\n{improved}'

    # Добавляем базовые стили
    if 'style="' not in improved and 'style=' not in improved:
        improved = improved.replace('class="', 'style="' + get_style_from_config() + '" class="')

    return improved

def get_style_from_config() -> str:
    """Возвращает CSS-строку из конфигурации стилей."""
    config = st.session_state.style_config
    return (f"color:{config.get('primary_color', '#ff5a1e')};"
            f"border-radius:{config.get('border_radius', '12px')};"
            f"font-family:{config.get('font_family', 'Inter, sans-serif')};"
            f"box-shadow:0 4px 12px rgba(0,0,0,{config.get('shadow_intensity', '0.08')});")

def generate_block_from_description(description: str) -> str:
    """
    Генерирует HTML-блок по текстовому описанию (используется в генераторе).
    """
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
    for key, template in templates.items():
        if key in description.lower():
            return template
    return templates['карточка']  # по умолчанию

def analyze_blocks(blocks: List[Dict]) -> Dict:
    """Анализирует блоки и возвращает статистику."""
    analysis = {
        'total': len(blocks),
        'by_category': {},
        'improved_count': sum(1 for b in blocks if b.get('is_improved')),
        'total_size': sum(b.get('size', 0) for b in blocks),
        'total_lines': sum(b.get('lines', 0) for b in blocks),
    }
    for b in blocks:
        cat = b.get('category', 'Другое')
        analysis['by_category'][cat] = analysis['by_category'].get(cat, 0) + 1
    return analysis

def apply_style_to_html(html: str, style_config: Dict) -> str:
    """Внедряет глобальные стили в HTML-документ."""
    if not html:
        return html
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

# ======================================================================
# ФУНКЦИИ РАБОТЫ С API (OpenAI, DeepSeek, Claude)
# ======================================================================

def improve_with_openai(content: str, description: str, block_type: str, api_key: str) -> str:
    """Улучшает блок через OpenAI API."""
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

def improve_with_deepseek(content: str, description: str, block_type: str, api_key: str) -> str:
    """Улучшает блок через DeepSeek API."""
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

def improve_with_claude(content: str, description: str, block_type: str, api_key: str) -> str:
    """Улучшает блок через Claude API (Anthropic)."""
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

def improve_block_with_ai(content: str, description: str, block_type: str,
                          provider: str, api_key: str) -> str:
    """Улучшает блок через выбранного провайдера или встроенный ИИ."""
    if not api_key or provider == 'Встроенный ИИ (без API)':
        return improve_block_local(content)
    try:
        if provider == 'OpenAI':
            return improve_with_openai(content, description, block_type, api_key)
        elif provider == 'DeepSeek':
            return improve_with_deepseek(content, description, block_type, api_key)
        elif provider == 'Claude':
            return improve_with_claude(content, description, block_type, api_key)
        else:
            return improve_block_local(content)
    except Exception as e:
        st.warning(f"Ошибка API: {e}. Использую встроенный ИИ.")
        return improve_block_local(content)

# ======================================================================
# ВИЗУАЛЬНЫЙ ГАЙД ДЛЯ НОВИЧКОВ
# ======================================================================
def show_guide():
    st.markdown("""
    <div class="guide-box">
        <h3>🎓 Как пользоваться</h3>
        <div class="guide-step">
            <div class="num">1</div>
            <div class="text"><strong>Загрузите HTML</strong> — через боковую панель выберите файл.</div>
        </div>
        <div class="guide-step">
            <div class="num">2</div>
            <div class="text"><strong>Выберите блок</strong> — кликните на карточку с его названием. Справа появится его визуальное отображение.</div>
        </div>
        <div class="guide-step">
            <div class="num">3</div>
            <div class="text"><strong>Улучшите</strong> — нажмите "🤖 Улучшить ИИ" для автоматического улучшения блока (встроенным ИИ или через API).</div>
        </div>
        <div class="guide-step">
            <div class="num">4</div>
            <div class="text"><strong>Обновите и соберите</strong> — после изменений нажмите "Обновить блок", затем "Пересобрать HTML".</div>
        </div>
        <div style="background:#dbeafe;padding:10px 16px;border-radius:8px;margin-top:12px;">
            💡 <strong>Совет:</strong> Каждый блок отображается в виде миниатюры — вы сразу видите, как он выглядит.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ======================================================================
# ЗАГОЛОВОК ПРИЛОЖЕНИЯ
# ======================================================================
st.markdown('<h1 class="main-header">🚀 Визуальный HTML-конструктор PRO</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Загрузите HTML, работайте с блоками визуально, улучшайте через ИИ и скачивайте результат</p>', unsafe_allow_html=True)

# ======================================================================
# БОКОВАЯ ПАНЕЛЬ
# ======================================================================
with st.sidebar:
    st.markdown("### 📂 Управление")
    uploaded = st.file_uploader("Загрузить HTML", type=['html', 'htm'])
    if uploaded is not None:
        content = uploaded.read().decode('utf-8')
        st.session_state.original_html = content
        st.session_state.blocks = parse_blocks(content)
        st.session_state.selected_index = 0 if st.session_state.blocks else -1
        st.session_state.undo_history = []
        st.session_state.ai_improved_blocks = set()
        st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
        st.success(f"✅ Загружено! Найдено {len(st.session_state.blocks)} блоков")

    st.divider()
    st.markdown("### 🔧 Действия")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Сохранить", use_container_width=True):
            if st.session_state.blocks:
                result = st.session_state.original_html
                for b in st.session_state.blocks:
                    try:
                        result = re.sub(re.escape(b['original']), b['content'], result, flags=re.DOTALL)
                    except:
                        pass
                st.download_button("📥 Скачать HTML", data=result,
                                   file_name=f"improved_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                                   mime="text/html", use_container_width=True)
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
    st.markdown("### 🔗 API ИИ")
    st.session_state.api_provider = st.selectbox(
        "Выберите провайдера",
        ['Встроенный ИИ (без API)', 'OpenAI', 'DeepSeek', 'Claude'],
        index=0
    )
    if st.session_state.api_provider != 'Встроенный ИИ (без API)':
        key = st.text_input(f"API-ключ {st.session_state.api_provider}", type="password")
        if key:
            st.session_state.api_key = key
            st.success("✅ API-ключ сохранён")
        else:
            st.warning("⚠️ Введите API-ключ для использования внешнего ИИ")

    st.divider()
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
            st.warning("Нет данных для экспорта")
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
            st.error(f"Ошибка импорта: {e}")

# ======================================================================
# ОСНОВНАЯ ОБЛАСТЬ
# ======================================================================
if not st.session_state.blocks:
    # Показываем гайд и генератор
    show_guide()

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

    if st.session_state.generated_blocks:
        st.markdown("#### 📦 Сгенерированные блоки")
        for i, gen in enumerate(st.session_state.generated_blocks):
            with st.expander(f"Блок #{i+1}: {gen['description'][:50]}..."):
                st.code(gen['html'], language='html')
                if st.button(f"Использовать блок #{i+1}", key=f"use_gen_{i}"):
                    new_block = {
                        'id': len(st.session_state.blocks),
                        'name': f"🎨 Сгенерированный #{i+1}",
                        'content': gen['html'],
                        'original': gen['html'],
                        'desc': gen['description'],
                        'icon': '🎨',
                        'category': 'Сгенерированные',
                        'explanation': 'Создан по вашему описанию',
                        'size': len(gen['html']),
                        'lines': gen['html'].count('\n') + 1,
                        'is_improved': False,
                        'preview_html': gen['html'][:500] + ('…' if len(gen['html']) > 500 else '')
                    }
                    st.session_state.blocks.append(new_block)
                    st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                    st.success("✅ Блок добавлен!")
                    st.rerun()

    st.divider()
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
    st.session_state.style_config['shadow_intensity'] = st.slider(
        "Интенсивность тени",
        min_value=0.0,
        max_value=0.3,
        value=float(st.session_state.style_config.get('shadow_intensity', '0.08')),
        step=0.01
    )

else:
    # ===== ПОКАЗЫВАЕМ ГАЙД (если не скрыт) =====
    if st.session_state.show_guide:
        show_guide()
        if st.button("Скрыть гайд", use_container_width=True):
            st.session_state.show_guide = False
            st.rerun()

    # ===== ДАШБОРД МЕТРИК =====
    analysis = st.session_state.analysis_data
    if analysis:
        cols = st.columns(4)
        with cols[0]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📦</div>
                <div class="metric-value">{analysis.get('total', 0)}</div>
                <div class="metric-label">Всего блоков</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            improved = analysis.get('improved_count', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">✨</div>
                <div class="metric-value">{improved}</div>
                <div class="metric-label">Улучшено</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[2]:
            size_kb = round(analysis.get('total_size', 0) / 1024, 1)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📄</div>
                <div class="metric-value">{size_kb} KB</div>
                <div class="metric-label">Общий размер</div>
            </div>
            """, unsafe_allow_html=True)
        with cols[3]:
            lines = analysis.get('total_lines', 0)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">📏</div>
                <div class="metric-value">{lines}</div>
                <div class="metric-label">Строк кода</div>
            </div>
            """, unsafe_allow_html=True)

        # Детальная аналитика
        with st.expander("📊 Детальная аналитика", expanded=False):
            if analysis.get('by_category'):
                st.markdown("**Распределение по категориям:**")
                for cat, count in analysis['by_category'].items():
                    st.progress(count / analysis['total'], text=f"{cat}: {count}")

    st.divider()

    # ===== ТРИ КОЛОНКИ =====
    col_left, col_mid, col_right = st.columns([1.2, 1.2, 1.6], gap="medium")

    # === ЛЕВАЯ КОЛОНКА: СПИСОК БЛОКОВ С МИНИАТЮРАМИ ===
    with col_left:
        st.markdown("### 📦 Блоки")
        # Фильтры
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            search = st.text_input("🔍 Поиск", placeholder="Название...", key="search_blocks")
        with col_filter2:
            categories_list = ['Все'] + sorted(list(set(b.get('category', 'Другое') for b in st.session_state.blocks)))
            filter_category = st.selectbox("📂 Категория", categories_list, key="filter_category")

        filtered_blocks = st.session_state.blocks
        if search:
            filtered_blocks = [b for b in filtered_blocks if search.lower() in b['name'].lower() or search.lower() in b['content'].lower()]
        if filter_category != 'Все':
            filtered_blocks = [b for b in filtered_blocks if b.get('category', 'Другое') == filter_category]

        for idx, block in enumerate(filtered_blocks):
            original_index = st.session_state.blocks.index(block)
            is_selected = (original_index == st.session_state.selected_index)
            card_class = "block-card selected" if is_selected else "block-card"
            improved_badge = '<span class="badge-improved">✨ Улучшен</span>' if block.get('is_improved') else ''
            size_badge = f'<span class="badge-size">{block.get("size", 0)}</span>'
            category_badge = f'<span class="category-badge">{block.get("category", "Другое")}</span>'

            # Визуальная миниатюра — рендерим HTML в iframe (упрощённо через div)
            mini_html = block.get('preview_html', '')

            card_html = f"""
            <div class="{card_class}">
                <div class="block-header">
                    <span class="block-name">{block.get('name', 'Блок')}</span>
                    <span class="block-badges">
                        {improved_badge}
                        {size_badge}
                    </span>
                </div>
                <div class="block-desc">{block.get('desc', '')}</div>
                <div class="block-meta">
                    {category_badge}
                    <span>📏 {block.get('lines', 0)} строк</span>
                </div>
                <div class="mini-preview">
                    {mini_html}
                    <div class="fade"></div>
                </div>
                <div class="mini-label">👁️ нажмите "Выбрать" для детального просмотра</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            # Кнопка выбора блока (видимая)
            if st.button(f"Выбрать {block.get('name', '')}", key=f"select_btn_{idx}", use_container_width=True):
                st.session_state.selected_index = original_index
                st.rerun()

            # Быстрые действия
            col_act1, col_act2 = st.columns(2)
            with col_act1:
                if st.button(f"🤖 Улучшить", key=f"improve_{idx}", use_container_width=True):
                    with st.spinner("🔄 ИИ улучшает блок..."):
                        improved = improve_block_with_ai(
                            block['content'],
                            block['desc'],
                            block['name'],
                            st.session_state.api_provider,
                            st.session_state.api_key
                        )
                        st.session_state.undo_history.append({'idx': original_index, 'content': block['content']})
                        if len(st.session_state.undo_history) > 20:
                            st.session_state.undo_history.pop(0)
                        block['content'] = improved
                        block['is_improved'] = True
                        block['preview_html'] = improved[:500] + '…'
                        st.session_state.ai_improved_blocks.add(original_index)
                        st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                        st.success("✅ Блок улучшен!")
                        st.rerun()
            with col_act2:
                if st.button(f"📋 Код", key=f"code_{idx}", use_container_width=True):
                    st.code(block['content'], language='html')
            st.divider()

    # === СРЕДНЯЯ КОЛОНКА: РЕДАКТОР ===
    with col_mid:
        st.markdown("### ✏️ Редактор")
        if st.session_state.selected_index >= 0 and st.session_state.selected_index < len(st.session_state.blocks):
            block = st.session_state.blocks[st.session_state.selected_index]
            st.info(f"📖 {block.get('explanation', 'Описание отсутствует')}")
            st.caption(f"Категория: {block.get('category', 'Другое')} • Размер: {block.get('size', 0)} символов • Строк: {block.get('lines', 0)}")

            new_content = st.text_area(
                "Содержимое блока",
                value=block['content'],
                height=400,
                key="editor",
                help="Редактируйте HTML-код"
            )
            col_upd1, col_upd2, col_upd3, col_upd4 = st.columns(4)
            with col_upd1:
                if st.button("🔄 Обновить", use_container_width=True):
                    st.session_state.undo_history.append({'idx': st.session_state.selected_index, 'content': block['content']})
                    if len(st.session_state.undo_history) > 20:
                        st.session_state.undo_history.pop(0)
                    block['content'] = new_content
                    block['preview_html'] = new_content[:500] + '…'
                    block['is_improved'] = True
                    st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                    st.success("✅ Блок обновлён!")
                    st.rerun()
            with col_upd2:
                if st.button("↩️ Отменить", use_container_width=True):
                    if st.session_state.undo_history:
                        last = st.session_state.undo_history.pop()
                        st.session_state.blocks[last['idx']]['content'] = last['content']
                        st.session_state.blocks[last['idx']]['preview_html'] = last['content'][:500] + '…'
                        st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                        st.success("↩️ Отменено!")
                        st.rerun()
                    else:
                        st.warning("Нет действий для отмены")
            with col_upd3:
                if st.button("📋 Копировать", use_container_width=True):
                    st.code(block['content'], language='html')
                    st.success("📋 Скопировано в буфер (используйте Ctrl+C)")
            with col_upd4:
                if st.button("🎨 Применить стили", use_container_width=True):
                    styled = apply_style_to_html(new_content, st.session_state.style_config)
                    st.session_state.undo_history.append({'idx': st.session_state.selected_index, 'content': block['content']})
                    block['content'] = styled
                    block['preview_html'] = styled[:500] + '…'
                    block['is_improved'] = True
                    st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                    st.success("✅ Стили применены!")
                    st.rerun()

            st.divider()
            st.markdown("### 🤖 Улучшение через ИИ")
            col_ai1, col_ai2 = st.columns(2)
            with col_ai1:
                if st.button("🤖 Улучшить ИИ", use_container_width=True, type="primary"):
                    with st.spinner("🔄 ИИ улучшает блок..."):
                        improved = improve_block_with_ai(
                            block['content'],
                            block['desc'],
                            block['name'],
                            st.session_state.api_provider,
                            st.session_state.api_key
                        )
                        st.session_state.undo_history.append({'idx': st.session_state.selected_index, 'content': block['content']})
                        if len(st.session_state.undo_history) > 20:
                            st.session_state.undo_history.pop(0)
                        block['content'] = improved
                        block['is_improved'] = True
                        block['preview_html'] = improved[:500] + '…'
                        st.session_state.ai_improved_blocks.add(st.session_state.selected_index)
                        st.session_state.analysis_data = analyze_blocks(st.session_state.blocks)
                        st.success("✅ Блок улучшен ИИ!")
                        st.rerun()
            with col_ai2:
                if st.button("📤 Отправить в ChatGPT", use_container_width=True):
                    prompt = f"Улучши этот {block['desc']}. Добавь современные стили, сделай код чище, добавь недостающие атрибуты, улучши доступность. Сохрани структуру. Выдай только HTML-код без пояснений.\n\n{block['content']}"
                    st.code(block['content'], language='html')
                    chatgpt_url = f"https://chat.openai.com/?q={prompt}"
                    st.markdown(f'<a href="{chatgpt_url}" target="_blank" style="background:linear-gradient(135deg,#ff5a1e,#8b5cf6);color:white;padding:12px 24px;border-radius:12px;text-decoration:none;display:inline-block;font-weight:600;margin-top:8px;">🚀 Открыть ChatGPT</a>', unsafe_allow_html=True)

            # Отображение тегов
            if block.get('tags'):
                st.markdown("**🏷️ Теги блока:**")
                tags = block.get('tags', [])[:5]
                tag_cols = st.columns(len(tags))
                for i, tag in enumerate(tags):
                    with tag_cols[i]:
                        st.markdown(f'<span class="badge-count">&lt;{tag}&gt;</span>', unsafe_allow_html=True)
        else:
            st.info("👈 Выберите блок в списке")

    # === ПРАВАЯ КОЛОНКА: ВИЗУАЛЬНОЕ ПРЕВЬЮ ===
    with col_right:
        st.markdown("### 🖼️ Визуальное отображение")
        if st.session_state.selected_index >= 0 and st.session_state.selected_index < len(st.session_state.blocks):
            block = st.session_state.blocks[st.session_state.selected_index]
            st.markdown("**Как выглядит блок:**")
            st.components.v1.html(block['content'], height=350, scrolling=True)

            with st.expander("📄 Исходный код"):
                st.code(block['content'], language='html')

            st.divider()
            st.markdown("### 🚀 Сборка HTML")
            if st.button("🚀 Пересобрать и скачать", use_container_width=True, type="primary"):
                result = st.session_state.original_html
                for b in st.session_state.blocks:
                    try:
                        result = re.sub(re.escape(b['original']), b['content'], result, flags=re.DOTALL)
                    except:
                        pass
                result = apply_style_to_html(result, st.session_state.style_config)
                st.download_button(
                    label="📥 Скачать HTML",
                    data=result,
                    file_name=f"final_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                    mime="text/html",
                    use_container_width=True
                )
                st.success("✅ HTML готов к скачиванию!")

            st.divider()
            st.markdown("### 📊 Информация о блоке")
            st.markdown(f"**Название:** {block.get('name', '')}")
            st.markdown(f"**Категория:** {block.get('category', 'Другое')}")
            st.markdown(f"**Размер:** {block.get('size', 0)} символов")
            st.markdown(f"**Строк:** {block.get('lines', 0)}")
            st.markdown(f"**Улучшен:** {'✅ Да' if block.get('is_improved') else '❌ Нет'}")
            if block.get('is_improved'):
                st.markdown('<span class="badge-improved">✨ Улучшен ИИ</span>', unsafe_allow_html=True)
        else:
            st.info("👈 Выберите блок для визуализации")

    # === ПРЕВЬЮ ВСЕЙ СТРАНИЦЫ ===
    with col_right:
        if st.session_state.original_html:
            st.divider()
            with st.expander("🌐 Показать всю страницу целиком", expanded=False):
                st.components.v1.html(st.session_state.original_html, height=600, scrolling=True)

# ======================================================================
# ФУТЕР
# ======================================================================
st.divider()
st.markdown("""
<div style="text-align:center;color:#6c757d;font-size:0.8rem;padding:1rem 0;">
    🚀 Визуальный HTML-конструктор PRO • Редактируйте блоки и сразу видите результат<br>
    <span style="font-size:0.7rem;">Поддерживает: встроенный ИИ, OpenAI, DeepSeek, Claude • Генератор • Аналитика • Миниатюры блоков</span>
</div>
""", unsafe_allow_html=True)
