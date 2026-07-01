/**
 * Binance Futures Trading Bot — Professional Dashboard Controller
 * ================================================================
 */

// ============================================================
// STATE
// ============================================================
const STATE = {
    currentSymbol: 'BTCUSDT',
    lastOrderResponse: null,
    marketInterval: null,
    accountInterval: null,
};

// ============================================================
// UTILITY
// ============================================================
function $(id) { return document.getElementById(id); }

function formatNumber(num, decimals) {
    if (num === null || num === undefined || num === '—') return '—';
    const n = typeof num === 'string' ? parseFloat(num) : num;
    if (isNaN(n)) return '—';
    return n.toLocaleString('en-US', {
        minimumFractionDigits: decimals || 2,
        maximumFractionDigits: decimals || 2,
    });
}

function timestamp() {
    return new Date().toLocaleTimeString('en-US', { hour12: false });
}

// ============================================================
// THEME TOGGLE
// ============================================================
function getSavedTheme() {
    try {
        return localStorage.getItem('tradebot-theme') || 'dark';
    } catch(e) {
        return 'dark';
    }
}

function setSavedTheme(theme) {
    try {
        localStorage.setItem('tradebot-theme', theme);
    } catch(e) {}
}

function applyTheme(theme) {
    var body = document.body;
    var btn = document.getElementById('themeBtn');
    if (theme === 'light') {
        body.classList.add('theme-light');
        if (btn) btn.textContent = '☀️';
    } else {
        body.classList.remove('theme-light');
        if (btn) btn.textContent = '🌙';
    }
}

function toggleTheme() {
    var next = document.body.classList.contains('theme-light') ? 'dark' : 'light';
    applyTheme(next);
    setSavedTheme(next);
    log('Switched to ' + next + ' theme', 'info');
}

// Apply saved theme on load
applyTheme(getSavedTheme());

// ============================================================
// CLOCK
// ============================================================
function updateClock() {
    const now = new Date();
    $('clock').textContent = now.toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
    $('serverTime').textContent = now.toISOString().replace('T', ' ').substring(0, 19);
}
setInterval(updateClock, 1000);
updateClock();

// ============================================================
// LOGGING
// ============================================================
function log(message, level) {
    const box = $('logsBox');
    const entry = document.createElement('div');
    entry.className = 'log-entry log-' + (level || 'info');
    entry.innerHTML = '<span class="log-time">[' + timestamp() + ']</span><span class="log-msg">' + message + '</span>';
    box.appendChild(entry);
    box.scrollTop = box.scrollHeight;
}

function clearLogs() {
    $('logsBox').innerHTML = '';
    log('Activity log cleared', 'info');
}

// ============================================================
// PING
// ============================================================
function ping() {
    const btn = $('pingBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Pinging...';
    log('Testing connection to Binance Futures Testnet...', 'info');

    fetch('/api/ping')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                log('Ping successful — Testnet reachable (' + (data.elapsed || '?') + 's)', 'success');
                showFlashMessage('Testnet reachable ✓', 'success');
            } else {
                log('Ping failed: ' + data.error, 'error');
                showFlashMessage('Ping failed', 'error');
            }
        })
        .catch(function(err) {
            log('Network error: ' + err.message, 'error');
            showFlashMessage('Network error', 'error');
        })
        .finally(function() {
            btn.disabled = false;
            btn.innerHTML = '<span class="btn-icon">🔗</span> Ping Test';
        });
}

// ============================================================
// FLASH MESSAGE (temporary notification)
// ============================================================
function showFlashMessage(text, type) {
    const response = $('responseContent');
    response.innerHTML =
        '<div class="response-status-badge ' + (type === 'success' ? 'success' : 'error') + '" style="padding:8px 16px;font-size:13px;">' +
        (type === 'success' ? '✓ ' : '✗ ') + text +
        '</div>';
}

// ============================================================
// TOGGLE PRICE FIELD
// ============================================================
function togglePriceField() {
    const isLimit = document.querySelector('input[name="type"]:checked').value === 'LIMIT';
    $('priceGroup').style.display = isLimit ? 'block' : 'none';
    $('price').disabled = !isLimit;
    updateOrderPreview();
}

// ============================================================
// QUANTITY PRESETS
// ============================================================
function setQuantity(percent) {
    // For now, just set a placeholder — in production this would
    // calculate from available balance.
    const qty = $('quantity');
    if (percent === 100) {
        qty.value = '1.0';
    } else if (percent === 75) {
        qty.value = '0.75';
    } else if (percent === 50) {
        qty.value = '0.5';
    } else {
        qty.value = '0.25';
    }
    updateOrderPreview();
}

