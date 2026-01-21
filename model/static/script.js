/**
 * CrisisSearch - Frontend JavaScript
 * Handles search interactions, mode switching, and user behavior tracking
 */

// DOM Elements
const app = document.getElementById('app');
const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-input');
const searchButton = document.getElementById('search-button');
const resultsContainer = document.getElementById('results-container');
const loadingIndicator = document.getElementById('loading');
const searchStats = document.getElementById('search-stats');
const emergencyBanner = document.getElementById('emergency-banner');
const alertTriggers = document.getElementById('alert-triggers');
const modeBadge = document.getElementById('mode-badge');
const resultCount = document.getElementById('result-count');
const searchTime = document.getElementById('search-time');
const modeIndicator = document.getElementById('mode-indicator');
const aiModeToggle = document.getElementById('ai-mode-toggle');

// State
let currentQuery = '';
let currentResults = [];
let lastClickedUrl = null;
let lastClickTime = null;
let forceEmergencyMode = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    // Search form submission
    searchForm.addEventListener('submit', handleSearch);

    // Hint chips
    document.querySelectorAll('.hint-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            searchInput.value = chip.dataset.query;
            handleSearch(new Event('submit'));
        });
    });

    // Emergency toggle button
    const emergencyToggle = document.getElementById('emergency-toggle');
    if (emergencyToggle) {
        emergencyToggle.addEventListener('click', () => {
            forceEmergencyMode = true;
            // Activate emergency mode visually
            updateMode({ mode: 'emergency', triggers: ['Manual activation'] });
            // If there's a current search, re-run it in emergency mode
            if (currentQuery) {
                handleSearch(new Event('submit'));
            }
        });
    }

    // Track when user returns to search page (back button detection)
    window.addEventListener('focus', handlePageFocus);

    // Track visibility change
    document.addEventListener('visibilitychange', handleVisibilityChange);
}

async function handleSearch(e) {
    e.preventDefault();

    const query = searchInput.value.trim();
    if (!query) return;

    currentQuery = query;

    // Show loading
    showLoading();
    hideResults();

    try {
        const aiMode = aiModeToggle ? aiModeToggle.checked : false;

        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                force_emergency: forceEmergencyMode,
                ai_mode: aiMode
            })
        });

        const data = await response.json();

        if (data.error) {
            showError(data.error);
            return;
        }

        // Update mode
        updateMode(data.mode);

        // Display results
        currentResults = data.results;
        displayResults(data);

    } catch (error) {
        showError('Search failed. Please try again.');
        console.error('Search error:', error);
    } finally {
        hideLoading();
    }
}

function updateMode(modeInfo) {
    const isEmergency = modeInfo.mode === 'emergency';

    if (isEmergency) {
        app.classList.add('emergency-mode');
        app.classList.remove('standard-mode');
        modeBadge.textContent = 'Emergency Mode';
        emergencyBanner.classList.remove('hidden');

        if (modeInfo.triggers && modeInfo.triggers.length > 0) {
            alertTriggers.textContent = `Detected: ${modeInfo.triggers.join(', ')}`;
        }
    } else {
        app.classList.remove('emergency-mode');
        app.classList.add('standard-mode');
        modeBadge.textContent = 'Standard Mode';
        emergencyBanner.classList.add('hidden');
    }
}

