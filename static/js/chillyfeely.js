/**
 * Enhanced fetch function with automatic loading indicator
 * @param {string} url - The URL to fetch from
 * @param {Object} options - Fetch options
 * @param {number} minLoadTime - Minimum loading time in ms (default: 500ms)
 * @returns {Promise<any>} - The parsed response data
 */
async function enhancedFetch(url, options = {}, minLoadTime = 500) {
  // Start loading indicator
  document.body.style.pointerEvents = "none";
  const loaderStartTime = Date.now();
  showLoader();

  try {
    // Make the actual fetch request
    const response = await fetch(url, options);

    if (!response.ok) {
      throw new Error(`Request failed with status: ${response.status}`);
    }

    // Parse the response (assuming JSON)
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Fetch error:", error);
    throw error; // Re-throw to handle in caller function
  } finally {
    // Ensure loader displays for at least minLoadTime milliseconds
    const elapsedTime = Date.now() - loaderStartTime;
    const remainingTime = Math.max(0, minLoadTime - elapsedTime);

    setTimeout(() => {
      hideLoader();
      document.body.style.pointerEvents = "auto";
    }, remainingTime);
  }
}

function createLoader() {
  // Create an overlay element if it doesn't exist
  let overlay = document.getElementById("loader-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "loader-overlay";
    overlay.className = "loader-overlay";
    document.body.appendChild(overlay);
  }

  // Create a loader element if it doesn't exist
  let loader = document.getElementById("loader");
  if (!loader) {
    loader = document.createElement("div");
    loader.id = "loader";
    loader.className = "loading-spinner";
    loader.innerHTML =
      '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>';
    loader.style.position = "fixed";
    loader.style.top = "50%";
    loader.style.left = "50%";
    loader.style.transform = "translate(-50%, -50%)";
    loader.style.zIndex = "1051"; // Ensure it's above the overlay
    overlay.appendChild(loader);
  }

  overlay.classList.remove("d-none", "fade-out");
  return overlay;
}

function showLoader() {
  const overlay = createLoader();
  overlay.classList.remove("d-none", "fade-out");
}

function hideLoader() {
  const overlay = document.getElementById("loader-overlay");
  if (overlay) {
    overlay.classList.add("fade-out");
    setTimeout(() => {
      overlay.classList.add("d-none");
    }, 200); // Match the transition duration
  }
}
