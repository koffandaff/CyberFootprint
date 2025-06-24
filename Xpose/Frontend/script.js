document.getElementById("Xpose").addEventListener("submit", async function(event) {
  event.preventDefault();
  
  // UI Feedback - Disable button and show spinner
  const submitBtn = document.getElementById("submitBtn");
  const spinner = document.getElementById("spinner");
  submitBtn.disabled = true;
  spinner.style.display = "inline";
  
  try {
    // 1. Collect Form Data
    const formData = {
      email: document.getElementById("email").value.trim(),
      fullName: document.getElementById("fullName").value.trim(),
      domain: document.getElementById("domain").value.trim(),
      dob: document.getElementById("dob").value,
      platforms: Array.from(document.getElementById("platforms").selectedOptions)
                    .map(option => option.value),
      // Security Practices
      publicProfiles: document.getElementById("publicProfiles").checked,
      reusedPasswords: document.getElementById("reusedPasswords").checked,
      twoFactorAuth: document.getElementById("twoFactorAuth").checked,
      passwordManager: document.getElementById("passwordManager").checked,
      dataBreachExposure: document.getElementById("dataBreachExposure").checked,
      // Online Behavior
      geoTagging: document.getElementById("geoTagging").checked,
      personalInfoPosts: document.getElementById("personalInfoPosts").checked,
      workInfoShared: document.getElementById("workInfoShared").checked,
      // Technical Security
      vpnUse: document.getElementById("vpnUse").checked,
      osUpdates: document.getElementById("osUpdates").checked,
      backupData: document.getElementById("backupData").checked
    };

    // 2. Validation
    if (!formData.email) {
      throw new Error("Email is required!");
    }

    if (!formData.email.includes("@")) {
      throw new Error("Please enter a valid email address");
    }

    if (formData.platforms.length === 0) {
      throw new Error("Please select at least one platform!");
    }

    // 3. Submit to Backend
    const response = await fetch('http://localhost:5000/submit', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData)
    });

    // 4. Handle Response
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Server returned an error");
    }

    const { scan_id, status_url } = await response.json();
    
    // 5. Redirect to Results
    window.location.href = `results.html?scan_id=${scan_id}`;

  } catch (error) {
    // 6. Error Handling
    console.error("Submission error:", error);
    
    // Show user-friendly error
    alert(`Scan failed: ${error.message}`);
    
    // Re-enable UI
    submitBtn.disabled = false;
    spinner.style.display = "none";
    
    // Detailed error reporting (for debugging)
    const errorDisplay = document.getElementById("error-display");
    if (errorDisplay) {
      errorDisplay.textContent = error.message;
      errorDisplay.style.display = "block";
    }
  }
});
