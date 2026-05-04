const loginSection = document.getElementById("login-section");
const dashboardSection = document.getElementById("dashboard-section");

const employeeInput = document.getElementById("employee-number");
const loginButton = document.getElementById("login-button");
const logoutButton = document.getElementById("logout-button");
const employeeDisplay = document.getElementById("employee-display");

const barcodeInput = document.getElementById("barcode-input");
const scanButton = document.getElementById("scan-button");
const optimiseButton = document.getElementById("optimise-button");

const selectedRouteBody = document.getElementById("selected-route-body");
const routePreview = document.getElementById("route-preview");
const statusMessage = document.getElementById("status-message");

const fakeDeliveries = [
    {
        id: 1,
        barcode: "DEL-100001",
        item_description: "Small parcel",
        customer_name: "Jordan Smith",
        city: "Enniskillen",
        postcode: "BT74 5AB",
        latitude: 54.3438,
        longitude: -7.6315
    },
    {
        id: 2,
        barcode: "DEL-100002",
        item_description: "Medium box",
        customer_name: "Megan Brown",
        city: "Lisnaskea",
        postcode: "BT92 1CD",
        latitude: 54.2500,
        longitude: -7.4428
    },
    {
        id: 3,
        barcode: "DEL-100003",
        item_description: "Document envelope",
        customer_name: "Ryan Campbell",
        city: "Irvinestown",
        postcode: "BT94 3EF",
        latitude: 54.4706,
        longitude: -7.6336
    },
    {
        id: 4,
        barcode: "DEL-100004",
        item_description: "Fragile parcel",
        customer_name: "Aoife Kelly",
        city: "Belleek",
        postcode: "BT93 2GH",
        latitude: 54.4793,
        longitude: -8.0895
    }
];

const selectedDeliveries = [];

loginButton.addEventListener("click", () => {
    const employeeNumber = employeeInput.value.trim();

    if (!employeeNumber) {
        showStatus("Enter an employee number first.", "error");
        return;
    }

    loginSection.classList.add("hidden");
    dashboardSection.classList.remove("hidden");

    employeeDisplay.textContent = `Active employee: ${employeeNumber}`;
    barcodeInput.focus();
});

logoutButton.addEventListener("click", () => {
    employeeInput.value = "";
    barcodeInput.value = "";
    selectedDeliveries.length = 0;

    renderSelectedDeliveries();
    renderRoutePreview([]);

    dashboardSection.classList.add("hidden");
    loginSection.classList.remove("hidden");

    statusMessage.textContent = "";
});

scanButton.addEventListener("click", addDeliveryByBarcode);

barcodeInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        addDeliveryByBarcode();
    }
});

optimiseButton.addEventListener("click", () => {
    if (selectedDeliveries.length === 0) {
        showStatus("No deliveries selected to optimise.", "error");
        return;
    }

    const optimisedRoute = [...selectedDeliveries].sort((a, b) =>
        a.city.localeCompare(b.city)
    );

    renderRoutePreview(optimisedRoute);
    showStatus("Route preview generated.", "success");
});

function addDeliveryByBarcode() {
    const barcode = barcodeInput.value.trim().toUpperCase();

    if (!barcode) {
        showStatus("Scan or enter a barcode.", "error");
        return;
    }

    const delivery = fakeDeliveries.find(item => item.barcode === barcode);

    if (!delivery) {
        showStatus("No delivery found for that barcode.", "error");
        return;
    }

    const alreadyAdded = selectedDeliveries.some(item => item.id === delivery.id);

    if (alreadyAdded) {
        showStatus("This delivery is already in the route.", "error");
        return;
    }

    selectedDeliveries.push(delivery);
    renderSelectedDeliveries();

    barcodeInput.value = "";
    barcodeInput.focus();

    showStatus(`Added ${delivery.barcode} to route.`, "success");
}

function renderSelectedDeliveries() {
    selectedRouteBody.innerHTML = "";

    if (selectedDeliveries.length === 0) {
        selectedRouteBody.innerHTML = `
            <tr>
                <td colspan="5">No deliveries scanned yet.</td>
            </tr>
        `;
        return;
    }

    selectedDeliveries.forEach((delivery) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${delivery.barcode}</td>
            <td>${delivery.item_description}</td>
            <td>${delivery.customer_name}</td>
            <td>${delivery.city}</td>
            <td>${delivery.postcode}</td>
        `;

        selectedRouteBody.appendChild(row);
    });
}

function renderRoutePreview(route) {
    routePreview.innerHTML = "";

    if (route.length === 0) {
        routePreview.innerHTML = "<li>No route generated yet.</li>";
        return;
    }

    route.forEach((delivery, index) => {
        const item = document.createElement("li");
        item.textContent = `${index + 1}. ${delivery.customer_name} - ${delivery.city} (${delivery.barcode})`;
        routePreview.appendChild(item);
    });
}

function showStatus(message, type) {
    statusMessage.textContent = message;

    if (type === "success") {
        statusMessage.style.color = "#15803d";
    } else {
        statusMessage.style.color = "#b91c1c";
    }
}