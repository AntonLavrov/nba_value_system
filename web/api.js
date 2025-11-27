export async function loadData() {
    const response = await fetch("outputs/value_today.json");
    return await response.json();
}
