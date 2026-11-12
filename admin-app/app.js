const state = { token: sessionStorage.getItem('virgo-admin-token'), admin: JSON.parse(sessionStorage.getItem('virgo-admin-profile') || 'null'), page: 'overview' };
const loginView = document.querySelector('#login-view');
const appView = document.querySelector('#app-view');
const content = document.querySelector('#page-content');
const error = document.querySelector('#app-error');

const api = async (path, options = {}) => {
  const response = await fetch(`/api/v1${path}`, { ...options, headers: { 'Content-Type': 'application/json', ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}), ...(options.headers || {}) } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) { const detail = Array.isArray(body.detail) ? body.detail.map(item => item.msg).join(' ') : body.detail; throw new Error(detail || 'The request could not be completed.'); }
  return body;
};
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const badge = value => `<span class="badge ${esc(value)}">${esc(value).replaceAll('_', ' ')}</span>`;
const localPhone = value => String(value ?? '').replace(/\D/g, '').slice(-10);
const has = permission => state.admin?.permissions?.includes(permission);

function showApp() {
  loginView.classList.add('hidden'); appView.classList.remove('hidden');
  document.querySelector('#admin-name').textContent = `${state.admin.full_name} · ID ${state.admin.id}`;
  document.querySelector('#admin-role').textContent = state.admin.role.replaceAll('_', ' ');
  document.querySelector('[data-page="rides"]').classList.toggle('hidden', !has('rides:read'));
  document.querySelector('[data-page="documents"]').classList.toggle('hidden', !has('documents:review'));
  document.querySelector('[data-page="rate-cards"]').classList.toggle('hidden', !has('rate_cards:read'));
  document.querySelector('[data-page="support"]').classList.toggle('hidden', !has('support:manage'));
  document.querySelector('[data-page="outstation"]').classList.toggle('hidden', !has('outstation:manage'));
  render();
}
function showLogin() { appView.classList.add('hidden'); loginView.classList.remove('hidden'); }
function clearSession() { sessionStorage.clear(); state.token = null; state.admin = null; showLogin(); }

document.querySelector('#login-form').addEventListener('submit', async event => {
  event.preventDefault(); const loginError = document.querySelector('#login-error'); const button = event.currentTarget.querySelector('button'); loginError.textContent = ''; button.disabled = true; button.textContent = 'Checking Admin ID...';
  try { const session = await api('/admin/auth/login', { method: 'POST', body: JSON.stringify({ email: document.querySelector('#email').value, password: document.querySelector('#password').value }) }); state.token = session.access_token; state.admin = session.admin; sessionStorage.setItem('virgo-admin-token', state.token); sessionStorage.setItem('virgo-admin-profile', JSON.stringify(state.admin)); showApp(); }
  catch (err) { loginError.textContent = err.message; }
  finally { button.disabled = false; button.textContent = 'Sign in securely'; }
});
document.querySelector('#logout').addEventListener('click', clearSession);
document.querySelectorAll('.nav-item').forEach(button => button.addEventListener('click', () => { state.page = button.dataset.page; document.querySelectorAll('.nav-item').forEach(item => item.classList.toggle('active', item === button)); render(); }));

async function render() {
  error.textContent = '';
  document.querySelector('#page-title').textContent = ({
    overview: 'Overview',
    rides: 'Local rides',
    documents: 'Document reviews',
    drivers: 'Drivers & vehicles',
    'rate-cards': 'Rate cards',
    support: 'Support tickets',
    outstation: 'Outstation bookings',
    account: 'Admin account',
  })[state.page];
  content.innerHTML = '<p class="empty">Loading...</p>';
  try {
    if (state.page === 'overview') await overview();
    if (state.page === 'rides') await rides();
    if (state.page === 'documents') await documents();
    if (state.page === 'drivers') await drivers();
    if (state.page === 'rate-cards') await rateCards();
    if (state.page === 'support') await support();
    if (state.page === 'outstation') await outstation();
    if (state.page === 'account') await account();
  } catch (err) {
    content.innerHTML = '';
    error.textContent = err.message;
    if (/Admin session|authentication|unavailable/i.test(err.message)) clearSession();
  }
}
async function overview() {
  const [docs, driverList, tickets, rideList] = await Promise.all([
    has('documents:review') ? api('/admin/driver-documents?status_filter=pending') : [],
    api('/admin/drivers'),
    has('support:manage') ? api('/admin/support-tickets?ticket_status=open') : [],
    has('rides:read') ? api('/admin/rides') : []
  ]);
  const activeCount = rideList.filter(r => ['searching', 'driver_arriving', 'driver_arrived', 'in_progress'].includes(r.status)).length;
  content.innerHTML = `<div class="metrics">
    <div class="metric"><span>Active local rides</span><strong>${activeCount}</strong></div>
    <div class="metric"><span>Pending documents</span><strong>${docs.length}</strong></div>
    <div class="metric"><span>Verified drivers</span><strong>${driverList.filter(driver => driver.vehicle_verification_status === 'verified').length}</strong></div>
    <div class="metric"><span>Open support tickets</span><strong>${tickets.length}</strong></div>
  </div>
  <div class="page-grid">
    <section class="panel">
      <h2>Virgo Operations – Imphal</h2>
      <p class="muted">Live monitoring of local ride matching, driver dispatch, rate cards, and physical document compliance in Imphal, Manipur.</p>
    </section>
    <section class="panel">
      <h2>Secure Operations</h2>
      <p class="muted">All ride lifecycle actions, manual driver assignments, and rate card changes are audited.</p>
    </section>
  </div>`;
}

