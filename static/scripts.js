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
    "final_cache": "Финальный капитал",
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
        valueCell.textContent = typeof value === 'number' ? value.toLocaleString() : value;
        row.appendChild(valueCell);

        table.appendChild(row);
    }

    // Добавляем таблицу в контейнер
    reportElement.appendChild(table);
});