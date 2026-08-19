#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ИНТЕРАКТИВНЫЙ ИНСПЕКТОР МОНОЛИТНОГО HTML
========================================
Данный скрипт загружает монолитный HTML-файл, разбивает его на блоки 
(по заданному вами CSS-селектору или структуре) и предоставляет веб-интерфейс 
для наглядного просмотра верстки на весь экран с возможностью клика по любому 
элементу для просмотра его исходного кода, копирования и отправки в ИИ.
"""

import os
import sys
import json
from flask import Flask, render_template_string, request, jsonify
from bs4 import BeautifulSoup

# =====================================================================
# 1. НАСТРОЙКИ И АРГУМЕНТЫ КОМАНДНОЙ СТРОКИ
# =====================================================================

# По умолчанию скрипт ищет файл 'upload.html' в текущей папке.
# Вы можете передать путь к файлу как аргумент при запуске:
# python inspector_full.py full_page.html
INPUT_HTML_FILE = "upload.html"

if len(sys.argv) > 1:
    INPUT_HTML_FILE = sys.argv[1]
    print(f"[INFO] Загружаем файл, переданный в аргументе: {INPUT_HTML_FILE}")

# ВАЖНО! Замените этот селектор на тот, которым ваше оригинальное приложение 
# отделяет один блок от другого внутри монолитного HTML.
# Например: 'div.block-item', '.component-wrapper', 'section[data-id]' и т.д.
BLOCK_CSS_SELECTOR = 'div.block-desc, div.component-wrapper, section[data-id]'


# =====================================================================
# 2. ИНИЦИАЛИЗАЦИЯ ВЕБ-СЕРВЕРА FLASK
# =====================================================================

app = Flask(__name__)


# =====================================================================
# 3. ФУНКЦИЯ ПАРСИНГА И РАЗБИЕНИЯ HTML НА БЛОКИ
# =====================================================================

def parse_and_wrap_html_blocks(raw_html_content):
    """
    Принимает на вход строку с монолитным HTML.
    Находит блоки по заданному CSS-селектору, оборачивает каждый блок в 
    интерактивный DIV с уникальным ID, собирает данные о каждом блоке в JSON
    и возвращает модифицированный HTML вместе с массивом данных блоков.
    """
    
    # Создаем объект BeautifulSoup для удобного DOM-парсинга
    soup = BeautifulSoup(raw_html_content, 'html.parser')
    
    # Ищем корневой контейнер. Если есть обертка, парсим внутри нее.
    # Если нет, парсим весь тег body.
    root_container = soup.body
    if not root_container:
        root_container = soup.find('main')
    if not root_container:
        root_container = soup.find('div', class_='app-container')
    
    # Для надежности, если ничего не нашли, берем весь документ
    if not root_container:
        root_container = soup
    
    # Ищем все элементы, которые являются отдельными блоками, 
    # используя указанный пользователем CSS_селектор
    block_elements = root_container.select(BLOCK_CSS_SELECTOR)
    
    # Если по селектору ничего не найдено (например, вы его не указали),
    # в качестве запасного варианта берём все прямые дочерние элементы body
    if not block_elements:
        print("[WARNING] Селектор не нашел блоков. Берем все прямые дочерние элементы.")
        block_elements = [child for child in root_container.find_all(recursive=False) if child.name]
    
    # Инициализируем список для хранения данных о блоках
    blocks_data = []
    
    # Проходим по каждому найденному элементу
    for index, element in enumerate(block_elements):
        
        # Генерируем уникальный ID для этого блока (начиная с 1)
        block_id = index + 1
        
        # Сохраняем оригинальный сырой HTML-код этого блока
        block_raw_html = str(element)
        
        # Создаем новую HTML-обертку (DIV), которая будет реагировать на клики
        wrapper_tag = soup.new_tag('div')
        
        # Присваиваем обертке CSS-класс, который ловит наведение мыши
        wrapper_tag['class'] = 'clickable-block-wrapper'
        
        # Навешиваем data-атрибут с ID блока для быстрой идентификации в JS
        wrapper_tag['data-block-id'] = str(block_id)
        
        # Навешиваем data-атрибут с именем блока для отображения в модалке
        wrapper_tag['data-block-name'] = f'Интерактивный блок #{block_id}'
        
        # Оборачиваем найденный DOM-элемент в созданную нами обертку.
        # Это ключевой момент: теперь в DOM структуре элемент лежит внутри обертки.
        element.wrap(wrapper_tag)
        
        # Записываем данные о блоке в общий массив для передачи в JavaScript
        blocks_data.append({
            'id': block_id,
            'html': block_raw_html,
            'name': f'Компонент #{block_id}'
        })
    
    print(f"[INFO] Успешно обнаружено и обернуто {len(blocks_data)} блоков.")
    
    # Возвращаем измененный HTML (с обертками) и JSON-данные о блоках
    return str(soup), blocks_data


# =====================================================================
# 4. ГЛАВНЫЙ HTML-ШАБЛОН ИНТЕРФЕЙСА (С ПОЛНЫМ CSS И JS)
# =====================================================================

# Обратите внимание: в этом шаблоне используется старый способ подстановки через .replace(),
# чтобы гарантировать совместимость с любой версией Python и Flask, 
# без привязки к конкретному шаблонизатору Jinja2, кроме как рендеринг строки.
FULL_HTML_INTERFACE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Полноэкранный инспектор кода HTML блоков</title>
    
    <!-- 
    ====================================================================
    CSS СТИЛИ. Оформление, анимации, модальные окна и интерактивность.
    ====================================================================
    -->
    <style>
        
        /* 1. ГЛОБАЛЬНЫЙ СБРОС СТИЛЕЙ */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        /* 2. СТИЛИЗАЦИЯ ТЕЛА СТРАНИЦЫ И ПРОКРУТКИ */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f0f2f5;
            height: 100vh;
            width: 100vw;
            overflow: hidden; /* Убираем двойную прокрутку */
        }
        
        /* 3. КОНТЕЙНЕР ПРЕДПРОСМОТРА (ЗАНИМАЕТ ВЕСЬ ЭКРАН) */
        #fullscreen-preview-container {
            width: 100%;
            height: 100vh;
            overflow-y: auto; /* Включаем прокрутку внутри самого контейнера */
            padding: 20px;
            background-color: #ffffff;
            position: relative;
        }
        
        /* 4. СТИЛИ ОБЕРТКИ БЛОКА (ПОДСВЕТКА ПРИ НАВЕДЕНИИ) */
        .clickable-block-wrapper {
            display: block;             /* Гарантируем блочное поведение */
            position: relative;         /* Для возможной абсолютной обводки внутри */
            cursor: pointer;            /* Указываем, что элемент кликабельный */
            outline: 2px solid transparent; /* Резервируем место под рамку, чтобы избежать скачков */
            outline-offset: -2px;
            transition: all 0.2s ease-in-out;
            border-radius: 4px;
            margin-bottom: 2px;         /* Небольшой отступ между блоками для удобства наведения */
        }
        
        /* 5. СТИЛИ ПРИ НАВЕДЕНИИ НА БЛОК */
        .clickable-block-wrapper:hover {
            outline: 3px solid #3b82f6;  /* Синяя рамка, как в Chrome DevTools */
            outline-offset: -3px;
            background-color: rgba(59, 130, 246, 0.03); /* Легкий полупрозрачный синий фон */
            z-index: 10;                 /* Поднимаем над соседними элементами */
        }
        
        /* 6. ОВЕРЛЕЙ МОДАЛЬНОГО ОКНА (ЗАТЕМНЕНИЕ ФОНА) */
        #code-inspector-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.65); /* Темный фон с прозрачностью */
            backdrop-filter: blur(6px);          /* Размытие фона за модалкой */
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        /* 7. АКТИВНОЕ СОСТОЯНИЕ МОДАЛЬНОГО ОКНА */
        #code-inspector-overlay.active {
            display: flex;
            opacity: 1;
        }
        
        /* 8. ЦЕНТРАЛЬНОЕ ОКНО С КОДОМ */
        .modal-content-box {
            background-color: #ffffff;
            border-radius: 20px;
            width: 90%;
            max-width: 1024px;
            max-height: 90vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.3);
            transform: translateY(20px) scale(0.95);
            transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        /* При активации включаем анимацию выплывания */
        #code-inspector-overlay.active .modal-content-box {
            transform: translateY(0) scale(1);
        }
        
        /* 9. ЗАГОЛОВОК МОДАЛЬНОГО ОКНА */
        .modal-header-section {
            padding: 20px 28px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f9fafb;
            border-radius: 20px 20px 0 0;
        }
        
        .modal-header-section h2 {
            font-size: 22px;
            font-weight: 700;
            color: #111827;
            margin: 0;
        }
        
        /* 10. КНОПКА ЗАКРЫТИЯ МОДАЛКИ */
        .modal-close-button {
            background: transparent;
            border: none;
            font-size: 32px;
            line-height: 1;
            cursor: pointer;
            color: #6b7280;
            padding: 4px 12px;
            border-radius: 8px;
            transition: background-color 0.2s, color 0.2s;
        }
        
        .modal-close-button:hover {
            background-color: #e5e7eb;
            color: #111827;
        }
        
        /* 11. ТЕЛО МОДАЛЬНОГО ОКНА (БЛОК ОТОБРАЖЕНИЯ КОДА) */
        .modal-code-body-section {
            padding: 24px 28px;
            overflow-y: auto;
            flex: 1;
            background-color: #f8fafc;
        }
        
        .modal-code-body-section pre {
            background-color: #1e293b; /* Темная тема для кода */
            color: #e2e8f0;
            padding: 24px;
            border-radius: 12px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', 'Bitstream Vera Sans Mono', monospace;
            font-size: 14px;
            line-height: 1.8;
            margin: 0;
            white-space: pre-wrap;
            word-break: break-all;
            box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.2);
            border: 1px solid #334155;
        }
        
        /* 12. ПОДВАЛ МОДАЛЬНОГО ОКНА (КНОПКИ ДЕЙСТВИЙ) */
        .modal-actions-footer {
            padding: 16px 28px 24px 28px;
            border-top: 1px solid #e5e7eb;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            background-color: #f9fafb;
            border-radius: 0 0 20px 20px;
        }
        
        /* 13. СТИЛИ КНОПОК ДЕЙСТВИЙ */
        .action-button {
            padding: 10px 22px;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            letter-spacing: 0.3px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Кнопка улучшения через ИИ (красная, как в оригинале) */
        .action-button.btn-improve-ai {
            background-color: #ef4444;
            color: white;
        }
        .action-button.btn-improve-ai:hover {
            background-color: #dc2626;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }
        
        /* Кнопка отправки в ChatGPT (зеленая, OpenAI стиль) */
        .action-button.btn-chatgpt {
            background-color: #10a37f;
            color: white;
        }
        .action-button.btn-chatgpt:hover {
            background-color: #0e8b6b;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
        }
        
        /* Кнопка копирования кода (серая) */
        .action-button.btn-copy-code {
            background-color: #e5e7eb;
            color: #374151;
        }
        .action-button.btn-copy-code:hover {
            background-color: #d1d5db;
            transform: translateY(-2px);
        }
        
        /* Кнопка закрытия (прозрачная, справа) */
        .action-button.btn-close-modal {
            margin-left: auto;
            background-color: transparent;
            color: #6b7280;
        }
        .action-button.btn-close-modal:hover {
            background-color: #f3f4f6;
            color: #111827;
        }
        
        /* 14. TOAST-УВЕДОМЛЕНИЯ (ВСПЛЫВАЮЩИЕ ПОДСКАЗКИ) */
        .floating-toast-message {
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #1f2937;
            color: #f9fafb;
            padding: 16px 32px;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 500;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
            z-index: 99999;
            pointer-events: none;
            border: 1px solid #374151;
        }
        
        .floating-toast-message.visible {
            opacity: 1;
            visibility: visible;
        }
        
    </style>
</head>
<body>

    <!-- 
    ====================================================================
    Основной контейнер для предпросмотра всей страницы
    ====================================================================
    -->
    <div id="fullscreen-preview-container">
        <!-- Сюда мы через Python вставим весь обернутый HTML -->
        {{ GENERATED_HTML | safe }}
    </div>

    <!-- 
    ====================================================================
    Модальное окно для отображения кода выбранного блока
    ====================================================================
    -->
    <div id="code-inspector-overlay" class="code-inspector-overlay">
        <div class="modal-content-box">
            
            <!-- Заголовок модалки -->
            <div class="modal-header-section">
                <h2 id="modal-block-title">Информация о компоненте</h2>
                <button id="modal-close-btn" class="modal-close-button">&times;</button>
            </div>
            
            <!-- Тело модалки с кодом -->
            <div class="modal-code-body-section">
                <pre id="modal-block-code-viewer"></pre>
            </div>
            
            <!-- Подвал модалки с кнопками -->
            <div class="modal-actions-footer">
                <button id="action-improve-ai" class="action-button btn-improve-ai">🤖 Улучшить через ИИ</button>
                <button id="action-chatgpt" class="action-button btn-chatgpt">📤 Отправить в ChatGPT</button>
                <button id="action-copy-clipboard" class="action-button btn-copy-code">📋 Копировать код</button>
                <button id="modal-close-btn-2" class="action-button btn-close-modal">Закрыть</button>
            </div>
        </div>
    </div>

    <!-- 
    ====================================================================
    Компонент всплывающего уведомления
    ====================================================================
    -->
    <div id="system-toast-message" class="floating-toast-message">Готово!</div>

    <!-- 
    ====================================================================
    JavaScript: Обработка кликов, модального окна и взаимодействий
    ====================================================================
    -->
    <script>
        
        // =============================================================
        // 1. ПРИНИМАЕМ ДАННЫЕ О БЛОКАХ ОТ PYTHON-СЕРВЕРА
        // =============================================================
        // Переменная blocksData будет автоматически заменена на JSON-строку
        // в момент рендеринга страницы сервером Flask.
        const blocksData = {{ BLOCKS_JSON | safe }};
        
        // Переменная для хранения ID блока, который сейчас открыт в модалке
        let currentOpenBlockId = null;

        // Получаем ссылки на DOM-элементы для дальнейшей работы с ними
        const previewContainer = document.getElementById('fullscreen-preview-container');
        const modalOverlay = document.getElementById('code-inspector-overlay');
        const modalTitleElement = document.getElementById('modal-block-title');
        const modalCodeViewer = document.getElementById('modal-block-code-viewer');
        const toastMessage = document.getElementById('system-toast-message');

        // =============================================================
        // 2. ДЕЛЕГИРОВАНИЕ СОБЫТИЯ КЛИКА ПО ВСЕЙ СТРАНИЦЕ ПРЕДПРОСМОТРА
        // =============================================================
        previewContainer.addEventListener('click', function(event) {
            // Ищем ближайший родительский элемент с классом .clickable-block-wrapper,
            // начиная от места, где произошел клик.
            const clickedWrapper = event.target.closest('.clickable-block-wrapper');
            
            // Если клик был совершен внутри обертки блока
            if (clickedWrapper) {
                // Извлекаем ID блока из data-атрибута обертки
                const blockIdString = clickedWrapper.getAttribute('data-block-id');
                
                if (blockIdString) {
                    // Преобразуем ID в целое число
                    const blockId = parseInt(blockIdString, 10);
                    
                    // Находим конкретный блок в массиве blocksData по этому ID
                    const targetBlockData = blocksData.find(function(block) {
                        return block.id === blockId;
                    });
                    
                    // Если блок найден, открываем модальное окно
                    if (targetBlockData) {
                        openBlockInspectorModal(targetBlockData);
                    } else {
                        console.warn('Блок с ID ' + blockId + ' не найден в массиве данных.');
                    }
                }
            }
        });

        // =============================================================
        // 3. ФУНКЦИЯ ОТКРЫТИЯ МОДАЛЬНОГО ОКНА С КОДОМ
        // =============================================================
        function openBlockInspectorModal(blockData) {
            // Запоминаем ID текущего открытого блока
            currentOpenBlockId = blockData.id;
            
            // Обновляем заголовок окна
            modalTitleElement.textContent = blockData.name + ' (ID: ' + blockData.id + ')';
            
            // Вставляем сырой HTML-код в тег <pre>
            modalCodeViewer.textContent = blockData.html;
            
            // Добавляем класс .active к оверлею, чтобы он появился с анимацией
            modalOverlay.classList.add('active');
            
            // Блокируем прокрутку основного окна сзади модалки
            document.body.style.overflow = 'hidden';
        }

        // =============================================================
        // 4. ФУНКЦИЯ ЗАКРЫТИЯ МОДАЛЬНОГО ОКНА
        // =============================================================
        function closeBlockInspectorModal() {
            // Убираем активный класс
            modalOverlay.classList.remove('active');
            
            // Возвращаем возможность прокрутки основному окну
            document.body.style.overflow = '';
            
            // Сбрасываем ID текущего блока
            currentOpenBlockId = null;
        }

        // =============================================================
        // 5. ОБРАБОТЧИКИ СОБЫТИЙ ДЛЯ ЗАКРЫТИЯ МОДАЛКИ
        // =============================================================
        
        // Кнопка закрытия "Крестик"
        document.getElementById('modal-close-btn').addEventListener('click', closeBlockInspectorModal);
        
        // Кнопка закрытия "Закрыть" в подвале
        document.getElementById('modal-close-btn-2').addEventListener('click', closeBlockInspectorModal);
        
        // Клик по пустому фону (затемненному оверлею) вне модалки
        modalOverlay.addEventListener('click', function(event) {
            // Проверяем, что клик был именно по оверлею, а не по внутреннему контенту
            if (event.target === modalOverlay) {
                closeBlockInspectorModal();
            }
        });
        
        // Нажатие клавиши Escape на клавиатуре
        document.addEventListener('keydown', function(event) {
            // Если нажали Escape и модалка в данный момент открыта
            if (event.key === 'Escape' && modalOverlay.classList.contains('active')) {
                closeBlockInspectorModal();
            }
        });

        // =============================================================
        // 6. ОБРАБОТЧИК КНОПКИ "КОПИРОВАТЬ КОД"
        // =============================================================
        document.getElementById('action-copy-clipboard').addEventListener('click', function() {
            // Берем текст, который сейчас отображается в теге <pre>
            const codeString = modalCodeViewer.textContent;
            
            // Пытаемся использовать современный Clipboard API
            if (navigator.clipboard) {
                navigator.clipboard.writeText(codeString).then(function() {
                    showToastNotification('✅ Код успешно скопирован в буфер обмена!');
                }).catch(function(error) {
                    console.error('Ошибка Clipboard API:', error);
                    // Если промис упал, пробуем старый способ копирования
                    fallbackCopyMethod(codeString);
                });
            } else {
                // Если браузер старый, сразу используем резервный метод
                fallbackCopyMethod(codeString);
            }
        });

        // =============================================================
        // 7. ЗАПАСНОЙ МЕТОД КОПИРОВАНИЯ (ДЛЯ СТАРЫХ БРАУЗЕРОВ)
        // =============================================================
        function fallbackCopyMethod(textToCopy) {
            // Создаем временное скрытое текстовое поле
            const temporaryTextarea = document.createElement('textarea');
            temporaryTextarea.value = textToCopy;
            temporaryTextarea.style.position = 'fixed';
            temporaryTextarea.style.left = '-9999px';
            document.body.appendChild(temporaryTextarea);
            
            // Выделяем текст в этом поле
            temporaryTextarea.select();
            temporaryTextarea.setSelectionRange(0, 99999); // Для мобильных устройств
            
            // Выполняем команду копирования
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    showToastNotification('✅ Код скопирован в буфер обмена!');
                } else {
                    showToastNotification('❌ Не удалось скопировать код.');
                }
            } catch (error) {
                console.error('Ошибка резервного копирования:', error);
                showToastNotification('❌ Ошибка при копировании.');
            }
            
            // Удаляем временное поле из DOM
            document.body.removeChild(temporaryTextarea);
        }

        // =============================================================
        // 8. ОБРАБОТЧИК КНОПКИ "УЛУЧШИТЬ ЧЕРЕЗ ИИ"
        // =============================================================
        document.getElementById('action-improve-ai').addEventListener('click', function() {
            // Проверяем, открыт ли какой-то блок
            if (currentOpenBlockId === null) {
                showToastNotification('⚠️ Сначала выберите блок для улучшения.');
                return;
            }
            
            // Находим данные выбранного блока в массиве
            const targetBlock = blocksData.find(function(block) {
                return block.id === currentOpenBlockId;
            });
            
            if (!targetBlock) {
                showToastNotification('⚠️ Данные блока не найдены.');
                return;
            }
            
            // Отправляем POST-запрос на сервер Flask
            fetch('/action/improve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: targetBlock.id,
                    code: targetBlock.html
                })
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(responseData) {
                // Если сервер ответил успешно, показываем уведомление
                showToastNotification('🚀 ' + (responseData.message || 'Запрос на улучшение отправлен!'));
            })
            .catch(function(error) {
                console.error('Ошибка при отправке на ИИ:', error);
                showToastNotification('❌ Ошибка соединения с модулем улучшения ИИ. Проверьте логи сервера.');
            });
        });

        // =============================================================
        // 9. ОБРАБОТЧИК КНОПКИ "ОТПРАВИТЬ В CHATGPT"
        // =============================================================
        document.getElementById('action-chatgpt').addEventListener('click', function() {
            // Проверяем, открыт ли какой-то блок
            if (currentOpenBlockId === null) {
                showToastNotification('⚠️ Сначала выберите блок для отправки.');
                return;
            }
            
            // Находим данные выбранного блока
            const targetBlock = blocksData.find(function(block) {
                return block.id === currentOpenBlockId;
            });
            
            if (!targetBlock) {
                showToastNotification('⚠️ Данные блока не найдены.');
                return;
            }
            
            // Отправляем POST-запрос на сервер Flask
            fetch('/action/chatgpt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: targetBlock.id,
                    code: targetBlock.html
                })
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(responseData) {
                // Если сервер ответил успешно, показываем уведомление
                showToastNotification('📤 ' + (responseData.message || 'Блок отправлен в ChatGPT!'));
            })
            .catch(function(error) {
                console.error('Ошибка при отправке в ChatGPT:', error);
                showToastNotification('❌ Ошибка отправки в ChatGPT. Проверьте логи сервера.');
            });
        });

        // =============================================================
        // 10. ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ TOAST-УВЕДОМЛЕНИЙ
        // =============================================================
        function showToastNotification(messageText) {
            // Вставляем текст в элемент уведомления
            toastMessage.textContent = messageText;
            
            // Добавляем класс .visible, чтобы он появился с анимацией
            toastMessage.classList.add('visible');
            
            // Автоматически скрываем уведомление через 3 секунды
            setTimeout(function() {
                toastMessage.classList.remove('visible');
            }, 3000);
        }

    </script>
</body>
</html>
"""