let currentRideFilter = 'all';

async function rides() {
  const allRides = await api('/admin/rides');
  const filtered = currentRideFilter === 'all'
    ? allRides
    : allRides.filter(r => {
        if (currentRideFilter === 'active') return ['searching', 'driver_arriving', 'driver_arrived', 'in_progress'].includes(r.status);
        return r.status === currentRideFilter;
      });

  content.innerHTML = `
    <div class="filter-bar">
      <button class="filter-btn ${currentRideFilter === 'all' ? 'active' : ''}" data-filter="all">All rides (${allRides.length})</button>
      <button class="filter-btn ${currentRideFilter === 'searching' ? 'active' : ''}" data-filter="searching">Searching</button>
      <button class="filter-btn ${currentRideFilter === 'active' ? 'active' : ''}" data-filter="active">In Progress / Arriving</button>
      <button class="filter-btn ${currentRideFilter === 'completed' ? 'active' : ''}" data-filter="completed">Completed</button>
      <button class="filter-btn ${currentRideFilter === 'cancelled' ? 'active' : ''}" data-filter="cancelled">Cancelled</button>
    </div>
    ${filtered.length ? `
      <div class="panel table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>Ride ID</th>
              <th>Passenger</th>
              <th>Category</th>
              <th>Driver &amp; Vehicle</th>
              <th>Route</th>
              <th>Fare</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${filtered.map(r => `
              <tr>
                <td><strong>#${r.id}</strong><br><span class="muted">${new Date(r.requested_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span></td>
                <td><strong>${esc(r.passenger_name)}</strong><br><span class="muted">${esc(localPhone(r.passenger_phone))}</span></td>
                <td><span class="badge in_progress">${esc(r.category_name)}</span></td>
                <td>${r.driver_name ? `<strong>${esc(r.driver_name)}</strong><br><span class="muted">${esc(r.vehicle_registration_number || '')}</span>` : '<span class="muted">Unassigned</span>'}</td>
                <td style="max-width:240px; font-size:12px;"><strong>P:</strong> ${esc(r.pickup_address)}<br><strong>D:</strong> ${esc(r.destination_address)}</td>
                <td><strong>₹${Math.round(r.fare_paise / 100)}</strong>${r.payment_status ? `<br><span class="badge ${r.payment_status === 'completed' ? 'verified' : 'pending'}">${esc(r.payment_status)}</span>` : ''}</td>
                <td>${badge(r.status)}</td>
                <td>
                  <div class="actions">
                    <button class="secondary btn-sm" data-ride-detail="${r.id}">View Details</button>
                    ${['requested', 'searching'].includes(r.status) && has('rides:manage') ? `<button class="approve btn-sm" data-assign-ride="${r.id}">Assign Driver</button>` : ''}
                    ${!['completed', 'cancelled'].includes(r.status) && has('rides:manage') ? `<button class="reject btn-sm" data-cancel-ride="${r.id}">Cancel</button>` : ''}
                  </div>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    ` : '<div class="panel empty">No rides found matching this filter.</div>'}
  `;

  document.querySelectorAll('.filter-btn').forEach(btn => btn.addEventListener('click', () => {
    currentRideFilter = btn.dataset.filter;
    rides();
  }));

  document.querySelectorAll('[data-ride-detail]').forEach(btn => btn.addEventListener('click', () => openRideDetailModal(Number(btn.dataset.rideDetail))));
  document.querySelectorAll('[data-assign-ride]').forEach(btn => btn.addEventListener('click', () => openAssignDriverModal(Number(btn.dataset.assignRide))));
  document.querySelectorAll('[data-cancel-ride]').forEach(btn => btn.addEventListener('click', () => adminCancelRide(Number(btn.dataset.cancelRide))));
}

async function openRideDetailModal(rideId) {
  try {
    const ride = await api(`/admin/rides/${rideId}`);
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <section class="ride-modal" role="dialog" aria-modal="true">
        <div class="picker-head">
          <div>
            <p class="eyebrow">RIDE AUDIT &amp; LIFECYCLE</p>
            <h2>Ride #${ride.id} · ${esc(ride.category_name)}</h2>
            <p class="muted">Requested ${new Date(ride.requested_at).toLocaleString()}</p>
          </div>
          <button class="picker-close" aria-label="Close">×</button>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
          <div class="panel" style="padding:14px;">
            <h3 style="margin:0 0 8px 0; font-size:15px;">Passenger &amp; Driver</h3>
            <div class="detail-row"><span class="muted">Passenger:</span><strong>${esc(ride.passenger_name)} (${esc(localPhone(ride.passenger_phone))})</strong></div>
            <div class="detail-row"><span class="muted">Driver:</span><strong>${ride.driver_name ? `${esc(ride.driver_name)} (${esc(localPhone(ride.driver_phone))})` : 'Unassigned'}</strong></div>
            <div class="detail-row"><span class="muted">Vehicle:</span><strong>${ride.vehicle_name ? `${esc(ride.vehicle_name)} · ${esc(ride.vehicle_registration_number)}` : 'None'}</strong></div>
            <div class="detail-row"><span class="muted">Current Status:</span>${badge(ride.status)}</div>
            ${ride.cancellation_reason ? `<div class="detail-row"><span class="muted">Cancellation:</span><span style="color:var(--red); font-weight:600;">${esc(ride.cancellation_reason)} (by ${esc(ride.cancelled_by)})</span></div>` : ''}
          </div>

          <div class="panel" style="padding:14px;">
            <h3 style="margin:0 0 8px 0; font-size:15px;">Trip &amp; Timing</h3>
            <div class="detail-row"><span class="muted">Pickup:</span><span style="text-align:right; max-width:200px;">${esc(ride.pickup_address)}</span></div>
            <div class="detail-row"><span class="muted">Destination:</span><span style="text-align:right; max-width:200px;">${esc(ride.destination_address)}</span></div>
            <div class="detail-row"><span class="muted">Distance:</span><strong>${ride.final_distance_km ?? ride.estimated_distance_km} km</strong></div>
            <div class="detail-row"><span class="muted">Waiting time:</span><strong>${ride.actual_waiting_minutes != null ? `${ride.actual_waiting_minutes} min` : '0 min'}</strong></div>
          </div>
        </div>

        <div class="panel" style="padding:14px;">
          <h3 style="margin:0 0 10px 0; font-size:15px;">Fare Breakdown &amp; Commission (Rate Card v${ride.rate_card_version || 1})</h3>
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px;">
            <div>
              <div class="detail-row"><span class="muted">Base fare:</span><strong>₹${ride.base_fare_paise != null ? Math.round(ride.base_fare_paise / 100) : '—'}</strong></div>
              <div class="detail-row"><span class="muted">Distance fare:</span><strong>₹${ride.distance_fare_paise != null ? Math.round(ride.distance_fare_paise / 100) : '—'}</strong></div>
              <div class="detail-row"><span class="muted">Waiting charge:</span><strong>₹${ride.waiting_charge_paise != null ? Math.round(ride.waiting_charge_paise / 100) : 0}</strong></div>
            </div>
            <div>
              <div class="detail-row"><span class="muted">Surcharge (15%):</span><strong>₹${ride.surcharge_paise != null ? Math.round(ride.surcharge_paise / 100) : 0}</strong></div>
              <div class="detail-row"><span class="muted">GST (5%):</span><strong>₹${ride.gst_paise != null ? Math.round(ride.gst_paise / 100) : '—'}</strong></div>
              <div class="detail-row"><span class="muted">Customer Total:</span><strong style="color:var(--primary); font-size:16px;">₹${Math.round(ride.fare_paise / 100)}</strong></div>
            </div>
            <div>
              <div class="detail-row"><span class="muted">Commission (10%):</span><strong>₹${ride.commission_paise != null ? Math.round(ride.commission_paise / 100) : '—'}</strong></div>
              <div class="detail-row"><span class="muted">Driver Net:</span><strong style="color:var(--green); font-size:16px;">₹${ride.driver_net_paise != null ? Math.round(ride.driver_net_paise / 100) : '—'}</strong></div>
              <div class="detail-row"><span class="muted">Payment:</span>${ride.payment_status ? badge(ride.payment_status) : '<span class="muted">Pending</span>'}</div>
            </div>
          </div>
        </div>

        <div class="panel" style="padding:14px;">
          <h3 style="margin:0 0 10px 0; font-size:15px;">Event Timeline</h3>
          <div class="timeline">
            ${ride.events.length ? ride.events.map(ev => `
              <div class="timeline-item">
                <span class="timeline-time">${new Date(ev.occurred_at).toLocaleTimeString()}</span> ·
                <strong>${esc(ev.event_type.replaceAll('_', ' ').toUpperCase())}</strong>
                by <span class="muted">${esc(ev.actor_type)}</span>
                ${ev.payload ? `<span style="font-size:11px; color:var(--muted); font-family:monospace;">${esc(JSON.stringify(ev.payload))}</span>` : ''}
              </div>
            `).join('') : '<p class="muted">No events recorded.</p>'}
          </div>
        </div>
      </section>
    `;
    document.body.appendChild(overlay);
    const close = () => overlay.remove();
    overlay.addEventListener('click', e => { if (e.target === overlay || e.target.closest('.picker-close')) close(); });
  } catch (err) {
    alert(err.message);
  }
}

