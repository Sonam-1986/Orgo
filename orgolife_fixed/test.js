
    const API = "http://127.0.0.1:8000/api/v1";

    const INDIA_DATA = {
      "Andhra Pradesh": ["Hyderabad", "Visakhapatnam", "Vijayawada"],
      "Arunachal Pradesh": ["Itanagar", "Tawang"],
      "Assam": ["Guwahati", "Dibrugarh"],
      "Bihar": ["Patna", "Gaya"],
      "Chhattisgarh": ["Raipur", "Bhilai"],
      "Goa": ["Panaji", "Margao"],
      "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
      "Haryana": ["Gurgaon", "Faridabad"],
      "Himachal Pradesh": ["Shimla", "Manali"],
      "Jharkhand": ["Ranchi", "Jamshedpur"],
      "Karnataka": ["Bangalore", "Mysore", "Hubli"],
      "Kerala": ["Trivandrum", "Kochi", "Calicut"],
      "Madhya Pradesh": ["Bhopal", "Indore"],
      "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
      "Manipur": ["Imphal"],
      "Meghalaya": ["Shillong"],
      "Mizoram": ["Aizawl"],
      "Nagaland": ["Kohima"],
      "Odisha": ["Bhubaneswar", "Cuttack"],
      "Punjab": ["Chandigarh", "Ludhiana", "Amritsar"],
      "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
      "Sikkim": ["Gangtok"],
      "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
      "Telangana": ["Hyderabad", "Warangal"],
      "Tripura": ["Agartala"],
      "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Noida"],
      "Uttarakhand": ["Dehradun", "Haridwar"],
      "West Bengal": ["Kolkata", "Howrah", "Siliguri"]
    };

    const ORGANS = ["Kidney", "Liver", "Heart", "Lung", "Pancreas", "Intestine", "Cornea", "Bone Marrow", "Skin"];

    const HOSPITAL_DATA = [
      { name: "AIIMS Delhi", reg: "AIIMS-DL-01", phone: "011-26588500", state: "Delhi", city: "New Delhi", addr: "Ansari Nagar, New Delhi" },
      { name: "Apollo Hospital Mumbai", reg: "APO-MH-02", phone: "022-33503350", state: "Maharashtra", city: "Mumbai", addr: "Belapur, Navi Mumbai" },
      { name: "Fortis Bangalore", reg: "FOR-KA-03", phone: "080-66214444", state: "Karnataka", city: "Bangalore", addr: "Bannerghatta Road" },
      { name: "CMC Vellore", reg: "CMC-TN-04", phone: "0416-2281000", state: "Tamil Nadu", city: "Chennai", addr: "Ida Scudder Road, Vellore" },
      { name: "Medanta Gurgaon", reg: "MED-HR-05", phone: "0124-4141414", state: "Haryana", city: "Gurgaon", addr: "CH Baktawar Singh Road" },
      { name: "Max Saket Delhi", reg: "MAX-DL-06", phone: "011-26515050", state: "Delhi", city: "New Delhi", addr: "Saket Institutional Area" },
      { name: "Manipal Goa", reg: "MAN-GA-07", phone: "0832-3048800", state: "Goa", city: "Panaji", addr: "Dona Paula" },
      { name: "Lilavati Mumbai", reg: "LIL-MH-08", phone: "022-26751000", state: "Maharashtra", city: "Mumbai", addr: "Bandra West" },
      { name: "PGIMER Chandigarh", reg: "PGI-PB-09", phone: "0172-2747585", state: "Punjab", city: "Chandigarh", addr: "Sector 12" },
      { name: "AMRI Kolkata", reg: "AMR-WB-10", phone: "033-66800000", state: "West Bengal", city: "Kolkata", addr: "Dhakuria" },
      { name: "KIMS Hyderabad", reg: "KIM-TL-11", phone: "040-44885000", state: "Telangana", city: "Hyderabad", addr: "Minister Road" },
      { name: "Narayana Health", reg: "NAR-KA-12", phone: "080-71222222", state: "Karnataka", city: "Bangalore", addr: "Bommasandra" },
      { name: "Ruby General", reg: "RUB-WB-13", phone: "033-66871800", state: "West Bengal", city: "Kolkata", addr: "EM Bypass" },
      { name: "Sir Ganga Ram", reg: "SGR-DL-14", phone: "011-25735205", state: "Delhi", city: "New Delhi", addr: "Rajinder Nagar" },
      { name: "Nanavati Mumbai", reg: "NAN-MH-15", phone: "022-26267500", state: "Maharashtra", city: "Mumbai", addr: "S.V. Road" },
      { name: "Sankara Nethralaya", reg: "SAN-TN-16", phone: "044-42271500", state: "Tamil Nadu", city: "Chennai", addr: "College Road" },
      { name: "Tata Memorial", reg: "TAT-MH-17", phone: "022-24177000", state: "Maharashtra", city: "Mumbai", addr: "Parel" },
      { name: "Yashoda Hyderabad", reg: "YAS-TL-18", phone: "040-45674567", state: "Telangana", city: "Hyderabad", addr: "Somajiguda" },
      { name: "Global Chennai", reg: "GLO-TN-19", phone: "044-44777000", state: "Tamil Nadu", city: "Chennai", addr: "Perumbakkam" },
      { name: "Kokilaben Ambani", reg: "KOK-MH-20", phone: "022-42696969", state: "Maharashtra", city: "Mumbai", addr: "Andheri West" }
    ];

    /* UI HELPERS */
    function goPage(p) {
      document.querySelectorAll('.page').forEach(e => e.classList.remove('active'));
      document.querySelectorAll('.nav-pill').forEach(e => e.classList.remove('active'));
      document.getElementById('p-' + p.split('-')[0])?.classList.add('active');

      if (p === 'donor-flow') {
        if (localStorage.getItem('token')) {
          if (localStorage.getItem('role') === 'donor') goPage('donor-organ');
          else toast("Switch role or logout to continue", "error");
        } else { document.getElementById('donor-reg-page').classList.add('active'); }
      } else if (p === 'receiver-flow') {
        if (localStorage.getItem('token') && localStorage.getItem('role') === 'receiver') goPage('search');
        else { document.getElementById('receiver-reg-page').classList.add('active'); }
      } else {
        document.getElementById(p + '-page').classList.add('active');
      }

      // Trigger data loads for specific tabs
      if (p === 'profile') loadProfile();
      if (p === 'admin-dash' && !window.dashType) setDashTab('donor'); // Auto load first tab

      window.scrollTo(0, 0);
    }

    function popStates(selId) {
      const sel = document.getElementById(selId);
      if (!sel) return;
      sel.innerHTML = '<option value="">-- State --</option>';
      Object.keys(INDIA_DATA).forEach(s => sel.innerHTML += `<option value="${s}">${s}</option>`);
    }

    function popCities(state, selId) {
      const sel = document.getElementById(selId);
      sel.innerHTML = '<option value="">-- City --</option>';
      if (INDIA_DATA[state]) INDIA_DATA[state].forEach(c => sel.innerHTML += `<option value="${c}">${c}</option>`);
    }

    function autoFillHospital(name) {
      const h = HOSPITAL_DATA.find(x => x.name === name);
      if (h) {
        document.getElementById('ar_hreg').value = h.reg;
        document.getElementById('ar_hphone').value = h.phone;
        document.getElementById('ar_hstate').value = h.state;
        document.getElementById('ar_hcity').value = h.city;
        document.getElementById('ar_haddr').value = h.addr;
      }
    }

    function handleFile(inp, lblId, slotId) {
      if (inp.files.length) {
        document.getElementById(lblId).innerText = inp.files[0].name;
        document.getElementById(slotId).classList.add('filled');
      }
    }

    function toast(m, type = 'info') {
      const w = document.getElementById('toast-wrap');
      if (!w) return;

      const formatMsg = (msg) => {
        if (Array.isArray(msg)) {
          return msg.map(e => formatMsg(e)).join(", ");
        }
        if (typeof msg === 'object' && msg !== null) {
          if (msg.message && msg.field) return `${msg.field}: ${msg.message}`;
          if (msg.message) return msg.message;
          if (msg.msg) return msg.msg;
          if (msg.detail) return formatMsg(msg.detail);
          return JSON.stringify(msg);
        }
        return String(msg);
      };

      const text = formatMsg(m);
      const e = document.createElement('div');
      e.className = 'toast';
      let color = '#D4AF37';
      if (type === 'error') color = '#EF4444';
      if (type === 'success') color = '#10B981';
      e.style.borderLeftColor = color;
      e.innerText = text;
      w.appendChild(e);
      setTimeout(() => { e.style.opacity = '0'; setTimeout(() => e.remove(), 400); }, 4000);
    }

    function toggleAdminBox(t) {
      document.getElementById('admin-login-box').style.display = t === 'login' ? 'block' : 'none';
      document.getElementById('admin-reg-box').style.display = t === 'reg' ? 'block' : 'none';
      document.getElementById('btn-al').classList.toggle('active', t === 'login');
      document.getElementById('btn-ar').classList.toggle('active', t === 'reg');
    }

    function toggleDonorBox(t) {
      document.getElementById('donor-login-box').style.display = t === 'login' ? 'block' : 'none';
      document.getElementById('donor-reg-box').style.display = t === 'reg' ? 'block' : 'none';
      document.getElementById('btn-dl').classList.toggle('active', t === 'login');
      document.getElementById('btn-dr').classList.toggle('active', t === 'reg');
    }

    function toggleReceiverBox(t) {
      document.getElementById('receiver-login-box').style.display = t === 'login' ? 'block' : 'none';
      document.getElementById('receiver-reg-box').style.display = t === 'reg' ? 'block' : 'none';
      document.getElementById('btn-rl').classList.toggle('active', t === 'login');
      document.getElementById('btn-rr').classList.toggle('active', t === 'reg');
    }

    /* CORE EXECUTION */
    async function submitDonorReg() {
      const btn = event.target;
      const originalText = btn.innerText;
      btn.innerText = "Processing registration...";
      btn.disabled = true;

      const fd = new FormData();
      fd.append('name', document.getElementById('d_name').value);
      fd.append('email', document.getElementById('d_email').value);
      fd.append('password', document.getElementById('d_pass').value);
      fd.append('contact_number', document.getElementById('d_phone').value);
      fd.append('age', document.getElementById('d_age').value);
      fd.append('father_name', document.getElementById('d_father').value);
      fd.append('state', document.getElementById('d_state').value);
      fd.append('city', document.getElementById('d_city').value);
      fd.append('full_address', document.getElementById('d_addr').value);
      fd.append('aadhaar_file', document.getElementById('f-d-aa').files[0]);
      fd.append('pan_file', document.getElementById('f-d-pn').files[0]);
      fd.append('medical_file', document.getElementById('f-d-rep').files[0]);

      try {
        const res = await fetch(`${API}/auth/register/donor`, { method: 'POST', body: fd });
        const d = await res.json();
        if (res.ok) {
          toast("Registration Successful!", "success");
          setTimeout(() => loginFast(document.getElementById('d_email').value, document.getElementById('d_pass').value, 'donor'), 1000);
        } else {
          toast(d.detail || d.message || "Signup error", "error");
          btn.innerText = originalText;
          btn.disabled = false;
        }
      } catch (e) {
        toast("Network error: " + e.message, "error");
        btn.innerText = originalText;
        btn.disabled = false;
      }
    }

    async function submitReceiverReg() {
      const btn = event.target;
      const originalText = btn.innerText;
      btn.innerText = "Setting up account...";
      btn.disabled = true;

      const fd = new FormData();
      fd.append('name', document.getElementById('r_name').value);
      fd.append('email', document.getElementById('r_email').value);
      fd.append('password', document.getElementById('r_pass').value);
      fd.append('contact_number', document.getElementById('r_phone').value);
      fd.append('age', document.getElementById('r_age').value);
      fd.append('father_name', document.getElementById('r_father').value);
      fd.append('state', document.getElementById('r_state').value);
      fd.append('city', document.getElementById('r_city').value);
      fd.append('aadhaar_file', document.getElementById('f-r-aa').files[0]);
      fd.append('pan_file', document.getElementById('f-r-pn').files[0]);
      fd.append('medical_file', document.getElementById('f-r-rep').files[0]);

      try {
        const res = await fetch(`${API}/auth/register/receiver`, { method: 'POST', body: fd });
        const d = await res.json();
        if (res.ok) {
          toast("Account Created Successfully!", "success");
          setTimeout(() => loginFast(document.getElementById('r_email').value, document.getElementById('r_pass').value, 'receiver'), 1000);
        } else {
          toast(d.detail || d.message || "Creation failed. Please try again.", "error");
          btn.innerText = originalText;
          btn.disabled = false;
        }
      } catch (e) {
        toast("Network error: " + e.message, "error");
        btn.innerText = originalText;
        btn.disabled = false;
      }
    }

    async function loginFast(email, pass, role) {
      const res = await fetch(`${API}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password: pass })
      });
      const d = await res.json();
      if (res.ok) {
        localStorage.setItem('token', d.access_token);
        localStorage.setItem('name', d.name);
        localStorage.setItem('role', d.role);
        initSession();
        goPage(d.role === 'donor' ? 'donor-organ' : 'search');
      }
    }

    async function submitOrganReg() {
      const token = localStorage.getItem('token');
      const hosps = Array.from(document.querySelectorAll('.hosp-check:checked')).map(c => c.value);
      const body = {
        organ_name: document.getElementById('o_organ').value,
        blood_group: document.getElementById('o_blood').value,
        health_report: document.getElementById('o_health').value,
        hospitals_selected: hosps,
        state: document.getElementById('o_state').value,
        city: document.getElementById('o_city').value
      };
      const res = await fetch(`${API}/donors/organs`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const d = await res.json();
      if (res.ok) { toast("Organ Registration Successful!", "success"); location.reload(); }
      else { toast(d.detail || d.message || "Organ registration failed.", "error"); }
    }

    async function executeSearch() {
      const token = localStorage.getItem('token');
      const body = {
        organ_type: document.getElementById('s_organ').value,
        blood_group: document.getElementById('s_blood').value,
        verified_donor: document.getElementById('s_ver').value === 'yes' ? 'yes' : 'all',
        state: document.getElementById('s_state').value
      };
      const res = await fetch(`${API}/receivers/search`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const d = await res.json();
      if (!res.ok) { toast(d.detail || d.message || "Search failed", "error"); return; }
      const box = document.getElementById('search-results');
      box.innerHTML = '';
      const items = d.data.items || [];
      if (items.length === 0) box.innerHTML = '<div class="p-4 text-center">No matching donors found.</div>';
      items.forEach(it => {
        const isVerified = (it.verification_status === 'legal' || it.verification_status === 'verified');
        const vBadge = isVerified ? `<span class="status-badge status-legal" style="float: right;">✓ Verified</span>` : `<span class="status-badge status-pending" style="float: right;">Pending</span>`;
        const initial = it.donor_name ? it.donor_name.charAt(0).toUpperCase() : 'U';
        
        box.innerHTML += `
      <div class="result-card" style="display: block; border-left: none; border: 1px solid var(--border); box-shadow: 0 4px 15px rgba(0,0,0,0.03); padding: 25px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px;">
          <div style="display: flex; gap: 15px; align-items: center;">
            <div style="width: 50px; height: 50px; border-radius: 50%; background: #C83E4D; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700;">${initial}</div>
            <div>
              <h3 style="margin: 0; font-family: var(--font-display); font-size: 1.2rem;">${it.donor_name}</h3>
              <p style="font-size: 0.85rem; color: var(--ink-subtle); margin: 0; margin-top: 3px;">S/o ${it.father_name || 'N/A'}</p>
              <p style="font-size: 0.85rem; color: var(--ink-subtle); margin: 0;">&middot; ${it.city || 'N/A'}, ${it.state || 'N/A'}</p>
            </div>
          </div>
          <div>${vBadge}</div>
        </div>
        
        <div style="background: var(--ivory); padding: 15px; border-radius: var(--radius); display: flex; gap: 30px; margin-bottom: 15px;">
          <div>
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--ink-subtle); margin-bottom: 5px;">Organ</div>
            <div style="font-weight: 700; font-size: 1rem; color: var(--ink);">${it.organ}</div>
          </div>
          <div>
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--ink-subtle); margin-bottom: 5px;">Blood Group</div>
            <div style="font-weight: 700; font-size: 1rem; color: #991b1b;">${it.blood_group}</div>
          </div>
          <div>
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--ink-subtle); margin-bottom: 5px;">Hospital</div>
            <div style="font-weight: 700; font-size: 1rem; color: var(--ink);">${it.hospital_verified_by || 'Awaiting'}</div>
          </div>
        </div>
        
        <div style="text-align: right;">
          <a href="#" onclick="alert('Viewing full profile functionality to be implemented'); return false;" style="color: var(--ink-subtle); text-decoration: none; font-size: 0.85rem; transition: 0.3s;" onmouseover="this.style.color='var(--ink)'" onmouseout="this.style.color='var(--ink-subtle)'">View full profile &rarr;</a>
        </div>
      </div>`;
      });
    }

    /* ADMIN LOGIC */
    async function executeAdminReg() {
      const hsel = document.getElementById('ar_hsel').value;
      if (!hsel) {
        toast("Please select a Hospital Entity first.", "error");
        return;
      }
      const fd = new FormData();
      fd.append('name', document.getElementById('ar_aname').value);
      fd.append('email', document.getElementById('ar_aemail').value);
      fd.append('password', document.getElementById('ar_apass').value);
      fd.append('contact_number', document.getElementById('ar_aphone').value);
      fd.append('hospital_name', document.getElementById('ar_hsel').value);
      fd.append('hospital_registration_number', document.getElementById('ar_hreg').value);
      fd.append('hospital_state', document.getElementById('ar_hstate').value);
      fd.append('hospital_city', document.getElementById('ar_hcity').value);
      fd.append('hospital_address', document.getElementById('ar_haddr').value);
      fd.append('hospital_contact', document.getElementById('ar_hphone').value);

      try {
        const res = await fetch(`${API}/auth/register/admin`, { method: 'POST', body: fd });
        const d = await res.json();
        if (res.ok) {
          toast("Hospital License Verified & Registered!", "success");
          setTimeout(() => {
            toggleAdminBox('login');
            document.getElementById('al_email').value = document.getElementById('ar_aemail').value;
            toast("Please log in with your new admin credentials.", "info");
          }, 1500);
        } else {
          toast(d.detail || d.message || "Hospital registration failed.", "error");
        }
      } catch (e) {
        toast("Network error: " + e.message, "error");
      }
    }

    async function executeAdminLogin() {
      const res = await fetch(`${API}/auth/login/admin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: document.getElementById('al_email').value, password: document.getElementById('al_pass').value,
          hospital_code: document.getElementById('al_code').value
        })
      });
      const d = await res.json();
      if (res.ok) {
        localStorage.setItem('token', d.access_token);
        localStorage.setItem('name', 'Admin');
        localStorage.setItem('role', 'admin');
        initSession();
        goPage('admin-dash');
      } else {
        toast(d.detail || d.message || "Admin login failed.", "error");
      }
    }

    async function loadDashboard(type) {
      window.dashType = type;
      if (type === 'stats') return loadStats();

      const token = localStorage.getItem('token');
      document.getElementById('tab-don').classList.toggle('active', type === 'donor');
      document.getElementById('tab-rec').classList.toggle('active', type === 'receiver');

      const endpoint = type === 'donor' ? '/admin/donors' : '/admin/receivers';
      const res = await fetch(`${API}${endpoint}`, { headers: { 'Authorization': `Bearer ${token}` } });
      const d = await res.json();
      if (!res.ok) { toast(d.detail || d.message || "Failed to load dashboard data.", "error"); return; }

      const thead = document.getElementById('admin-thead');
      const tbody = document.getElementById('admin-tbody');

      thead.innerHTML = type === 'donor'
        ? '<tr><th>Donor</th><th>ID Info</th><th>Docs</th><th>Status</th><th>Actions</th></tr>'
        : '<tr><th>Receiver</th><th>Priority Info</th><th>Docs</th><th>Status</th><th>Actions</th></tr>';

      tbody.innerHTML = '';
      const items = d.data.items || [];
      items.forEach(it => {
        const itId = type === 'donor' ? it.donor_id : it.receiver_id;
        
        // Escape data for function call
        const escName = it.name ? encodeURIComponent(it.name) : '';
        const escFather = it.father_name ? encodeURIComponent(it.father_name) : '';
        const escCont = it.contact_number ? encodeURIComponent(it.contact_number) : '';
        const escOrg = it.organ_name ? encodeURIComponent(it.organ_name) : (it.organ ? encodeURIComponent(it.organ) : '');
        
        const btnCall = `viewAdminProfile(decodeURIComponent('${escName}'), decodeURIComponent('${escFather}'), '${it.age}', decodeURIComponent('${escCont}'), decodeURIComponent('${escOrg}'), '${it.aadhaar_card_url}', '${it.pan_card_url}', '${it.medical_report_url}')`;

        tbody.innerHTML += `
      <tr>
        <td><b>${it.name}</b><br><small>${it.email}</small></td>
        <td>Age: ${it.age}<br>${it.city}, ${it.state}</td>
        <td>
          <div style="display:flex; flex-direction:column; gap:5px;">
            <a href="${it.aadhaar_card_url}" target="_blank" class="doc-btn">📄 Aadhaar Card</a>
            <a href="${it.pan_card_url}" target="_blank" class="doc-btn">💳 PAN Card</a>
            <a href="${it.medical_report_url}" target="_blank" class="doc-btn">🏥 Medical Report</a>
          </div>
        </td>
        <td><span class="status-badge">${it.status || 'pending'}</span></td>
        <td>
          <button class="action-btn" style="background:var(--ink); color:#fff; width:100%; margin-bottom:5px;" onclick="${btnCall}">View Profile</button>
          <div style="display:flex;">
            <button class="action-btn btn-approve" style="flex:1;" onclick="verifyAction('${itId}', 'approve')">Approve</button>
            <button class="action-btn btn-reject" style="flex:1; margin-right:0;" onclick="verifyAction('${itId}', 'reject')">Reject</button>
          </div>
        </td>
      </tr>`;
      });
    }

    function viewAdminProfile(name, father, age, contact, organ, doc_aa, doc_pan, doc_med) {
        const typeStr = window.dashType === 'donor' ? 'Donor' : 'Receiver';
        document.getElementById('apm-type').innerText = typeStr + ' Profile Information';
        const organLabel = window.dashType === 'donor' ? 'Organ Donate' : 'Organ to Receive';
        
        document.getElementById('apm-content').innerHTML = `
            <div class="profile-row" style="padding: 10px 0;"><b style="text-transform: uppercase;">Name</b> <span style="font-weight: 500;">${name || 'N/A'}</span></div>
            <div class="profile-row" style="padding: 10px 0;"><b style="text-transform: uppercase;">Father Name</b> <span style="font-weight: 500;">${father || 'N/A'}</span></div>
            <div class="profile-row" style="padding: 10px 0;"><b style="text-transform: uppercase;">Age</b> <span style="font-weight: 500;">${age || 'N/A'}</span></div>
            <div class="profile-row" style="padding: 10px 0;"><b style="text-transform: uppercase;">Contact No.</b> <span style="font-weight: 500;">${contact || 'N/A'}</span></div>
            <div class="profile-row" style="padding: 10px 0;"><b style="text-transform: uppercase;">${organLabel}</b> <span style="font-weight: 500;">${organ || 'N/A'}</span></div>
            <div style="margin-top: 20px;">
                <b style="font-size: 0.85rem; text-transform: uppercase; color: var(--ink-subtle); display:block; margin-bottom:10px;">Attached Documents</b>
                <div style="display:flex; flex-direction:column; gap:8px;">
                    <a href="${doc_pan && doc_pan !== 'null' ? doc_pan : '#'}" target="_blank" class="doc-btn" style="text-align: center;">💳 PAN Card</a>
                    <a href="${doc_aa && doc_aa !== 'null' ? doc_aa : '#'}" target="_blank" class="doc-btn" style="text-align: center;">📄 Aadhaar Card</a>
                    <a href="${doc_med && doc_med !== 'null' ? doc_med : '#'}" target="_blank" class="doc-btn" style="text-align: center;">🏥 Health Report</a>
                </div>
            </div>
        `;
        document.getElementById('admin-profile-modal').style.display = 'flex';
    }

    function setDashTab(t) {
      document.getElementById('admin-table-container').style.display = t === 'stats' ? 'none' : 'block';
      document.getElementById('admin-stats-container').style.display = t === 'stats' ? 'block' : 'none';

      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      if (t === 'donor') document.getElementById('tab-don').classList.add('active');
      if (t === 'receiver') document.getElementById('tab-rec').classList.add('active');
      if (t === 'stats') {
        document.getElementById('tab-sta').classList.add('active');
        loadStats();
      } else {
        loadDashboard(t);
      }
    }

    async function verifyAction(id, action) {
      const type = window.dashType === 'donor' ? 'donors' : 'receivers';
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`${API}/admin/${type}/${id}/${action}`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const d = await res.json();
        if (res.ok) {
          toast(`${action.charAt(0).toUpperCase() + action.slice(1)}ed!`, "success");
          loadDashboard(window.dashType);
        } else {
          toast(d.detail || d.message || "Action failed.", "error");
        }
      } catch (e) {
        toast("Action error: " + e.message, "error");
      }
    }

    async function loadProfile() {
      const token = localStorage.getItem('token');
      const box = document.getElementById('profile-content');
      try {
        const res = await fetch(`${API}/auth/profile`, { headers: { 'Authorization': `Bearer ${token}` } });
        const d = await res.json();

        // Fallback if token is dead or user was purged
        if (res.status === 401 || res.status === 404) {
          toast("Session expired or account not found. Please log in again.", "error");
          logout(); return;
        }

        if (!res.ok) throw new Error(d.detail || "Profile error");

        const p = d.data;
        if (!p) throw new Error("Could not retrieve profile data.");

        const joinedDate = p.created_at ? new Date(p.created_at).toLocaleDateString() : 'N/A';

        const initial = p.name ? p.name.charAt(0).toUpperCase() : 'U';
        const roleLabel = p.role ? (p.role.charAt(0).toUpperCase() + p.role.slice(1)) + ' Account' : 'User Account';

        if (p.role === 'donor') {
            const orgTitle = (p.donor_info && p.donor_info.organ_registrations && p.donor_info.organ_registrations.length > 0) ? p.donor_info.organ_registrations[0].organ_name : "Pending";
            const bloodTitle = (p.donor_info && p.donor_info.organ_registrations && p.donor_info.organ_registrations.length > 0) ? p.donor_info.organ_registrations[0].blood_group : "-";
            const vStatus = p.donor_info ? p.donor_info.status : "Pending";
            const vColor = vStatus.toLowerCase() === 'approved' ? '#064E3B' : (vStatus.toLowerCase() === 'rejected' ? 'var(--crimson)' : 'var(--gold-deep)');
            const vIcon = vStatus.toLowerCase() === 'approved' ? '🏥' : '⏳';

            box.innerHTML = `
              <div style="background: var(--ivory); padding: 25px; border-radius: 16px; margin-bottom: 30px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 20px;">
                  <div style="width: 60px; height: 60px; border-radius: 50%; background: var(--crimson-deep); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; font-weight: 700;">${initial}</div>
                  <div>
                    <h2 style="font-family: var(--font-display); margin: 0; font-size: 1.4rem; color: var(--ink);">${p.name || 'Anonymous'}</h2>
                    <p style="color: var(--ink-subtle); margin: 0; font-size: 0.9rem;">${roleLabel}</p>
                  </div>
                </div>
                <div style="background: #e6f4ea; color: #064E3B; padding: 12px 20px; border-radius: 50px; font-weight: 600; font-size: 0.85rem; border: 1px solid #c3e6cb;">Registered Donor</div>
              </div>

              <h2 style="font-family: var(--font-display); font-size: 2rem; margin-top: 30px; margin-bottom: 5px;">Your Donation Overview</h2>
              <p style="color: var(--ink-subtle); margin-bottom: 25px;">Track and manage your organ donation registration</p>

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                <div style="background: #fff; padding: 25px; border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 4px 10px rgba(0,0,0,0.03); text-align: center;">
                  <div style="font-size: 2.2rem; margin-bottom: 10px;">🖤</div>
                  <div style="color: var(--crimson); font-size: 1.3rem; font-weight: 700; text-transform: capitalize;">${orgTitle}</div>
                  <div style="font-size: 0.85rem; color: var(--ink-subtle);">Registered Organ</div>
                </div>
                <div style="background: #fff; padding: 25px; border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 4px 10px rgba(0,0,0,0.03); text-align: center;">
                  <div style="font-size: 2.2rem; margin-bottom: 10px;">🩸</div>
                  <div style="color: var(--crimson); font-size: 1.3rem; font-weight: 700;">${bloodTitle}</div>
                  <div style="font-size: 0.85rem; color: var(--ink-subtle);">Blood Group</div>
                </div>
                <div style="background: #fff; padding: 25px; border-radius: 16px; border: 1px solid var(--border); box-shadow: 0 4px 10px rgba(0,0,0,0.03); text-align: center;">
                  <div style="font-size: 2.2rem; margin-bottom: 10px;">${vIcon}</div>
                  <div style="color: ${vColor}; font-size: 1.3rem; font-weight: 700; text-transform: capitalize;">${vStatus}</div>
                  <div style="font-size: 0.85rem; color: var(--ink-subtle);">Verification Status</div>
                </div>
              </div>

              <h3 style="font-family: var(--font-display); font-size: 1.5rem; margin-bottom: 15px; border-bottom: 1px solid var(--border); padding-bottom: 10px;">Registration Summary</h3>
              <div style="display: flex; flex-direction: column;">
                <div class="profile-row"><b style="text-transform: uppercase;">Full Name</b> <span style="font-weight: 500; color: var(--ink);">${p.name || 'Anonymous'}</span></div>
                <div class="profile-row"><b style="text-transform: uppercase;">Email</b> <span style="font-weight: 500; color: var(--ink);">${p.email || 'N/A'}</span></div>
                <div class="profile-row"><b style="text-transform: uppercase;">Contact</b> <span style="font-weight: 500; color: var(--ink);">${p.contact_number || 'N/A'}</span></div>
                <div class="profile-row"><b style="text-transform: uppercase;">Joined</b> <span style="font-weight: 500; color: var(--ink);">${joinedDate}</span></div>
              </div>
            `;
            return;
        }

        let extra = '';
        if (p.role === 'hospital_admin' && p.hospital_info) {
          extra = `
          <div class="profile-row"><b style="text-transform: uppercase;">Hospital</b> <span style="font-weight: 500; color: var(--ink);">${p.hospital_info.name}</span></div>
          <div class="profile-row"><b style="text-transform: uppercase;">Reg Number</b> <span style="font-weight: 500; color: var(--ink);">${p.hospital_info.registration_number}</span></div>
        `;
        }

        box.innerHTML = `
      <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 40px;">
        <div style="width: 70px; height: 70px; border-radius: 50%; background: #2A6A4B; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 700;">${initial}</div>
        <div>
          <h2 style="font-family: var(--font-display); margin: 0; font-size: 1.6rem; color: var(--ink);">${p.name || 'Anonymous'}</h2>
          <p style="color: var(--ink-subtle); margin: 0; font-size: 0.95rem;">${roleLabel}</p>
        </div>
      </div>
      <div style="display: flex; flex-direction: column;">
        <div class="profile-row"><b style="text-transform: uppercase;">Full Name</b> <span style="font-weight: 500; color: var(--ink);">${p.name || 'Anonymous'}</span></div>
        <div class="profile-row"><b style="text-transform: uppercase;">Email</b> <span style="font-weight: 500; color: var(--ink);">${p.email || 'N/A'}</span></div>
        <div class="profile-row"><b style="text-transform: uppercase;">Contact</b> <span style="font-weight: 500; color: var(--ink);">${p.contact_number || 'N/A'}</span></div>
        ${extra}
        <div class="profile-row"><b style="text-transform: uppercase;">Joined</b> <span style="font-weight: 500; color: var(--ink);">${joinedDate}</span></div>
      </div>
    `;
      } catch (e) {
        box.innerHTML = `
        <div class="p-8 text-center" style="color:var(--crimson);">
            <p><b>Profile Load Failed</b></p>
            <p style="font-size:0.8rem; margin-top:5px;">${e.message}</p>
            <button onclick="logout()" class="doc-btn" style="margin-top:20px">Back to Login</button>
        </div>
    `;
      }
    }

    async function loadStats() {
      const token = localStorage.getItem('token');
      const box = document.getElementById('stats-grid');
      try {
        const res = await fetch(`${API}/admin/stats`, { headers: { 'Authorization': `Bearer ${token}` } });
        const d = await res.json(); if (!res.ok) throw new Error(d.detail);
        const s = d.data;
        box.innerHTML = `
            <div class="stat-box"><h3>${s.total_donors}</h3><p>TOTAL DONORS</p></div>
            <div class="stat-box"><h3>${s.verified_donors}</h3><p>VERIFIED DONORS</p></div>
            <div class="stat-box"><h3>${s.total_receivers}</h3><p>WAITING PATIENTS</p></div>
            <div class="stat-box"><h3>${s.total_hospitals}</h3><p>LINKED HOSPITALS</p></div>
            <div class="stat-box"><h3>${s.total_organs_listed}</h3><p>ORGANS PLEDGED</p></div>
            <div class="stat-box"><h3>${s.pending_verifications}</h3><p>PENDING REVIEW</p></div>
        `;
      } catch (e) { box.innerHTML = `<p>${e.message}</p>`; }
    }

    function initSession() {
      if (localStorage.getItem('token')) {
        document.getElementById('user-meta').style.display = 'flex';
        document.getElementById('user-name').innerText = localStorage.getItem('name');
      }
    }
    function logout() { localStorage.clear(); location.reload(); }

    /* DATA INIT */
    popStates('d_state'); popStates('r_state'); popStates('o_state'); popStates('s_state');
    ORGANS.forEach(o => {
      const val = o.toLowerCase().replace(" ", "_");
      document.getElementById('o_organ').innerHTML += `<option value="${val}">${o}</option>`;
      document.getElementById('s_organ').innerHTML += `<option value="${val}">${o}</option>`;
    });
    HOSPITAL_DATA.forEach(h => {
      document.getElementById('ar_hsel').innerHTML += `<option value="${h.name}">${h.name}</option>`;
      document.getElementById('hosp-checks').innerHTML += `<div><input type="checkbox" class="hosp-check" value="${h.name}"> ${h.name}</div>`;
    });
    initSession();
  