# =====================================================================
# 5. ОБРАБОТЧИКИ МАРШРУТОВ FLASK
# =====================================================================

@app.route('/')
def main_page_controller():
    """
    Главный маршрут. Загружает HTML-файл, парсит его, 
    оборачивает блоки и рендерит страницу.
    """
    try:
        # Пытаемся открыть и прочитать указанный пользователем файл
        with open(INPUT_HTML_FILE, 'r', encoding='utf-8') as html_file_handle:
            raw_html_string = html_file_handle.read()
            
        # Передаем содержимое файла в нашу функцию парсинга и обертки
        final_processed_html, blocks_database = parse_and_wrap_html_blocks(raw_html_string)
        
        # Преобразуем Python-список блоков в строку JSON
        blocks_json_string = json.dumps(blocks_database)
        
        # Подставляем HTML и JSON в наш главный шаблон
        final_page_content = FULL_HTML_INTERFACE_TEMPLATE.replace(
            '{{ GENERATED_HTML | safe }}', final_processed_html
        ).replace(
            '{{ BLOCKS_JSON | safe }}', blocks_json_string
        )
        
        # Возвращаем сгенерированную страницу клиенту
        return final_page_content
        
    except FileNotFoundError:
        # Если файл не найден, возвращаем HTML с ошибкой
        error_message = f"""
        <div style="padding: 40px; font-family: sans-serif; max-width: 800px; margin: 0 auto;">
            <h1 style="color: #dc2626;">❌ Файл не найден</h1>
            <p style="font-size: 18px;">Скрипт не может найти HTML-файл по указанному пути:</p>
            <pre style="background: #f3f4f6; padding: 15px; border-radius: 8px; font-weight: bold;">{os.path.abspath(INPUT_HTML_FILE)}</pre>
            <p>Чтобы исправить это:</p>
            <ul>
                <li>Переименуйте ваш монолитный HTML-файл в <b>upload.html</b> и положите его рядом со скриптом.</li>
                <li>Либо передайте путь к файлу при запуске: <code>python inspector_full.py путь_к_файлу.html</code></li>
            </ul>
        </div>
        """
        return error_message, 404


