// Global variable to track polling interval
let statusPollingInterval = null;

// Load URLs when page loads
document.addEventListener('DOMContentLoaded', function() {
  loadUrls();
  loadScraperStatus();
  
  // Set up scraper button event listener
  document.getElementById('run-scraper-btn').addEventListener('click', runScraper);
  
  // Start polling for scraper status updates every 2 seconds
  startStatusPolling();
});

// Function to load URLs from the server
async function loadUrls() {
  try {
    const response = await fetch('/admin/api/urls-data');
    const urls = await response.json();
    displayUrls(urls);
  } catch (error) {
    console.error('Error loading URLs:', error);
    displayUrls([]);
  }
}

// Function to display URLs in the table
function displayUrls(urls) {
  const urlCount = document.getElementById('url-count');
  const urlTable = document.getElementById('url-table');
  
  urlCount.textContent = urls.length;
  
  if (urls.length > 0) {
    const tableHTML = `
      <table>
        <thead>
          <tr>
            <th>Product Name</th>
            <th>URL</th>
            <th>Added</th>
            <th>Updated</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${urls.map(url => `
            <tr>
              <td>
                <div class="product-name">${url.name || 'Unnamed Product'}</div>
              </td>
              <td>
                <a href="${url.url}" target="_blank" class="product-url">${url.url}</a>
              </td>
              <td>
                <div class="timestamp">${new Date(url.createdAt).toLocaleString()}</div>
              </td>
              <td>
                <div class="timestamp">${url.updatedAt ? new Date(url.updatedAt).toLocaleString() : 'Never'}</div>
              </td>
              <td>
                <button class="icon-btn copy-btn" onclick="copyUrl('${url.url}')" title="Copy URL">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                  </svg>
                </button>
                <button class="icon-btn delete-btn" onclick="deleteUrl('${url._id}')" title="Delete URL">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                  </svg>
                </button>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
    urlTable.innerHTML = tableHTML;
  } else {
    urlTable.innerHTML = `
      <div class="empty-state">
        <h3>No URLs Added Yet</h3>
        <p>Add your first product URL using the form above to get started.</p>
      </div>
    `;
  }
}

// Function to delete URL
async function deleteUrl(urlId) {
  if (!confirm('Are you sure you want to delete this URL?')) {
    return;
  }
  
  try {
    const response = await fetch('/admin/delete-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ id: urlId })
    });
    
    if (response.ok) {
      // Reload URLs after successful deletion
      loadUrls();
    } else {
      alert('Error deleting URL. Please try again.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error deleting URL. Please try again.');
  }
}

// Function to copy URL to clipboard
async function copyUrl(url) {
  try {
    await navigator.clipboard.writeText(url);
    
    // Show success feedback
    const copyBtn = event.target.closest('.copy-btn');
    const originalHTML = copyBtn.innerHTML;
    copyBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
      </svg>
    `;
    copyBtn.style.background = '#28a745';
    
    // Reset button after 2 seconds
    setTimeout(() => {
      copyBtn.innerHTML = originalHTML;
      copyBtn.style.background = '';
    }, 2000);
    
  } catch (err) {
    console.error('Failed to copy URL:', err);
    
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = url;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    
    // Show success feedback
    const copyBtn = event.target.closest('.copy-btn');
    const originalHTML = copyBtn.innerHTML;
    copyBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
      </svg>
    `;
    copyBtn.style.background = '#28a745';
    
    setTimeout(() => {
      copyBtn.innerHTML = originalHTML;
      copyBtn.style.background = '';
    }, 2000);
  }
}

// Handle form submission with AJAX
document.querySelector('form[action="/admin/add-url"]').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const formData = new FormData(this);
  const url = formData.get('url');
  const name = formData.get('name');
  
  try {
    const response = await fetch('/admin/add-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, name })
    });
    
    if (response.ok) {
      // Reload URLs after successful addition
      loadUrls();
      // Clear form
      this.reset();
    } else {
      alert('Error adding URL. Please try again.');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error adding URL. Please try again.');
  }
});

// Function to start status polling
function startStatusPolling() {
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval);
  }
  statusPollingInterval = setInterval(loadScraperStatus, 2000);
}

// Function to stop status polling
function stopStatusPolling() {
  if (statusPollingInterval) {
    clearInterval(statusPollingInterval);
    statusPollingInterval = null;
  }
}

// Function to load scraper status
async function loadScraperStatus() {
  try {
    const response = await fetch('/admin/scraper-status');
    const status = await response.json();
    updateScraperStatus(status);
    
    // Stop polling if scraper is not running
    if (!status.running) {
      stopStatusPolling();
    }
  } catch (error) {
    console.error('Error loading scraper status:', error);
  }
}

// Function to update scraper status display
function updateScraperStatus(status) {
  const statusText = document.getElementById('status-text');
  const runBtn = document.getElementById('run-scraper-btn');
  const lastRun = document.getElementById('last-run');
  const currentStatus = document.getElementById('current-status');
  const details = document.getElementById('scraper-details');
  
  // Update status text
  if (status.running) {
    statusText.textContent = 'Running...';
    statusText.className = 'status-running';
    runBtn.disabled = true;
    runBtn.textContent = 'Scraper Running...';
  } else {
    statusText.textContent = 'Ready';
    statusText.className = 'status-ready';
    runBtn.disabled = false;
    runBtn.textContent = 'Run Scraper';
  }
  
  // Update details
  if (status.last_run || status.last_status) {
    details.style.display = 'block';
    lastRun.textContent = status.last_run ? new Date(status.last_run).toLocaleString() : 'Never';
    currentStatus.textContent = status.last_status || '-';
    
    if (status.error) {
      currentStatus.textContent = `Error: ${status.error}`;
      currentStatus.className = 'status-error';
    } else {
      currentStatus.className = '';
    }
  }
}

// Function to run scraper
async function runScraper() {
  const runBtn = document.getElementById('run-scraper-btn');
  
  try {
    runBtn.disabled = true;
    runBtn.textContent = 'Starting...';
    
    const response = await fetch('/admin/run-scraper', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Start polling for status updates
      startStatusPolling();
      console.log('Scraper started successfully');
    } else {
      alert(`Error: ${result.error}`);
      runBtn.disabled = false;
      runBtn.textContent = 'Run Scraper';
    }
  } catch (error) {
    console.error('Error starting scraper:', error);
    alert('Error starting scraper. Please try again.');
    runBtn.disabled = false;
    runBtn.textContent = 'Run Scraper';
  }
} 