// ============================================================
// ORDER PREVIEW
// ============================================================
function updateOrderPreview() {
    const symbol = $('symbol').value;
    const side = document.querySelector('input[name="side"]:checked').value;
    const type = document.querySelector('input[name="type"]:checked').value;
    const qty = $('quantity').value || '—';
    const price = $('price').value || '—';

    let preview = side + ' ' + type + ' ' + qty + ' ' + symbol;
    if (type === 'LIMIT' && price !== '—') {
        preview += ' @ ' + price;
    }
    $('previewText').textContent = preview || '—';
}

// Auto-update preview on input changes
document.addEventListener('DOMContentLoaded', function() {
    ['symbol', 'quantity', 'price'].forEach(function(id) {
        var el = $(id);
        if (el) el.addEventListener('input', updateOrderPreview);
    });
    document.querySelectorAll('input[name="side"], input[name="type"]').forEach(function(el) {
        el.addEventListener('change', updateOrderPreview);
    });
    updateOrderPreview();
});

// ============================================================
// PLACE ORDER
// ============================================================
function placeOrder() {
    const btn = $('placeBtn');
    const loader = $('orderLoader');
    const btnText = btn.querySelector('.btn-submit-text');

    btn.disabled = true;
    btnText.style.display = 'none';
    loader.style.display = 'flex';

    const data = {
        symbol: $('symbol').value,
        side: document.querySelector('input[name="side"]:checked').value,
        type: document.querySelector('input[name="type"]:checked').value,
        quantity: $('quantity').value
    };

    if (data.type === 'LIMIT') {
        data.price = $('price').value;
    }

    log(data.side + ' ' + data.type + ' ' + data.quantity + ' ' + data.symbol + ' — submitting...', 'info');

    fetch('/api/order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
        .then(function(r) { return r.json(); })
        .then(function(resp) {
            if (resp.success) {
                STATE.lastOrderResponse = resp;
                log('Order ' + (resp.order.orderId || '?') + ' — ' + resp.order.status, 'success');
                showOrderResponse(resp);
                $('execTimer').textContent = 'Last order: ' + resp.elapsed + 's';
            } else {
                log('Order failed: ' + resp.error, 'error');
                showOrderError(resp.error);
            }
        })
        .catch(function(err) {
            log('Network error: ' + err.message, 'error');
            showOrderError('Network error: ' + err.message);
        })
        .finally(function() {
            btn.disabled = false;
            btnText.style.display = 'inline';
            loader.style.display = 'none';
        });
}

// ============================================================
// RESPONSE DISPLAY
// ============================================================
function showOrderResponse(response) {
    const order = response.order || {};
    const status = order.status || 'UNKNOWN';
    const isGood = status === 'FILLED' || status === 'NEW' || status === 'PARTIALLY_FILLED';

    var html = '<table class="response-table">';
    html += '<tr><td>Order ID</td><td>' + (order.orderId || 'N/A') + '</td></tr>';
    html += '<tr><td>Symbol</td><td>' + (order.symbol || 'N/A') + '</td></tr>';
    html += '<tr><td>Side</td><td>' + (order.side || 'N/A') + '</td></tr>';
    html += '<tr><td>Type</td><td>' + (order.type || 'N/A') + '</td></tr>';
    html += '<tr><td>Status</td><td>' + status + '</td></tr>';
    html += '<tr><td>Executed Qty</td><td>' + (order.executedQty || '0') + '</td></tr>';
    html += '<tr><td>Avg Price</td><td>' + (order.avgPrice || '—') + '</td></tr>';
    html += '</table>';

    html += '<div class="response-summary">';
    html += '<span class="response-status-badge ' + (isGood ? 'success' : 'error') + '">' +
            (isGood ? '✓ Order Placed' : 'Status: ' + status) + '</span>';
    if (response.elapsed) {
        html += '<span class="response-timer">' + response.elapsed + 's</span>';
    }
    html += '</div>';

    $('responseContent').innerHTML = html;
}

function showOrderError(message) {
    $('responseContent').innerHTML =
        '<div class="response-summary">' +
        '<span class="response-status-badge error">✗ Order Failed</span>' +
        '</div>' +
        '<div style="color:var(--red);font-family:var(--mono);font-size:12px;margin-top:8px;padding:8px;background:var(--red-bg);border-radius:4px;">' +
        message +
        '</div>';
}

// ============================================================
// MARKET DATA
// ============================================================
function fetchMarketData() {
    const symbol = $('symbol').value;

    fetch('/api/ticker/' + symbol)
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                updateMarketDisplay(data);
                $('priceUpdated').textContent = 'updated ' + timestamp();
            }
        })
        .catch(function(err) {
            // Silent fail — market data is refresh-on-interval
        });
}