@app.route('/action/improve', methods=['POST'])
def backend_improve_ai_endpoint():
    """
    Эндпоинт для кнопки "Улучшить через ИИ".
    Принимает JSON с ID и кодом блока.
    """
    try:
        incoming_data = request.json
        print(f"\n[СЕРВЕР - УЛУЧШЕНИЕ] Получен запрос на улучшение блока #{incoming_data.get('id')}")
        print(f"[Исходный код]:\n{incoming_data.get('code')[:200]}... (сокращено для лога)")
        print("-" * 40)
        
        # =============================================================
        # ВСТАВЬТЕ СЮДА ВАШУ ЛОГИКУ ВЫЗОВА OpenAI/GPT API.
        # Например: response = openai.ChatCompletion.create(...)
        # =============================================================
        
        # Отправляем успешный заглушечный ответ
        return jsonify({
            'status': 'ok',
            'message': 'ИИ принял код в обработку (Заглушка. Вставьте свой API вызов в функцию backend_improve_ai_endpoint).'
        })
    except Exception as error:
        print(f"[ОШИБКА] {error}")
        return jsonify({'status': 'error', 'message': str(error)}), 500


@app.route('/action/chatgpt', methods=['POST'])
def backend_chatgpt_endpoint():
    """
    Эндпоинт для кнопки "Отправить в ChatGPT".
    Принимает JSON с ID и кодом блока.
    """
    try:
        incoming_data = request.json
        print(f"\n[СЕРВЕР - CHATGPT] Получен запрос на отправку в ChatGPT блока #{incoming_data.get('id')}")
        print(f"[Код для ChatGPT]:\n{incoming_data.get('code')[:200]}... (сокращено для лога)")
        print("-" * 40)
        
        # =============================================================
        # ВСТАВЬТЕ СЮДА ВАШУ ЛОГИКУ ВЫЗОВА ChatGPT API ИЛИ
        # ПЕРЕДАЧИ ДАННЫХ В TELEGRAM, DISCORD ИЛИ ДРУГУЮ СИСТЕМУ.
        # =============================================================
        
        # Отправляем успешный заглушечный ответ
        return jsonify({
            'status': 'ok',
            'message': 'Код передан в ChatGPT (Заглушка. Вставьте свой API вызов в функцию backend_chatgpt_endpoint).'
        })
    except Exception as error:
        print(f"[ОШИБКА] {error}")
        return jsonify({'status': 'error', 'message': str(error)}), 500


