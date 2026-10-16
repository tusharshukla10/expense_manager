
 // ==========================================
 // CONFIGURATION
 // ==========================================

const API_URL = "http://127.0.0.1:5000";
let allExpenses = [];
let USER_ID = Number(sessionStorage.getItem("userId")) || null;


// ==========================================
// REGISTRATION
// ==========================================

const form = document.getElementById("registerForm");
const message = document.getElementById("message");

if (form) {
    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const userData = {
            username: document.getElementById("username").value.trim(),
            email: document.getElementById("email").value.trim(),
            password: document.getElementById("password").value
        };

        try {
            const response = await fetch(`${API_URL}/api/v1/register`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "same-origin",
                body: JSON.stringify(userData)
            });

            const result = await readResponse(response);

            sessionStorage.setItem("userId", data.user.id);
            USER_ID = Number(result.user.id);

            message.textContent =
                "Registration successful! Opening Expense Manager...";
            //sessionStorage.setItem("userId", data.user.id);
            window.location.href = "/";
        } catch (error) {
            message.textContent = error.message ||
                "Could not connect to the backend. Check whether Flask is running.";
        }
    });
}

// ==========================================
// LOGIN FORM
// ==========================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const email = document.getElementById("loginEmail").value.trim();
        const password = document.getElementById("loginPassword").value;
        const message = document.getElementById("loginMessage");

        message.textContent = "Logging in...";

        try {
            const response = await fetch("/api/v1/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "same-origin",
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                message.textContent =
                    data.error || "Login failed. Please try again.";
                return;
            }

            // Save the ID for your existing dashboard JavaScript.
            sessionStorage.setItem("userId", data.user.id);

            // Flask session is now authenticated.
            window.location.href = "/";

        } catch (error) {
            console.error("Login error:", error);
            message.textContent =
                "Unable to connect to the server. Please try again.";
        }
    });
}


// ==========================================
// HELPER: SHOW MESSAGE
// ==========================================

function showMessage(messageText) {
    alert(messageText);

}

// ==========================================
// LOGOUT
// ==========================================


const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        try {
            const response = await fetch("/api/v1/logout", {
                method: "POST",
                credentials: "same-origin"
            });

            if (response.ok) {
                sessionStorage.removeItem("userId");
                window.location.href = "/login.html";
            } else {
                alert("Logout failed. Please try again.");
            }
        } catch (error) {
            console.error("Logout error:", error);
            alert("Unable to logout. Check your connection.");
        }
    });
}





// ==========================================
// HELPER: API RESPONSE
// ==========================================

async function readResponse(response) {
    let result;

    try {
        result = await response.json();
    } catch {
        throw new Error("The server returned an invalid response.");
    }

    if (!response.ok) {
        throw new Error(
            result.error || result.message || "Request failed"
        );
    }

    return result;
}


// ==========================================
// LOAD EXPENSES
// ==========================================

async function loadExpenses() {
    if (!document.getElementById("expenseList")) {
        return;
    }

    if (!USER_ID) {
        window.location.href = "/register.html";
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/api/v1/users/${USER_ID}/expenses`,
            { credentials: "same-origin" }
        );

        allExpenses = await readResponse(response);

        updateCategoryFilter();
        filterExpenses();
        updateSummary(allExpenses);
        updateQuickStats(allExpenses);
    } catch (error) {
        console.error("Load expenses error:", error);
        showMessage(`Could not load expenses: ${error.message}`);
    }
}


// ==========================================
// DISPLAY EXPENSES
// ==========================================

function displayExpenses(expenses) {
    const expenseList = document.getElementById("expenseList");

    if (!expenseList) return;

    expenseList.innerHTML = "";

    if (expenses.length === 0) {
        expenseList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🧾</div>
                <h3>No expenses found</h3>
                <p>Add an expense to get started.</p>
            </div>
        `;
        return;
    }

    for (const expense of expenses) {
        const div = document.createElement("div");
        div.className = "expense-item";

        const info = document.createElement("div");
        info.className = "expense-info";

        const title = document.createElement("strong");
        title.className = "expense-title";
        title.textContent = expense.title;

        const amount = document.createElement("span");
        amount.className = "expense-amount";
        amount.textContent =
            `₹${Number(expense.amount).toLocaleString("en-IN")}`;

        const category = document.createElement("small");
        category.className = "expense-category";
        category.textContent = expense.category;

        info.append(title, amount, category);

        const actions = document.createElement("div");
        actions.className = "expense-actions";

        const editButton = document.createElement("button");
        editButton.className = "edit-btn";
        editButton.textContent = "Edit";
        editButton.addEventListener("click", () => {
            editExpense(expense.id);
        });

        const deleteButton = document.createElement("button");
        deleteButton.className = "delete-btn";
        deleteButton.textContent = "Delete";
        deleteButton.addEventListener("click", () => {
            deleteExpense(expense.id);
        });

        actions.append(editButton, deleteButton);
        div.append(info, actions);
        expenseList.appendChild(div);
    }
}


// ==========================================
// ADD EXPENSE
// ==========================================

const expenseForm = document.getElementById("expenseForm");

if (expenseForm) {
    expenseForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const title = document.getElementById("title").value.trim();
        const amount = Number(document.getElementById("amount").value);
        const category = document.getElementById("category").value.trim();

        if (!title || !category || !Number.isFinite(amount) || amount <= 0) {
            showMessage("Enter a valid title, category, and positive amount.");
            return;
        }

        try {
            const response = await fetch(`${API_URL}/api/v1/expenses`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "same-origin",
                body: JSON.stringify({ title, amount, category })
            });

            const result = await readResponse(response);

            showMessage(result.message || "Expense added successfully.");
            this.reset();

            await loadExpenses();
        } catch (error) {
            console.error("Add expense error:", error);
            showMessage(`Could not add expense: ${error.message}`);
        }
    });
}


