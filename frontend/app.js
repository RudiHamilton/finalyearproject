const API_BASE_URL = "/api";

const loginSection = document.getElementById("login-section");
const dashboardSection = document.getElementById("dashboard-section");

const employeeInput = document.getElementById("employee-number");
const loginButton = document.getElementById("login-button");
const logoutButton = document.getElementById("logout-button");
const employeeDisplay = document.getElementById("employee-display");

const barcodeInput = document.getElementById("barcode-input");
const scanButton = document.getElementById("scan-button");
const optimiseButton = document.getElementById("optimise-button");
const googleMapsButton = document.getElementById("google-maps-button");

const selectedRouteBody = document.getElementById("selected-route-body");
const routePreview = document.getElementById("route-preview");
const statusMessage = document.getElementById("status-message");

const selectedDeliveries = [];
let optimisedRoute = [];

loginButton.addEventListener("click", loginEmployee);

employeeInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        loginEmployee();
    }
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
    employeeInput.focus();
});

scanButton.addEventListener("click", addDeliveryByBarcode);

barcodeInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        addDeliveryByBarcode();
    }
});

optimiseButton.addEventListener("click", optimiseSelectedRoute);

if (googleMapsButton) {
    googleMapsButton.addEventListener("click", () => {
        if (!optimisedRoute || optimisedRoute.length === 0) {
            showStatus("Optimise a route before opening Google Maps.", "error");
            return;
        }

        openRouteInGoogleMaps(optimisedRoute);
    });
} else {
    console.error("Google Maps button not found in HTML.");
}

async function optimiseSelectedRoute() {
    if (selectedDeliveries.length === 0) {
        showStatus("No deliveries selected to optimise.", "error");
        return;
    }

    showStatus("Optimising route...", "success");

    try {
        const response = await fetch(`${API_BASE_URL}/deliveries/optimise`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                deliveries: selectedDeliveries,
                method: "auto",
            }),
        });

        const result = await response.json();
        console.log("Full API result:", result); // add here

        if (!response.ok) {
            showStatus(result.error || "Route optimisation failed.", "error");
            console.error(result);
            return;
        }

        optimisedRoute = result.route;
        renderRoutePreview(optimisedRoute);

        if (googleMapsButton) {
            googleMapsButton.classList.remove("hidden");
        } else {
            console.error("Google Maps button not found");
        }

        let comparisonText = "";

        if (result.comparison && Object.keys(result.comparison).length > 0) {
            comparisonText = ` NN+2opt: ${result.comparison.nn_two_opt_distance_km} km. ML+2opt: ${result.comparison.ml_two_opt_distance_km} km.`;
        }

        showStatus(
            `Selected ${result.selected_method}. Distance: ${result.total_distance_km} km. Runtime: ${result.runtime_ms} ms.${comparisonText}`,
            "success"
        );

    } catch (error) {
        console.error(error);
        showStatus("Could not connect to route optimisation API.", "error");
    }
}

async function loginEmployee() {
    console.log("REAL DATABASE LOGIN FUNCTION RUNNING");
    const employeeNumber = employeeInput.value.trim();

    if (!employeeNumber) {
        showStatus("Enter an employee number first.", "error");
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/employees/${encodeURIComponent(employeeNumber)}`
        );

        if (!response.ok) {
            showStatus("Employee number not recognised.", "error");
            return;
        }

        const employee = await response.json();

        loginSection.classList.add("hidden");
        dashboardSection.classList.remove("hidden");

        employeeDisplay.textContent = `Active employee: ${employee.full_name} (${employee.employee_number})`;

        statusMessage.textContent = "";
        barcodeInput.focus();

    } catch (error) {
        console.error(error);
        showStatus("Could not connect to employee API.", "error");
    }
}

async function addDeliveryByBarcode() {
    const barcode = barcodeInput.value.trim();

    if (!barcode) {
        showStatus("Scan or enter a barcode.", "error");
        return;
    }

    let delivery;

    try {
        const response = await fetch(
            `${API_BASE_URL}/deliveries/barcode/${encodeURIComponent(barcode)}`
        );

        if (!response.ok) {
            showStatus("No delivery found for that barcode.", "error");
            return;
        }

        delivery = await response.json();

    } catch (error) {
        console.error(error);
        showStatus("Could not connect to delivery API.", "error");
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
    console.log("renderRoutePreview called", route);
    console.log("routePreview element", routePreview);
    routePreview.innerHTML = "";

    if (!route || route.length === 0) {
        routePreview.innerHTML = "<li>No route generated yet.</li>";
        return;
    }

    route.forEach((delivery) => {
        const item = document.createElement("li");

        const position = delivery.route_position || "";
        const customer = delivery.customer_name || "Unknown customer";
        const city = delivery.city || "Unknown town";
        const postcode = delivery.postcode || "";
        const barcode = delivery.barcode || "";

       item.textContent = `${customer} - ${city} ${postcode} (${barcode})`;

        routePreview.appendChild(item);
    });
}

function openRouteInGoogleMaps(route) {
    const locations = route.map(stop => {
        if (stop.latitude && stop.longitude) {
            return `${stop.latitude},${stop.longitude}`;
        }

        const locationText = `${stop.city || ""} ${stop.postcode || ""} Northern Ireland`;
        return encodeURIComponent(locationText.trim());
    });

    const url = `https://www.google.com/maps/dir/${locations.join("/")}`;

    console.log("Opening Google Maps URL:", url);

    window.open(url, "_blank");
}

function showStatus(message, type) {
    statusMessage.textContent = message;

    if (type === "success") {
        statusMessage.style.color = "#15803d";
    } else {
        statusMessage.style.color = "#b91c1c";
    }
}