# =====================================================================
# 6. ТОЧКА ВХОДА В ПРОГРАММУ (МЕЙН)
# =====================================================================

if __name__ == '__main__':
    
    # Проверяем, существует ли переданный файл прямо сейчас, чтобы дать раннюю ошибку
    if not os.path.exists(INPUT_HTML_FILE):
        print("=" * 70)
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: Файл '{INPUT_HTML_FILE}' не найден.")
        print("Убедитесь, что файл лежит рядом со скриптом, или передайте путь.")
        print("=" * 70)
    else:
        print("=" * 70)
        print("🚀 ИНТЕРАКТИВНЫЙ ИНСПЕКТОР HTML ЗАПУЩЕН")
        print(f"📁 Загружаемый исходный файл: {os.path.abspath(INPUT_HTML_FILE)}")
        print(f"🛠️  Поиск блоков по селектору: '{BLOCK_CSS_SELECTOR}'")
        print("🌐 Откройте интерфейс в браузере: http://127.0.0.1:5000")
        print("💡 Чтобы закрыть сервер, нажмите Ctrl+C в консоли.")
        print("=" * 70)
        
    # Запускаем веб-сервер Flask (debug=True выводит ошибки прямо в консоль)
    app.run(debug=True, host='127.0.0.1', port=5000)
