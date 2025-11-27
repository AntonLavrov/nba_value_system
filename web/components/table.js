export function sortData(data, key) {
    // создаём копию, чтобы не мутировать исходный массив
    const sorted = [...data];

    sorted.sort((a, b) => {
        const va = a[key] ?? 0;
        const vb = b[key] ?? 0;
        if (va < vb) return -1;
        if (va > vb) return 1;
        return 0;
    });

    return sorted;
}

export function renderTable(data) {
    if (!Array.isArray(data)) {
        console.error("renderTable: data is not array", data);
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Match</th>
                    <th class="sortable" onclick="window.sortTableBy('win_prob_home')">Win H%</th>
                    <th class="sortable" onclick="window.sortTableBy('win_prob_away')">Win A%</th>
                    <th class="sortable" onclick="window.sortTableBy('edge_home')">Edge H</th>
                    <th class="sortable" onclick="window.sortTableBy('edge_away')">Edge A</th>
                    <th class="sortable" onclick="window.sortTableBy('P_spread_home_cover')">Spread</th>
                    <th class="sortable" onclick="window.sortTableBy('P_total_over')">Total</th>
                </tr>
            </thead>
            <tbody>
    `;

    for (let i = 0; i < data.length; i++) {
        const g = data[i];

        const winH = (g.win_prob_home * 100).toFixed(1) + "%";
        const winA = (g.win_prob_away * 100).toFixed(1) + "%";

        const edgeH = g.edge_home != null ? g.edge_home.toFixed(1) : "-";
        const edgeA = g.edge_away != null ? g.edge_away.toFixed(1) : "-";

        const spread = g.P_spread_home_cover != null
            ? g.P_spread_home_cover.toFixed(2)
            : "-";

        const total = g.P_total_over != null
            ? g.P_total_over.toFixed(2)
            : "-";

        html += `
            <tr onclick="window.showCharts(${i})" style="cursor:pointer">

                <td>${g.home} - ${g.away}</td>
                <td>${winH}</td>
                <td>${winA}</td>
                <td>${edgeH}</td>
                <td>${edgeA}</td>
                <td>${spread}</td>
                <td>${total}</td>
            </tr>
        `;
    }

    html += "</tbody></table>";

    const el = document.getElementById("table-area");
    if (el) {
        el.innerHTML = html;
    } else {
        console.error("Element #table-area not found");
    }
}
