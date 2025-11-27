export function renderCharts(game) {
    const chartArea = document.getElementById("chart");
    chartArea.innerHTML = `
        <h3>${game.home} vs ${game.away}</h3>
        <canvas id="chartCanvas" width="400" height="200"></canvas>
    `;

    const ctx = document.getElementById("chartCanvas").getContext("2d");

    const isDark = document.getElementById("theme-style").href.includes("dark");

    const textColor = isDark ? "#e6edf3" : "#000000";
    const gridColor = isDark ? "#30363d" : "#d5d5d5";

    const labels = ["Win % Home", "Win % Away", "Expected Diff"];
    const values = [
        (game.win_prob_home * 100).toFixed(1),
        (game.win_prob_away * 100).toFixed(1),
        game.expected_diff.toFixed(1)
    ];

    if (window.currentChart) window.currentChart.destroy();

    window.currentChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Model Output",
                data: values,
                backgroundColor: [
                    "#4caf50",
                    "#f44336",
                    "#2196f3"
                ]
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: textColor },
                    grid: { color: gridColor }
                },
                x: {
                    ticks: { color: textColor },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: {
                    labels: { color: textColor }
                }
            }
        }
    });
}
