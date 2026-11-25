document.addEventListener("DOMContentLoaded", () => {
    // 1. Navigation Buttons
    document.getElementById("back-btn").addEventListener("click", () => {
        window.history.back(); // Or replace with window.location.href = '/dashboard';
    });

    document.getElementById("logout-btn").addEventListener("click", () => {
        localStorage.removeItem("admin_token"); // Clear the session token
        window.location.href = "/admin/login"; // Redirect to login page
    });

    // 2. Form Submission
    const form = document.getElementById("add-product-form");
    const statusMessage = document.getElementById("status-message");

    form.addEventListener("submit", async (e) => {
        e.preventDefault(); // Stop the page from reloading
        statusMessage.textContent = "Submitting...";
        statusMessage.className = "status-message";

        // Retrieve the token you saved during login
        const token = localStorage.getItem("admin_token"); 

        if (!token) {
            statusMessage.textContent = "Error: Not logged in.";
            statusMessage.className = "status-message error";
            return;
        }

        // Gather all form data into a dictionary
        const formData = {
            name: document.getElementById("name").value,
            gender: document.getElementById("gender").value,
            category: document.getElementById("category").value,
            subcategory: document.getElementById("subcategory").value,
            sub_subcategory: document.getElementById("sub_subcategory").value,
            price: parseFloat(document.getElementById("price").value),
            url: document.getElementById("url").value
        };

        try {
            // Send to your FastAPI endpoint (change URL if your route is different)
            const response = await fetch("/admin/add_product", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}` // Send the session token for verification
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                statusMessage.textContent = "✅ Product added successfully!";
                statusMessage.className = "status-message success";
                form.reset(); // Clear the form
            } else {
                const errorData = await response.json();
                statusMessage.textContent = `❌ Error: ${errorData.detail || "Failed to add product"}`;
                statusMessage.className = "status-message error";
            }
        } catch (error) {
            statusMessage.textContent = `❌ Network error: ${error.message}`;
            statusMessage.className = "status-message error";
        }
    });
});