function updateMarketDisplay(data) {
    const t = data.ticker || {};

    // Current price with color
    const price = parseFloat(t.lastPrice || t.markPrice || 0);
    $('markPrice').textContent = formatNumber(price, 2);
    $('markPrice').className = 'metric-value';

    // 24h change
    const change = parseFloat(t.priceChangePercent || 0);
    const changeEl = $('change24h');
    changeEl.textContent = (change >= 0 ? '+' : '') + change.toFixed(2) + '%';
    changeEl.className = 'metric-value ' + (change >= 0 ? 'up' : 'down');

    // Update current price in symbol selector
    $('currentPrice').textContent = formatNumber(price, 2);
    $('currentPrice').style.color = change >= 0 ? 'var(--green)' : 'var(--red)';

    // High / Low
    $('high24h').textContent = formatNumber(t.highPrice, 2);
    $('low24h').textContent = formatNumber(t.lowPrice, 2);

    // Volume
    const vol = parseFloat(t.volume || t.quoteVolume || 0);
    $('volume24h').textContent = formatNumber(vol, 1);

    // Trades
    if (t.count) {
        $('trades24h').textContent = parseInt(t.count).toLocaleString();
    }
}

// ============================================================
// ACCOUNT DATA
// ============================================================
function refreshAccount() {
    // Visual feedback on the refresh button
    var btn = document.querySelector('.account-panel .panel-header .btn');
    if (btn) {
        btn.textContent = '⟳ Refreshing...';
        btn.disabled = true;
    }

    log('Refreshing account data...', 'info');

    fetch('/api/account')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                updateAccountDisplay(data);
                log('Account data refreshed', 'success');
            } else {
                log('Account refresh failed: ' + data.error, 'error');
                showFlashMessage('Account: ' + data.error, 'error');
            }
        })
        .catch(function(err) {
            log('Account refresh network error: ' + err.message, 'error');
            showFlashMessage('Account refresh failed', 'error');
        })
        .finally(function() {
            if (btn) {
                btn.textContent = '⟳ Refresh';
                btn.disabled = false;
            }
        });
}

function updateAccountDisplay(data) {
    const acct = data.account || {};

    $('accountBalance').textContent = formatNumber(acct.totalWalletBalance, 2) + ' USDT';
    $('availableBalance').textContent = formatNumber(acct.availableBalance, 2) + ' USDT';

    const pnl = parseFloat(acct.totalUnrealizedProfit || 0);
    const pnlEl = $('unrealizedPnl');
    pnlEl.textContent = (pnl >= 0 ? '+' : '') + pnl.toFixed(2) + ' USDT';
    pnlEl.className = 'metric-value ' + (pnl >= 0 ? 'up' : 'down');

    const positions = acct.positions || [];
    const openCount = positions.filter(function(p) {
        return parseFloat(p.positionAmt || 0) !== 0;
    }).length;
    $('openPositions').textContent = openCount;
}

// ============================================================
// AUTO-REFRESH
// ============================================================
function startAutoRefresh() {
    // Market data every 5s
    if (STATE.marketInterval) clearInterval(STATE.marketInterval);
    STATE.marketInterval = setInterval(fetchMarketData, 5000);
    fetchMarketData();

    // Account data every 15s
    if (STATE.accountInterval) clearInterval(STATE.accountInterval);
    STATE.accountInterval = setInterval(refreshAccount, 15000);
    refreshAccount();
}

// ============================================================
// SYMBOL CHANGE HANDLER
// ============================================================
$('symbol').addEventListener('change', function() {
    STATE.currentSymbol = this.value;
    $('currentPrice').textContent = '—';
    fetchMarketData();
    log('Switched to ' + this.value, 'info');
    updateOrderPreview();
});

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    log('Dashboard initialized. Connected to Binance Futures Testnet.', 'success');
    startAutoRefresh();

    // Keyboard shortcut: Enter to place order
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey && !$('placeBtn').disabled) {
            placeOrder();
        }
    });
});
