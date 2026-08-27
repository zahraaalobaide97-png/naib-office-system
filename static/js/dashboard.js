document.addEventListener("DOMContentLoaded", function () {
    var dataEl = document.getElementById("dashboard-data");
    if (!dataEl) return;
    var data = JSON.parse(dataEl.textContent);

    new Chart(document.getElementById("statusChart"), {
        type: "bar",
        data: {
            labels: data.statusLabels,
            datasets: [{ label: "عدد الطلبات", data: data.statusValues, backgroundColor: "#0f2d4d" }],
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } },
    });

    new Chart(document.getElementById("typeChart"), {
        type: "doughnut",
        data: {
            labels: data.typeLabels,
            datasets: [{ data: data.typeValues, backgroundColor: ["#0f2d4d", "#a67c27", "#2f6f4e"] }],
        },
        options: { responsive: true, maintainAspectRatio: false },
    });
});
