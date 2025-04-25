// Simple SPA logic for PurchaseTracker web frontend
const API_BASE = "http://localhost:8000";
let accessToken = null;

function showSection(sectionId) {
    document.getElementById("login-section").style.display = sectionId === "login" ? "block" : "none";
    document.getElementById("dashboard-section").style.display = sectionId === "dashboard" ? "block" : "none";
    document.getElementById("nav-login").style.display = sectionId === "login" ? "inline-block" : "none";
    document.getElementById("nav-dashboard").style.display = sectionId === "dashboard" ? "inline-block" : "none";
    document.getElementById("nav-logout").style.display = sectionId === "dashboard" ? "inline-block" : "none";
}

async function login(username, password) {
    const form = new FormData();
    form.append("username", username);
    form.append("password", password);
    const res = await fetch(`${API_BASE}/token`, {
        method: "POST",
        body: form
    });
    if (!res.ok) {
        throw new Error("Invalid username or password");
    }
    const data = await res.json();
    accessToken = data.access_token;
}

async function fetchCategories() {
    const res = await fetch(`${API_BASE}/categories/`, {
        headers: { Authorization: `Bearer ${accessToken}` }
    });
    if (!res.ok) return [];
    return await res.json();
}

async function fetchPurchases() {
    const res = await fetch(`${API_BASE}/purchases/`, {
        headers: { Authorization: `Bearer ${accessToken}` }
    });
    if (!res.ok) return [];
    return await res.json();
}

async function addPurchase(purchase) {
    const res = await fetch(`${API_BASE}/purchases/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`
        },
        body: JSON.stringify(purchase)
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to add purchase");
    }
    return await res.json();
}

function renderCategories(categories) {
    const select = document.getElementById("category");
    select.innerHTML = "";
    categories.forEach(cat => {
        const opt = document.createElement("option");
        opt.value = cat.id;
        opt.textContent = cat.name;
        select.appendChild(opt);
    });
}

function renderPurchases(purchases) {
    const tbody = document.querySelector("#purchases-table tbody");
    tbody.innerHTML = "";
    purchases.forEach(p => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${p.date ? p.date.split("T")[0] : ""}</td>
            <td>${p.description}</td>
            <td>${p.amount.toFixed(2)}</td>
            <td>${p.category_name || "Uncategorized"}</td>
        `;
        tbody.appendChild(tr);
    });
}

document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    document.getElementById("login-error").textContent = "";
    try {
        await login(username, password);
        showSection("dashboard");
        await loadDashboard();
    } catch (err) {
        document.getElementById("login-error").textContent = err.message;
    }
});

document.getElementById("purchase-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const amount = parseFloat(document.getElementById("amount").value);
    const description = document.getElementById("description").value;
    const date = document.getElementById("date").value;
    const category_id = parseInt(document.getElementById("category").value);
    document.getElementById("purchase-error").textContent = "";
    try {
        await addPurchase({ amount, description, date, category_id });
        await loadPurchases();
        document.getElementById("purchase-form").reset();
    } catch (err) {
        document.getElementById("purchase-error").textContent = err.message;
    }
});

document.getElementById("nav-login").onclick = () => showSection("login");
document.getElementById("nav-dashboard").onclick = async () => {
    showSection("dashboard");
    await loadDashboard();
};
document.getElementById("nav-logout").onclick = () => {
    accessToken = null;
    showSection("login");
};

async function loadDashboard() {
    const [categories, purchases] = await Promise.all([
        fetchCategories(),
        fetchPurchases()
    ]);
    renderCategories(categories);
    renderPurchases(purchases);
}

async function loadPurchases() {
    const purchases = await fetchPurchases();
    renderPurchases(purchases);
}

// On load, show login
showSection("login");