function displayResults(data) {
    const { results, total_results, search_time, mode } = data;

    // Update stats
    searchStats.classList.remove('hidden');
    resultCount.textContent = `${results.length} results`;
    searchTime.textContent = `${(search_time * 1000).toFixed(0)}ms`;

    if (mode.ai_enabled) {
        modeIndicator.textContent = mode.mode === 'emergency'
            ? '🤖 AI Emergency Mode'
            : '🤖 AI Enhanced Mode';
    } else {
        modeIndicator.textContent = mode.mode === 'emergency'
            ? '🚨 Emergency Mode'
            : '✓ Standard Mode';
    }

    // Clear previous results
    resultsContainer.innerHTML = '';

    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <p>No results found for "${currentQuery}"</p>
            </div>
        `;
        return;
    }

    // Render each result
    results.forEach((result, index) => {
        const card = createResultCard(result, index);
        resultsContainer.appendChild(card);
    });
}

function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.dataset.url = result.link;
    card.dataset.index = index;

    // Trust badge
    const trustBadgeContent = {
        verified: '✓',
        unverified: '?',
        suspicious: '⚠'
    };

    // Freshness class
    let freshnessClass = '';
    if (result.freshness_label === 'just now' || result.freshness_label === 'very recent') {
        freshnessClass = 'fresh';
    } else if (result.freshness_label === 'today' || result.freshness_label === 'yesterday') {
        freshnessClass = 'recent';
    } else if (result.freshness_label === 'outdated') {
        freshnessClass = 'outdated';
    }

    // Pogo warning
    const pogoWarning = result.pogo_count > 0
        ? `<span class="pogo-warning">⚡ ${result.pogo_count} quick returns</span>`
        : '';

    card.innerHTML = `
        <div class="result-header">
            <a href="${escapeHtml(result.link)}" 
               class="result-title" 
               target="_blank"
               onclick="trackClick('${escapeHtml(result.link)}')"
            >
                ${escapeHtml(result.title)}
            </a>
            <div class="result-badges">
                <span class="badge ${result.badge}" title="Trust: ${result.trust_score}">
                    ${trustBadgeContent[result.badge] || '?'}
                </span>
                <span class="freshness-badge ${freshnessClass}">
                    ${result.freshness_label || 'unknown'}
                </span>
            </div>
        </div>
        <div class="result-url">${escapeHtml(result.displayLink || result.link)}</div>
        <p class="result-snippet">${escapeHtml(result.snippet)}</p>
        <div class="result-meta">
            <div class="result-score">
                <span>Score:</span>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${result.final_score * 100}%"></div>
                </div>
                <span>${(result.final_score * 100).toFixed(0)}%</span>
            </div>
            ${pogoWarning}
        </div>
    `;

    return card;
}

function trackClick(url) {
    lastClickedUrl = url;
    lastClickTime = Date.now();

    // Send click event to backend
    fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            action: 'click',
            url: url,
            query: currentQuery
        })
    }).catch(err => console.error('Failed to track click:', err));
}

function handlePageFocus() {
    // Check if user returned quickly (potential pogo-stick)
    if (lastClickedUrl && lastClickTime) {
        const timeSpent = (Date.now() - lastClickTime) / 1000;

        if (timeSpent < 10) { // Quick return within 10 seconds
            // Send return event
            fetch('/api/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'return',
                    url: lastClickedUrl
                })
            }).then(response => response.json())
                .then(data => {
                    if (data.pogo_detected) {
                        console.log('Pogo-sticking detected:', data);
                        // Optionally refresh results
                        if (data.penalty_applied) {
                            refreshResults();
                        }
                    }
                })
                .catch(err => console.error('Failed to track return:', err));
        }

        // Reset tracking
        lastClickedUrl = null;
        lastClickTime = null;
    }
}

function handleVisibilityChange() {
    if (document.visibilityState === 'visible') {
        handlePageFocus();
    }
}

async function refreshResults() {
    if (currentQuery) {
        // Re-run search to get updated rankings
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: currentQuery })
        });

        const data = await response.json();
        if (!data.error) {
            displayResults(data);
        }
    }
}

// Utility Functions
function showLoading() {
    loadingIndicator.classList.remove('hidden');
}

function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

function hideResults() {
    resultsContainer.innerHTML = '';
    searchStats.classList.add('hidden');
}

function showError(message) {
    resultsContainer.innerHTML = `
        <div class="error-message" style="
            text-align: center; 
            padding: 2rem; 
            color: var(--suspicious-color);
            background: rgba(239, 68, 68, 0.1);
            border-radius: var(--radius-lg);
        ">
            <p>⚠️ ${escapeHtml(message)}</p>
        </div>
    `;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