// ==========================================
// DELETE EXPENSE
// ==========================================

async function deleteExpense(expenseId) {
    const expense = allExpenses.find(
        item => item.id === expenseId
    );

    if (!expense) {
        showMessage("Expense not found.");
        return;
    }

    if (!confirm(`Delete "${expense.title}"?`)) return;

    try {
        const response = await fetch(
            `${API_URL}/api/v1/expenses/${expenseId}`,
            {
                method: "DELETE",
                credentials: "same-origin"
            }
        );

        const result = await readResponse(response);

        showMessage(result.message || "Expense deleted successfully.");
        await loadExpenses();
    } catch (error) {
        console.error("Delete expense error:", error);
        showMessage(`Could not delete expense: ${error.message}`);
    }
}


// ==========================================
// EDIT EXPENSE
// ==========================================

async function editExpense(expenseId) {
    const expense = allExpenses.find(
        item => item.id === expenseId
    );

    if (!expense) {
        showMessage("Expense not found.");
        return;
    }

    const newTitle = prompt("Enter expense title:", expense.title);
    if (newTitle === null) return;

    const newAmount = prompt("Enter expense amount:", expense.amount);
    if (newAmount === null) return;

    const newCategory = prompt(
        "Enter expense category:",
        expense.category
    );
    if (newCategory === null) return;

    const title = newTitle.trim();
    const category = newCategory.trim();
    const amount = Number(newAmount);

    if (!title || !category || !Number.isFinite(amount) || amount <= 0) {
        showMessage("Enter a valid title, category, and positive amount.");
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/api/v1/expenses/${expenseId}`,
            {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                credentials: "same-origin",
                body: JSON.stringify({ title, amount, category })
            }
        );

        const result = await readResponse(response);

        showMessage(result.message || "Expense updated successfully.");
        await loadExpenses();
    } catch (error) {
        console.error("Update expense error:", error);
        showMessage(`Could not update expense: ${error.message}`);
    }
}


// ==========================================
// SEARCH AND CATEGORY FILTER
// ==========================================

const searchInput = document.getElementById("searchExpense");

if (searchInput) {
    searchInput.addEventListener("input", filterExpenses);
}

const categoryFilter = document.getElementById("categoryFilter");

if (categoryFilter) {
    categoryFilter.addEventListener("change", filterExpenses);
}

function filterExpenses() {
    const searchText = (
        document.getElementById("searchExpense")?.value || ""
    ).toLowerCase().trim();

    const selectedCategory =
        document.getElementById("categoryFilter")?.value || "all";

    const filtered = allExpenses.filter(expense => {
        const matchesSearch = String(expense.title || "")
            .toLowerCase()
            .includes(searchText);

        const matchesCategory =
            selectedCategory === "all" ||
            expense.category === selectedCategory;

        return matchesSearch && matchesCategory;
    });

    displayExpenses(filtered);
}


// ==========================================
// UPDATE CATEGORY DROPDOWN
// ==========================================

function updateCategoryFilter() {
    const select = document.getElementById("categoryFilter");

    if (!select) return;

    const currentValue = select.value;
    select.innerHTML = "";

    const allOption = document.createElement("option");
    allOption.value = "all";
    allOption.textContent = "All Categories";
    select.appendChild(allOption);

    const categories = [
        ...new Set(
            allExpenses
                .map(expense => expense.category)
                .filter(Boolean)
        )
    ];

    categories.sort((a, b) => a.localeCompare(b));

    for (const category of categories) {
        const option = document.createElement("option");
        option.value = category;
        option.textContent = category;
        select.appendChild(option);
    }

    select.value = categories.includes(currentValue)
        ? currentValue
        : "all";
}


// ==========================================
// SUMMARY CARDS
// ==========================================

function updateSummary(expenses) {
    let total = 0;
    const categories = new Set();

    for (const expense of expenses) {
        total += Number(expense.amount) || 0;

        if (expense.category) {
            categories.add(expense.category);
        }
    }

    const totalElement = document.getElementById("totalAmount");
    const countElement = document.getElementById("expenseCount");
    const categoryElement = document.getElementById("categoryCount");

    if (totalElement) {
        totalElement.textContent =
            `₹${total.toLocaleString("en-IN")}`;
    }

    if (countElement) {
        countElement.textContent = expenses.length;
    }

    if (categoryElement) {
        categoryElement.textContent = categories.size;
    }
}


// ==========================================
// SPENDING OVERVIEW
// ==========================================

function updateQuickStats(expenses) {
    const totals = {
        food: 0,
        travel: 0,
        shopping: 0,
        other: 0
    };

    for (const expense of expenses) {
        const category = String(expense.category || "")
            .trim()
            .toLowerCase();

        const amount = Number(expense.amount) || 0;

        if (category === "food") {
            totals.food += amount;
        } else if (category === "travel") {
            totals.travel += amount;
        } else if (category === "shopping") {
            totals.shopping += amount;
        } else {
            totals.other += amount;
        }
    }

    const elements = {
        foodTotal: totals.food,
        travelTotal: totals.travel,
        shoppingTotal: totals.shopping,
        otherTotal: totals.other
    };

    for (const [id, amount] of Object.entries(elements)) {
        const element = document.getElementById(id);

        if (element) {
            element.textContent =
                `₹${amount.toLocaleString("en-IN")}`;
        }
    }
}


// ==========================================
// START APPLICATION
// ==========================================

document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("expenseList")) {
        loadExpenses();
    }
});
