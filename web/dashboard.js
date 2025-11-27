import { renderTable } from "./components/table.js";
import { renderFilters, applyFilters } from "./components/filters.js";
import { renderCharts } from "./components/charts.js";
import { loadData } from "./api.js";

// Глобальные переменные
let originalData = [];
window.lastGame = null;      // нужно для автоматического обновления графиков при смене темы
window.currentChart = null;  // ссылку на текущий график Chart.js

// Основная загрузка
document.addEventListener("DOMContentLoaded", async () => {
    originalData = await loadData();

    // Рендер таблицы
    renderTable(originalData);

    // Рендер фильтров
    renderFilters(originalData);

    // Обработчики фильтрации
    document.getElementById("team-filter").addEventListener("change", () => {
        const filtered = applyFilters(originalData);
        renderTable(filtered);
    });

    document.getElementById("min-edge").addEventListener("input", () => {
        const filtered = applyFilters(originalData);
        renderTable(filtered);
    });
});

// Выбор строки таблицы → построение графиков
export function selectGame(game) {
    window.lastGame = game;    // <--- запоминаем игру для автообновления при смене темы
    renderCharts(game);
}

// -----------------------------------------
// ТЕМА (СВЕТЛАЯ / ТЁМНАЯ)
// -----------------------------------------

window.showCharts = function(index) {
    const game = originalData[index];
    renderCharts(game);
    window.lastGame = game;
};
window.setTheme = function (themeName) {
    const cssFile = "styles/" + themeName + ".css";
    const linkEl = document.getElementById("theme-style");

    linkEl.href = cssFile;

    // Если уже есть открытая игра — перерисовываем график под тему
    if (window.currentChart && window.lastGame) {
        renderCharts(window.lastGame);
    }
};
