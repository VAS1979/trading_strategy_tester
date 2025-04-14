// scripts.js

// Словарь для перевода ключей на русский язык
const translations = {
    "start_date": "Дата начала",
    "end_date": "Дата окончания",
    "initial_cache": "Начальный капитал",
    "buy_price": "Цена покупки",
    "sell_price": "Цена продажи",
    "buy_count": "Количество покупок",
    "sell_count": "Количество продаж",
    "comission_percent": "Комиссия (%)",
    "tax_percent": "Налог (%)",
    "invest_period_days": "Период инвестирования (дни)",
    "invest_period_years": "Период инвестирования (годы)",
    "total_income_sum": "Общий доход (сумма)",
    "total_income_perc": "Общий доход (%)",
    "incom_year_sum": "Доход в год (сумма)",
    "incom_year_pers": "Доход в год (%)",
    "accumulated_commission": "Накопленная комиссия",
    "final_cache": "Финальная сумма в кэше",
    "final_amount_in_shares": "Финальная сумма в акциях",
    "final_overall_result": "Общий финальный результат",
    "total_tax": "Общий налог"
};

// Обработка формы для запроса данных
document.getElementById('fetch-data-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch('/api/fetch-data', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    alert(data.success ? "Data fetched successfully!" : "Failed to fetch data.");
});

// Обработка формы для генерации отчета
document.getElementById('generate-report-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch('/api/generate-report', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();

    // Очищаем предыдущий вывод
    const reportElement = document.getElementById('report');
    reportElement.innerHTML = '';

    // Создаем таблицу
    const table = document.createElement('table');

    // Добавляем заголовок
    const caption = document.createElement('caption');
    caption.textContent = 'Отчет по торговой стратегии';
    table.appendChild(caption);

    // Добавляем заголовки столбцов
    const headerRow = document.createElement('tr');
    const header1 = document.createElement('th');
    header1.textContent = 'Параметр';
    headerRow.appendChild(header1);

    const header2 = document.createElement('th');
    header2.textContent = 'Значение';
    headerRow.appendChild(header2);

    table.appendChild(headerRow);

    // Добавляем строки таблицы
    for (const [key, value] of Object.entries(data.success)) {
        const row = document.createElement('tr');

        // Название параметра (перевод на русский)
        const keyCell = document.createElement('td');
        keyCell.textContent = translations[key] || key; // Используем перевод или оригинальный ключ
        row.appendChild(keyCell);

        // Значение параметра
        const valueCell = document.createElement('td');
        if (typeof value === 'number') {
            // Для comission_percent используем toFixed(5)
            if (key === 'comission_percent') {
                valueCell.textContent = value.toFixed(5);
            } else {
                // Для остальных чисел используем toLocaleString()
                valueCell.textContent = value.toLocaleString();
            }
        } else {
            // Для нечисловых значений выводим как есть
            valueCell.textContent = value;
        }
        row.appendChild(valueCell);

        table.appendChild(row);
    }

    // Добавляем таблицу в контейнер
    reportElement.appendChild(table);
});

document.getElementById('show-history-btn').addEventListener('click', function() {
    const ticker = document.getElementById('report-ticker').value.trim();
    
    if (!ticker) {
        alert('Пожалуйста, введите тикер');
        return;
    }

    const btn = this;
    btn.disabled = true;
    btn.textContent = 'Загрузка...';

    fetch('/api/show-history', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `ticker=${encodeURIComponent(ticker)}`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Ошибка сети');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const win = window.open('', '_blank');
            win.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>История торгов: ${data.ticker}</title>
                    <link rel="stylesheet" href="styles.css">
                    <style>
                        .trading-results {
                            width: 100%;
                            border-collapse: collapse;
                            margin-top: 10px;
                        }
                        .trading-results th {
                            background-color: #f2f2f2;
                            padding: 10px;
                            text-align: left;
                            position: sticky;
                            top: 0;
                            white-space: normal;
                            height: 60px;
                            vertical-align: bottom;
                        }
                        .trading-results th span {
                            display: inline-block;
                            max-width: 100%;
                            word-break: break-word;
                            line-height: 1.3;
                        }
                        .trading-results td {
                            padding: 8px 10px;
                            border-bottom: 1px solid #ddd;
                        }
                        .numeric {
                            text-align: right;
                            font-family: 'Courier New', monospace;
                        }
                        tr.increase {
                            background-color:rgb(58, 209, 58) !important; /* Светло-зеленый */
                        }
                        tr.decrease {
                            background-color:rgb(228, 71, 71) !important; /* Светло-красный */
                        }
                        tr:hover {
                            background-color: #f5f5f5;
                        }
                    </style>
                </head>
                <body>
                    <h2>Результаты стратегии: ${data.ticker}</h2>
                    <script>
                        function highlightQuantityChanges() {
                            const rows = document.querySelectorAll('.trading-results tr:not(:first-child)');
                            let prevQuantity = null;
                            
                            rows.forEach(row => {
                                const cells = row.querySelectorAll('td');
                                if (cells.length > 4) { // Проверяем, что есть 5-я колонка
                                    const quantityCell = cells[4]; // 5-я колонка с количеством акций
                                    const quantityText = quantityCell.textContent.trim().replace(/\s+/g, '');
                                    const currentQuantity = parseInt(quantityText) || 0;
                                    
                                    if (prevQuantity !== null) {
                                        if (currentQuantity > prevQuantity) {
                                            row.classList.add('increase');
                                        } else if (currentQuantity < prevQuantity) {
                                            row.classList.add('decrease');
                                        }
                                    }
                                    prevQuantity = currentQuantity;
                                }
                            });
                        }
                        
                        document.addEventListener('DOMContentLoaded', highlightQuantityChanges);
                    </script>
                    ${data.html_table.replace(/<th([^>]*)>([^<]*)<\/th>/g, '<th$1><span>$2</span></th>')}
                </body>
                </html>
            `);
            win.document.close();
        } else {
            alert(data.error || 'Не удалось загрузить историю');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при загрузке данных');
    })
    .finally(() => {
        btn.disabled = false;
        btn.textContent = 'Показать историю';
    });
});
