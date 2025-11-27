// components/filters.js

// Список команд
export function extractTeams(data) {
    const set = new Set();
    data.forEach(g => {
        if (g.home) set.add(g.home);
        if (g.away) set.add(g.away);
    });
    return Array.from(set);
}

// Отрисовка фильтров
export function renderFilters(teams, onChange) {
    const container = document.getElementById("filters");
    container.innerHTML = "";

    const panel = document.createElement("div");
    panel.className = "filter-panel";

    // TEAM SELECTOR
    const teamLabel = document.createElement("label");
    teamLabel.textContent = "Team: ";

    const teamSelect = document.createElement("select");
    teamSelect.id = "team-filter";

    const all = document.createElement("option");
    all.value = "All";
    all.textContent = "All";
    teamSelect.appendChild(all);

    teams.forEach(t => {
        const op = document.createElement("option");
        op.value = t;
        op.textContent = t;
        teamSelect.appendChild(op);
    });

    // EDGE SELECTOR
    const edgeLabel = document.createElement("label");
    edgeLabel.textContent = "Min edge (abs): ";

    const edgeInput = document.createElement("input");
    edgeInput.type = "number";
    edgeInput.id = "min-edge";
    edgeInput.value = 0;
    edgeInput.min = 0;

    // Обработчики
    teamSelect.addEventListener("change", onChange);
    edgeInput.addEventListener("input", onChange);

    // Добавляем элементы
    panel.appendChild(teamLabel);
    panel.appendChild(teamSelect);
    panel.appendChild(edgeLabel);
    panel.appendChild(edgeInput);

    container.appendChild(panel);
}

// Применение фильтров
export function applyFilters(data) {
    const team = document.getElementById("team-filter").value;
    const minEdge = Number(document.getElementById("min-edge").value);

    return data.filter(g => {
        let ok = true;

        if (team !== "All") {
            ok = ok && (g.home === team || g.away === team);
        }

        const edge = Math.max(
            Math.abs(g.edge_home ?? 0),
            Math.abs(g.edge_away ?? 0)
        );

        ok = ok && edge >= minEdge;

        return ok;
    });
}