async function openAssignDriverModal(rideId) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <section class="upload-modal" role="dialog" aria-modal="true">
      <div class="picker-head">
        <div>
          <p class="eyebrow">MANUAL DISPATCH</p>
          <h3>Assign Driver to Ride #${rideId}</h3>
        </div>
        <button class="picker-close" aria-label="Close">×</button>
      </div>
      <form id="assign-driver-form" class="upload-form">
        <label>Driver Phone Number (10 digits) *
          <input type="text" name="driver_phone" required placeholder="e.g. 9876543210" />
        </label>
        <p id="assign-error" class="error"></p>
        <button class="primary" type="submit">Assign &amp; Dispatch</button>
      </form>
    </section>
  `;
  document.body.appendChild(overlay);
  const close = () => overlay.remove();
  overlay.addEventListener('click', e => { if (e.target === overlay || e.target.closest('.picker-close')) close(); });

  const form = overlay.querySelector('#assign-driver-form');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const errBox = overlay.querySelector('#assign-error');
    errBox.textContent = '';
    btn.disabled = true;
    try {
      const phone = form.querySelector('input[name="driver_phone"]').value;
      await api(`/admin/rides/${rideId}/assign-driver`, {
        method: 'POST',
        body: JSON.stringify({ driver_phone: phone.trim() }),
      });
      close();
      await rides();
    } catch (err) {
      errBox.textContent = err.message;
      btn.disabled = false;
    }
  });
}

async function adminCancelRide(rideId) {
  const reason = prompt('Please enter the reason for cancelling this ride:');
  if (!reason || !reason.trim()) return;
  try {
    await api(`/admin/rides/${rideId}/cancel`, {
      method: 'POST',
      body: JSON.stringify({ reason: reason.trim() }),
    });
    await rides();
  } catch (err) {
    alert(err.message);
  }
}

async function rateCards() {
  const cards = await api('/admin/rate-cards');
  content.innerHTML = `
    <div class="rate-card-grid">
      ${cards.map(card => `
        <article class="rate-card">
          <div class="rate-card-header">
            <h3>${esc(card.category_code.replace('_', ' ').toUpperCase())}</h3>
            <span class="badge in_progress">v${card.version}</span>
          </div>
          <div class="rate-row"><span>Base Fare:</span><strong>₹${card.base_fare_paise / 100}</strong></div>
          <div class="rate-row"><span>First ${card.first_tier_km} km:</span><strong>₹${card.first_tier_rate_paise / 100}/km</strong></div>
          <div class="rate-row"><span>After ${card.first_tier_km} km:</span><strong>₹${card.second_tier_rate_paise / 100}/km</strong></div>
          <div class="rate-row"><span>Waiting Charge:</span><strong>₹${card.waiting_charge_per_minute_paise / 100}/min</strong></div>
          <div class="rate-row"><span>Grace Period:</span><strong>${card.waiting_grace_period_minutes} min</strong></div>
          <div class="rate-row"><span>Surcharge:</span><strong>${Math.round(card.surcharge_percentage * 100)}% (&gt; ${card.surcharge_distance_threshold_km} km)</strong></div>
          <div class="rate-row"><span>Cancellation Fee:</span><strong>₹${card.cancellation_fee_paise / 100}</strong></div>
          <div class="rate-row"><span>GST Rate:</span><strong>${Math.round(card.gst_rate * 100)}%</strong></div>
          <div class="rate-row"><span>Virgo Commission:</span><strong>${Math.round(card.commission_rate * 100)}%</strong></div>
          ${has('rate_cards:manage') ? `
            <div style="margin-top:8px;">
              <button class="secondary btn-sm" style="width:100%;" data-edit-card="${card.id}">Edit Rate Card</button>
            </div>
          ` : ''}
        </article>
      `).join('')}
    </div>
  `;

  document.querySelectorAll('[data-edit-card]').forEach(btn => btn.addEventListener('click', () => {
    const card = cards.find(c => c.id === Number(btn.dataset.editCard));
    if (card) openEditRateCardModal(card);
  }));
}

function openEditRateCardModal(card) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <section class="upload-modal" role="dialog" aria-modal="true" style="max-width:540px;">
      <div class="picker-head">
        <div>
          <p class="eyebrow">RATE CARD CONFIGURATION</p>
          <h3>${esc(card.category_code.replace('_', ' ').toUpperCase())} · v${card.version}</h3>
        </div>
        <button class="picker-close" aria-label="Close">×</button>
      </div>
      <form id="edit-rate-card-form" class="upload-form">
        <label>Base Fare (₹)
          <input type="number" step="0.5" name="base_fare_rupees" value="${card.base_fare_paise / 100}" required />
        </label>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
          <label>First Tier Rate (₹/km)
            <input type="number" step="0.5" name="first_tier_rate_rupees" value="${card.first_tier_rate_paise / 100}" required />
          </label>
          <label>Second Tier Rate (₹/km)
            <input type="number" step="0.5" name="second_tier_rate_rupees" value="${card.second_tier_rate_paise / 100}" required />
          </label>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
          <label>Waiting Charge (₹/min)
            <input type="number" step="0.25" name="waiting_charge_rupees" value="${card.waiting_charge_per_minute_paise / 100}" required />
          </label>
          <label>Waiting Grace Period (min)
            <input type="number" name="waiting_grace_period_minutes" value="${card.waiting_grace_period_minutes}" required />
          </label>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
          <label>Cancellation Fee (₹)
            <input type="number" step="1" name="cancellation_fee_rupees" value="${card.cancellation_fee_paise / 100}" required />
          </label>
          <label>Surcharge Percentage (%)
            <input type="number" step="1" name="surcharge_percentage_display" value="${Math.round(card.surcharge_percentage * 100)}" required />
          </label>
        </div>
        <p id="rate-card-error" class="error"></p>
        <button class="primary" type="submit">Update &amp; Increment Version</button>
      </form>
    </section>
  `;
  document.body.appendChild(overlay);
  const close = () => overlay.remove();
  overlay.addEventListener('click', e => { if (e.target === overlay || e.target.closest('.picker-close')) close(); });

  const form = overlay.querySelector('#edit-rate-card-form');
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const errBox = overlay.querySelector('#rate-card-error');
    errBox.textContent = '';
    btn.disabled = true;
    try {
      const baseFare = Math.round(Number(form.base_fare_rupees.value) * 100);
      const tier1Rate = Math.round(Number(form.first_tier_rate_rupees.value) * 100);
      const tier2Rate = Math.round(Number(form.second_tier_rate_rupees.value) * 100);
      const waitingCharge = Math.round(Number(form.waiting_charge_rupees.value) * 100);
      const graceMin = parseInt(form.waiting_grace_period_minutes.value, 10);
      const cancelFee = Math.round(Number(form.cancellation_fee_rupees.value) * 100);
      const surchargePct = Number(form.surcharge_percentage_display.value) / 100.0;

      await api(`/admin/rate-cards/${card.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          base_fare_paise: baseFare,
          first_tier_rate_paise: tier1Rate,
          second_tier_rate_paise: tier2Rate,
          waiting_charge_per_minute_paise: waitingCharge,
          waiting_grace_period_minutes: graceMin,
          cancellation_fee_paise: cancelFee,
          surcharge_percentage: surchargePct,
        }),
      });
      close();
      await rateCards();
    } catch (err) {
      errBox.textContent = err.message;
      btn.disabled = false;
    }
  });
}
async function documents() {
  const items = await api('/admin/driver-documents?status_filter=pending');
  content.innerHTML = items.length ? `<div class="list">${items.map(item => `<article class="item"><div class="item-head"><h3>${esc(item.driver_name)} · ${esc(labelDocument(item.document_type))}</h3>${badge(item.verification_status)}</div><p>${esc(item.operating_city || 'City not provided')} · Vehicle: ${esc(item.vehicle_registration_number || 'Not assigned')}</p><p>Document number: ${esc(item.document_number)}</p><div class="actions"><button class="secondary" data-preview-driver="${item.driver_id}" data-document="${item.document_type}">Preview document</button><button class="approve" data-review="verified" data-driver="${item.driver_id}" data-document="${item.document_type}">Approve</button><button class="reject" data-review="rejected" data-driver="${item.driver_id}" data-document="${item.document_type}">Reject</button></div></article>`).join('')}</div>` : '<div class="panel empty">No pending documents to review.</div>';
  document.querySelectorAll('[data-review]').forEach(button => button.addEventListener('click', () => reviewDocument(button.dataset.driver, button.dataset.document, button.dataset.review)));
  document.querySelectorAll('[data-preview-driver]').forEach(button => button.addEventListener('click', () => previewDriverDocument(button.dataset.previewDriver, button.dataset.document)));
}

async function previewDriverDocument(driverId, documentType) {
  try {
    const res = await api(`/admin/drivers/${driverId}/documents/${documentType}/preview`);
    openPreviewModal(res.preview_url, labelDocument(documentType));
  } catch (err) {
    alert(err.message);
  }
}

async function reviewDocument(driverId, documentType, decision) {
  const review_note = decision === 'rejected' ? prompt('Explain why this document is rejected:') : null;
  if (decision === 'rejected' && (!review_note || !review_note.trim())) return;
  try {
    await api(`/admin/drivers/${driverId}/documents/${documentType}/review`, {
      method: 'PUT',
      body: JSON.stringify({ status: decision, review_note: review_note ? review_note.trim() : null })
    });
    if (state.page === 'documents') await documents();
  } catch (err) {
    error.textContent = err.message;
  }
}

async function drivers() {
  const items = await api('/admin/drivers');
  content.innerHTML = items.length ? `<div class="panel table-wrap"><table class="table"><thead><tr><th>Driver</th><th>City</th><th>Vehicle</th><th>Vehicle status</th><th>Documents & Compliance</th></tr></thead><tbody>${items.map(item => `<tr><td><strong>${esc(item.full_name)}</strong><br><span class="muted">${esc(localPhone(item.phone_number))}</span></td><td>${esc(item.operating_city || '—')}</td><td>${esc(item.vehicle_name || '—')}<br><span class="muted">${esc(item.vehicle_registration_number || '')}</span></td><td>${item.vehicle_verification_status ? badge(item.vehicle_verification_status) : '—'}</td><td><button class="secondary btn-sm" data-manage-docs="${item.id}" data-driver-name="${esc(item.full_name)}">Manage Documents</button></td></tr>`).join('')}</tbody></table></div>` : '<div class="panel empty">No Drivers are registered yet.</div>';
  document.querySelectorAll('[data-manage-docs]').forEach(button => button.addEventListener('click', () => openDriverDocumentsModal(Number(button.dataset.manageDocs), button.dataset.driverName)));
}

async function openDriverDocumentsModal(driverId, driverName) {
  try {
    const data = await api(`/admin/drivers/${driverId}/documents`);
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `<section class="doc-modal" role="dialog" aria-modal="true">
      <div class="picker-head">
        <div>
          <p class="eyebrow">PHYSICAL VERIFICATION CONSOLE</p>
          <h2>${esc(driverName)} · Documents</h2>
          <p class="muted">All identity, driving, and vehicle documents are collected and physically checked by Virgo operations staff.</p>
        </div>
        <button class="picker-close" aria-label="Close">×</button>
      </div>
      <div class="detail-row">
        <span>Operating Status Eligibility:</span>
        ${data.can_go_online ? '<span class="badge verified">Eligible to go Online</span>' : '<span class="badge rejected">Blocked from going Online</span>'}
      </div>
      ${data.blocking_reasons.length ? `<div class="doc-rejection-box"><strong>Compliance Blockers:</strong><ul>${data.blocking_reasons.map(r => `<li>${esc(r)}</li>`).join('')}</ul></div>` : ''}
      <div class="doc-grid">
        ${data.documents.map(doc => `
          <article class="doc-card">
            <div class="doc-card-head">
              <strong>${esc(doc.label)}</strong>
              ${badge(doc.verification_status)}
            </div>
            <p><strong>Document number:</strong> ${esc(doc.document_number || 'Not provided')}</p>
            ${doc.expires_at ? `<p><strong>Expiry:</strong> ${new Date(doc.expires_at).toLocaleDateString()} ${doc.expiry_status === 'expired' ? '<span class="badge expired">EXPIRED</span>' : doc.expiry_status === 'expiring_soon' ? '<span class="badge expiring_soon">EXPIRING SOON</span>' : ''}</p>` : ''}
            ${doc.expiry_warning ? `<div class="doc-expiry-warning">${esc(doc.expiry_warning)}</div>` : ''}
            ${doc.rejection_reason ? `<div class="doc-rejection-box"><strong>Rejection reason:</strong> ${esc(doc.rejection_reason)}</div>` : ''}
            ${doc.reviewed_by ? `<p class="muted" style="font-size:12px;">Verified by: ${esc(doc.reviewed_by)} ${doc.reviewed_at ? 'on ' + new Date(doc.reviewed_at).toLocaleDateString() : ''}</p>` : ''}
            <div class="actions">
              ${doc.has_file ? `<button class="secondary btn-sm" data-preview-type="${doc.document_type}">Preview</button>` : ''}
              ${has('documents:upload') ? `<button class="secondary btn-sm" data-upload-type="${doc.document_type}" data-label="${esc(doc.label)}" data-number="${esc(doc.document_number || '')}" data-exp="${doc.expires_at ? doc.expires_at.slice(0, 10) : ''}">${doc.has_file ? 'Replace File' : 'Upload File'}</button>` : ''}
              ${doc.has_file && doc.verification_status !== 'verified' && has('documents:review') ? `<button class="approve btn-sm" data-doc-approve="${doc.document_type}">Approve</button>` : ''}
              ${doc.has_file && doc.verification_status !== 'rejected' && has('documents:review') ? `<button class="reject btn-sm" data-doc-reject="${doc.document_type}">Reject</button>` : ''}
              ${doc.has_file && has('documents:delete') ? `<button class="reject btn-sm" style="background:#fee2e2;" data-doc-delete="${doc.document_type}">Delete</button>` : ''}
            </div>
          </article>
        `).join('')}
      </div>
    </section>`;
    document.body.appendChild(overlay);
    const close = () => overlay.remove();
    overlay.addEventListener('click', e => { if (e.target === overlay || e.target.closest('.picker-close')) close(); });

    overlay.querySelectorAll('[data-preview-type]').forEach(btn => btn.addEventListener('click', () => previewDriverDocument(driverId, btn.dataset.previewType)));
    overlay.querySelectorAll('[data-doc-approve]').forEach(btn => btn.addEventListener('click', async () => {
      await reviewDocument(driverId, btn.dataset.docApprove, 'verified');
      close();
      openDriverDocumentsModal(driverId, driverName);
    }));
    overlay.querySelectorAll('[data-doc-reject]').forEach(btn => btn.addEventListener('click', async () => {
      await reviewDocument(driverId, btn.dataset.docReject, 'rejected');
      close();
      openDriverDocumentsModal(driverId, driverName);
    }));
    overlay.querySelectorAll('[data-doc-delete]').forEach(btn => btn.addEventListener('click', async () => {
      if (!confirm(`Are you sure you want to delete the ${btn.dataset.docDelete} file?`)) return;
      try {
        await api(`/admin/drivers/${driverId}/documents/${btn.dataset.docDelete}`, { method: 'DELETE' });
        close();
        openDriverDocumentsModal(driverId, driverName);
      } catch (err) { alert(err.message); }
    }));
    overlay.querySelectorAll('[data-upload-type]').forEach(btn => btn.addEventListener('click', () => {
      openUploadModal(driverId, btn.dataset.uploadType, btn.dataset.label, btn.dataset.number, btn.dataset.exp, () => {
        close();
        openDriverDocumentsModal(driverId, driverName);
      });
    }));
  } catch (err) {
    alert(err.message);
  }
}

function openUploadModal(driverId, docType, docLabel, existingNumber, existingExpiry, onComplete) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `<section class="upload-modal" role="dialog" aria-modal="true">
    <div class="picker-head">
      <div>
        <p class="eyebrow">UPLOAD VERIFIED DOCUMENT</p>
        <h3>${esc(docLabel)}</h3>
      </div>
      <button class="picker-close" aria-label="Close">×</button>
    </div>
    <form id="upload-doc-form" class="upload-form">
      <label>Document Number *
        <input type="text" name="document_number" value="${esc(existingNumber)}" required placeholder="e.g. DL-1234567890" />
      </label>
      <label>Expiry Date (if applicable)
        <input type="date" name="expires_at" value="${esc(existingExpiry)}" />
      </label>
      <label>Choose File (PDF, PNG, JPG, WebP - Max 5MB) *
        <input type="file" name="file" accept=".pdf,.png,.jpg,.jpeg,.webp" required />
      </label>
      <p id="upload-error" class="error"></p>
      <button class="primary" type="submit">Upload &amp; Save</button>
    </form>
  </section>`;
  document.body.appendChild(overlay);
  const close = () => overlay.remove();
  overlay.addEventListener('click', e => { if (e.target === overlay || e.target.closest('.picker-close')) close(); });

  const form = overlay.querySelector('#upload-doc-form');
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    const errBox = overlay.querySelector('#upload-error');
    errBox.textContent = '';
    btn.disabled = true;
    btn.textContent = 'Uploading securely...';

    const formData = new FormData(form);
    try {
      const response = await fetch(`/api/v1/admin/drivers/${driverId}/documents/${docType}/upload`, {
        method: 'POST',
        headers: { ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}) },
        body: formData,
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = Array.isArray(body.detail) ? body.detail.map(item => item.msg).join(' ') : body.detail;
        throw new Error(detail || 'Upload failed.');
      }
      close();
      if (onComplete) onComplete();
    } catch (err) {
      errBox.textContent = err.message;
      btn.disabled = false;
      btn.textContent = 'Upload & Save';
    }
  });
}

function openPreviewModal(previewUrl, docLabel) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  const isImage = /\.(png|jpe?g|webp)($|\?)/i.test(previewUrl);
  overlay.innerHTML = `<section class="preview-modal" role="dialog" aria-modal="true">
    <div class="picker-head">
      <div>
        <p class="eyebrow">DOCUMENT PREVIEW</p>
        <h3>${esc(docLabel)}</h3>
      </div>
      <button class="picker-close" aria-label="Close">×</button>
    </div>
    ${isImage
      ? `<img class="preview-img" src="${esc(previewUrl)}" alt="${esc(docLabel)}" />`
      : `<iframe class="preview-frame" src="${esc(previewUrl)}"></iframe>`}
  </section>`;
  document.body.appendChild(overlay);
  const close = () => overlay.remove();
  overlay.addEventListener('click', e => { if (e.target === overlay || e.target.closest('.picker-close')) close(); });
}
async function support() {
  const items = await api('/admin/support-tickets');
  content.innerHTML = items.length ? `<div class="list">${items.map(item => `<article class="item"><div class="item-head"><h3>${esc(item.subject)}</h3>${badge(item.status)}</div><p>${esc(item.passenger_name)} · ${esc(item.category)} · ${new Date(item.created_at).toLocaleDateString()}</p><p>${esc(item.description)}</p>${item.resolution_note ? `<p><strong>Resolution:</strong> ${esc(item.resolution_note)}</p>` : ''}<div class="actions"><button class="secondary" data-ticket="${item.id}" data-status="in_progress">Mark in progress</button><button class="approve" data-ticket="${item.id}" data-status="resolved">Resolve</button></div></article>`).join('')}</div>` : '<div class="panel empty">No support tickets require action.</div>';
  document.querySelectorAll('[data-ticket]').forEach(button => button.addEventListener('click', () => updateTicket(button.dataset.ticket, button.dataset.status)));
}
async function updateTicket(ticketId, status) { const resolution_note = status === 'resolved' ? prompt('Add a resolution note:') : null; if (status === 'resolved' && !resolution_note) return; try { await api(`/admin/support-tickets/${ticketId}`, { method: 'PATCH', body: JSON.stringify({ status, resolution_note }) }); await support(); } catch (err) { error.textContent = err.message; } }
async function outstation() {
  const items = await api('/admin/outstation-bookings');
  content.innerHTML = items.length ? `<div class="list">${items.map(item => `<article class="item outstation-item"><div class="item-head"><h3>Booking #${item.id} · ${esc(item.passenger_name)}</h3>${badge(item.status)}</div><div class="booking-flow">${['Request','Confirm','Assign driver'].map((label,index) => `<span class="${outstationStage(item.status) >= index ? 'done' : ''}"><b>${index + 1}</b>${label}</span>`).join('')}</div><p>${esc(localPhone(item.passenger_phone_number))} · ${new Date(item.scheduled_at).toLocaleString('en-IN')}</p><p><strong>${esc(item.pickup_address)}</strong> → <strong>${esc(item.destination_address)}</strong></p><p>Preference: ${esc(item.preferred_vehicle_type || 'Any car')} · ${item.estimated_distance_km ? `${item.estimated_distance_km} km routed` : 'Route unavailable'} · ${item.estimated_fare_paise ? `Estimated ₹${Math.round(item.estimated_fare_paise / 100).toLocaleString('en-IN')}` : 'Estimate unavailable'}</p>${item.driver_name ? `<div class="assigned-driver"><strong>${esc(item.driver_name)}</strong><span>${esc(localPhone(item.driver_phone_number))} · ${esc(item.vehicle_name)} · ${esc(item.vehicle_registration_number)}</span></div>` : ''}<div class="actions">${item.status === 'requested' ? `<button class="approve" data-outstation="confirm" data-id="${item.id}">Confirm request &amp; estimate</button><button class="reject" data-outstation="reject" data-id="${item.id}">Reject</button>` : ''}${item.status === 'confirmed' ? `<button class="approve" data-outstation="assign" data-id="${item.id}">Choose eligible driver</button>` : ''}${item.status === 'driver_assigned' ? `<button class="secondary" data-outstation="complete" data-id="${item.id}">Mark completed</button>` : ''}</div></article>`).join('')}</div>` : '<div class="panel empty">No outstation bookings require attention.</div>';
  document.querySelectorAll('[data-outstation]').forEach(button => button.addEventListener('click', () => button.dataset.outstation === 'assign' ? openDriverPicker(Number(button.dataset.id)) : updateOutstation(Number(button.dataset.id), button.dataset.outstation)));
}
function outstationStage(status) { return status === 'requested' ? 0 : status === 'confirmed' ? 1 : ['driver_assigned','completed'].includes(status) ? 2 : -1; }
async function openDriverPicker(bookingId) {
  try {
    const drivers = await api(`/admin/outstation-bookings/${bookingId}/eligible-drivers`);
    const overlay = document.createElement('div'); overlay.className = 'modal-overlay';
    overlay.innerHTML = `<section class="driver-picker" role="dialog" aria-modal="true"><div class="picker-head"><div><p class="eyebrow">BOOKING #${bookingId}</p><h2>Choose an eligible driver</h2><p class="muted">Only active drivers with verified vehicles and no schedule conflict are shown.</p></div><button class="picker-close" aria-label="Close">×</button></div>${drivers.length ? `<div class="driver-options">${drivers.map(driver => `<article class="driver-option"><div><h3>${esc(driver.full_name)}</h3><p>${esc(driver.phone_number)} · ${esc(driver.operating_city || 'City not set')}</p><p>${esc(driver.vehicle_name)} · ${esc(driver.vehicle_registration_number)} · ${driver.seat_count} seats</p><span>★ ${driver.rating || 'New'} · ${driver.completed_rides} completed rides</span></div><button class="approve" data-assign-phone="${esc(driver.phone_number)}">Assign driver</button></article>`).join('')}</div>` : '<div class="empty">No eligible driver is available for this schedule.</div>'}</section>`;
    document.body.appendChild(overlay);
    const close = () => overlay.remove();
    overlay.addEventListener('click', event => { if (event.target === overlay || event.target.closest('.picker-close')) close(); });
    overlay.querySelectorAll('[data-assign-phone]').forEach(button => button.addEventListener('click', async () => { button.disabled = true; button.textContent = 'Assigning…'; try { await api(`/admin/outstation-bookings/${bookingId}`, { method:'PATCH', body:JSON.stringify({ status:'driver_assigned', driver_phone_number:button.dataset.assignPhone }) }); close(); await outstation(); } catch (err) { button.disabled = false; button.textContent = 'Assign driver'; error.textContent = err.message; } }));
  } catch (err) { error.textContent = err.message; }
}
async function updateOutstation(id, action) { let body; if (action === 'confirm') { if (!confirm('Confirm the routed fare estimate and accept this booking for support fulfilment?')) return; body = { status:'confirmed' }; } else if (action === 'reject') { const note = prompt('Reason for rejecting this request:'); if (!note) return; body = { status:'rejected', support_note:note }; } else body = { status:'completed' }; try { await api(`/admin/outstation-bookings/${id}`, { method:'PATCH', body:JSON.stringify(body) }); await outstation(); } catch (err) { error.textContent = err.message; } }
async function account() {
  state.admin = await api('/admin/auth/me'); sessionStorage.setItem('virgo-admin-profile', JSON.stringify(state.admin));
  content.innerHTML = `<div class="account-grid"><section class="panel"><h2>Admin ID</h2><div class="detail-row"><span class="muted">ID</span><strong>${state.admin.id}</strong></div><div class="detail-row"><span class="muted">Email</span><strong>${esc(state.admin.email)}</strong></div><div class="detail-row"><span class="muted">Role</span>${badge(state.admin.role)}</div><div class="detail-row"><span class="muted">Last login</span><strong>${state.admin.last_login_at ? new Date(state.admin.last_login_at).toLocaleString() : 'First session'}</strong></div><h2>Role permissions</h2><div class="permission-list">${state.admin.permissions.map(permission => badge(permission.replace(':', '_'))).join('')}</div></section><form id="password-form" class="panel account-form"><h2>Security maintenance</h2><p class="muted">Changing your password immediately closes every existing Admin session.</p><label>Current password<input id="current-password" type="password" autocomplete="current-password" minlength="8" required /></label><label>New password<input id="new-password" type="password" autocomplete="new-password" minlength="12" required /></label><label>Confirm new password<input id="confirm-password" type="password" autocomplete="new-password" minlength="12" required /></label><p id="password-error" class="error" role="alert"></p><button class="primary" type="submit">Change password</button></form></div>`;
  document.querySelector('#password-form').addEventListener('submit', changePassword);
}
async function changePassword(event) { event.preventDefault(); const message = document.querySelector('#password-error'); const current = document.querySelector('#current-password').value; const next = document.querySelector('#new-password').value; const confirm = document.querySelector('#confirm-password').value; if (next !== confirm) { message.textContent = 'New passwords do not match.'; return; } const button = event.currentTarget.querySelector('button'); button.disabled = true; try { const result = await api('/admin/auth/change-password', { method: 'POST', body: JSON.stringify({ current_password: current, new_password: next }) }); alert(result.message); clearSession(); } catch (err) { message.textContent = err.message; } finally { button.disabled = false; } }
function labelDocument(value) { return ({ driving_licence: 'Driving licence', vehicle_registration: 'Vehicle registration', aadhaar: 'Aadhaar card', vehicle_insurance: 'Vehicle insurance' })[value] || value; }

if (state.token && state.admin) api('/admin/auth/me').then(profile => { state.admin = profile; sessionStorage.setItem('virgo-admin-profile', JSON.stringify(profile)); showApp(); }).catch(clearSession); else showLogin();
