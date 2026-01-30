document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // helper to avoid inserting raw HTML (basic escaping)
  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${escapeHtml(name)}</h4>
          <p>${escapeHtml(details.description)}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule)}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>

          <div class="participants-section">
            <h5 class="participants-title">Participants</h5>
            ${
              details.participants && details.participants.length > 0
                ? `<ul class="participants-list">
                    ${details.participants.map(p => `<li><span class="participant-email">${escapeHtml(p)}</span><button class="delete-btn" data-activity="${escapeHtml(name)}" data-email="${escapeHtml(p)}" title="Remove participant">✕</button></li>`).join("")}
                  </ul>`
                : `<p class="no-participants">No participants yet</p>`
            }
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add delete button event listeners
        const deleteButtons = activityCard.querySelectorAll(".delete-btn");
        deleteButtons.forEach(btn => {
          btn.addEventListener("click", handleDeleteParticipant);
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        messageDiv.classList.remove("hidden");

        // Reload activities after successful signup
        setTimeout(() => {
          messageDiv.classList.add("hidden");
          fetchActivities();
        }, 1500);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");

        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      }
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle participant deletion
  async function handleDeleteParticipant(event) {
    event.preventDefault();
    const button = event.target;
    const activity = button.dataset.activity;
    const email = button.dataset.email;

    if (!confirm(`Remove ${escapeHtml(email)} from ${escapeHtml(activity)}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        messageDiv.classList.remove("hidden");
        // Reload activities after successful deletion
        setTimeout(() => {
          messageDiv.classList.add("hidden");
          fetchActivities();
        }, 1500);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  }

  // Initialize app
  fetchActivities();
});
