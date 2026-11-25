document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const errorMessage = document.getElementById('error-message');

  loginForm.addEventListener('submit', async (e) => {
    // 1. Prevent the browser from refreshing the page
    e.preventDefault();

    // 2. Gather the data
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
      // 3. Send the POST request to FastAPI
      // Note: FastAPI's default OAuth2 expects standard JSON or FormData. 
      // We use JSON here. Your FastAPI route must accept a JSON body.
      const response = await fetch('/admin/verify_login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        throw new Error("Invalid credentials");
      }

      const data = await response.json();

      // 4. Store the token securely in the current tab's session
      // (It deletes automatically when the tab is closed)
      sessionStorage.setItem('admin_token', data.access_token);

      // 5. Redirect the user to the admin HTML page
      window.location.href = '/admin';  //should it be admin.html or just admin

    } catch (error) {
      // Show the hidden error message from your HTML
      errorMessage.style.display = 'block';
      errorMessage.innerText = "Login failed. Please check your credentials.";
      console.error("Login Error:", error);
    }
  });
});