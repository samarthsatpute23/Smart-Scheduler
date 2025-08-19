// ---- Theme toggle with localStorage ----
(function () {
  const html = document.documentElement;
  const btn = document.getElementById("darkModeBtn");
  const key = "smart-scheduler-theme";

  // init from storage
  const saved = localStorage.getItem(key);
  if (saved === "dark" || saved === "light") {
    html.setAttribute("data-bs-theme", saved);
    if (btn) btn.textContent = saved === "dark" ? "☀️" : "🌙";
  }

  if (btn) {
    btn.addEventListener("click", () => {
      const current = html.getAttribute("data-bs-theme") || "light";
      const next = current === "light" ? "dark" : "light";
      html.setAttribute("data-bs-theme", next);
      localStorage.setItem(key, next);
      btn.textContent = next === "dark" ? "☀️" : "🌙";
    });
  }
})();

// ---- Charts (Chart.js) ----
(function () {
  if (typeof TASKS === "undefined") return;

  // Priority Distribution
  const counts = { 1: 0, 2: 0, 3: 0 };
  TASKS.forEach(t => {
    const p = Number(t.priority) || 1;
    if (counts[p] == null) counts[p] = 0;
    counts[p] += 1;
  });

  const prCanvas = document.getElementById("priorityChart");
  if (prCanvas) {
    new Chart(prCanvas, {
      type: "pie",
      data: {
        labels: ["Low", "Medium", "High"],
        datasets: [{
          data: [counts[1], counts[2], counts[3]]
          // colors are automatic per instructions; no explicit colors
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } }
      }
    });
  }

  // Deadlines bar chart: group by date (YYYY-MM-DD)
  const byDate = {};
  TASKS.forEach(t => {
    const d = (t.deadline || "").slice(0, 10); // assume "YYYY-MM-DD" from <input type="date">
    if (!d) return;
    byDate[d] = (byDate[d] || 0) + 1;
  });

  const dates = Object.keys(byDate).sort();
  const values = dates.map(d => byDate[d]);

  const dlCanvas = document.getElementById("deadlineChart");
  if (dlCanvas) {
    new Chart(dlCanvas, {
      type: "bar",
      data: {
        labels: dates,
        datasets: [{
          label: "Tasks due",
          data: values
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: { ticks: { autoSkip: true, maxRotation: 0 } },
          y: { beginAtZero: true, precision: 0 }
        },
        plugins: { legend: { display: false } }
      }
    });
  }
})();
