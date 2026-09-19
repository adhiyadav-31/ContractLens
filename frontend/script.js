// ===================================================================
// ContractLens — frontend/script.js
// Owner: Adhi. Talks to the backend only via the API contract
// (Section 14–16). Starts on mock data (Section 21); swap MOCK_MODE
// to false once Safa's endpoints are live.
// ===================================================================

const API_BASE = "http://localhost:8000";
const MOCK_MODE = true;

// -------------------------------------------------------------
// Mock data — shapes match Section 15 exactly (field names fixed)
// -------------------------------------------------------------

const MOCK_CONTRACTS = {
  CL001: {
    contract_id: "CL001",
    filename: "contract_v1.pdf",
    parties: ["ABC Corporation", "XYZ Technologies"],
    effective_date: "2026-01-01",
    expiration_date: "2026-12-31",
    renewal: { type: "automatic", notice_period_days: 60 },
    payment_terms: "Payment must be made within 30 days of invoice.",
    obligations: [
      {
        obligation_id: "OB001",
        party: "XYZ Technologies",
        action: "Submit monthly service report",
        deadline: "5th of every month",
        frequency: "monthly",
        status: "UPCOMING",
        source: { section: "7.2", page: 4 }
      },
      {
        obligation_id: "OB002",
        party: "ABC Corporation",
        action: "Pay outstanding invoice #114",
        deadline: "2026-09-25",
        frequency: null,
        status: "OVERDUE",
        source: { section: "8.1", page: 5 }
      },
      {
        obligation_id: "OB003",
        party: "XYZ Technologies",
        action: "Provide 60 days' notice before renewal",
        deadline: "2026-11-01",
        frequency: null,
        status: "DUE_SOON",
        source: { section: "10.1", page: 6 }
      }
    ],
    review_flags: [
      {
        type: "AUTO_RENEWAL",
        description: "Contract automatically renews unless notice is provided 60 days before expiration.",
        severity: "medium",
        source: { section: "10.1", page: 6 }
      },
      {
        type: "ONE_SIDED_OBLIGATION",
        description: "Termination rights appear to favor ABC Corporation. This may require review.",
        severity: "low",
        source: { section: "12.3", page: 7 }
      }
    ]
  },
  CL002: {
    contract_id: "CL002",
    filename: "contract_v2.pdf",
    parties: ["ABC Corporation", "XYZ Technologies"],
    effective_date: "2026-01-01",
    expiration_date: "2026-12-31",
    renewal: { type: "automatic", notice_period_days: 30 },
    payment_terms: "Payment must be made within 15 days of invoice.",
    obligations: [
      {
        obligation_id: "OB101",
        party: "XYZ Technologies",
        action: "Submit monthly service report",
        deadline: "5th of every month",
        frequency: "monthly",
        status: "UPCOMING",
        source: { section: "7.2", page: 4 }
      }
    ],
    review_flags: [
      {
        type: "SHORT_NOTICE_PERIOD",
        description: "Notice period for termination has been shortened to 30 days. Review recommended.",
        severity: "medium",
        source: { section: "10.1", page: 6 }
      }
    ]
  }
};

const MOCK_CHAT_ANSWERS = {
  default: {
    answer: "The contract does not specify that detail in the retrieved sections.",
    sources: []
  },
  payment: {
    answer: "Payment is due within 30 days of invoice.",
    sources: [{ page: 5, section: "8.1", text: "Payment must be made within 30 days of invoice." }]
  }
};

const MOCK_COMPARISON = {
  changes: [
    {
      category: "payment",
      description: "Payment period changed from 30 days to 15 days.",
      old_value: "30 days",
      new_value: "15 days"
    },
    {
      category: "renewal",
      description: "Termination notice period changed from 60 days to 30 days.",
      old_value: "60 days",
      new_value: "30 days"
    }
  ]
};

// -------------------------------------------------------------
// State
// -------------------------------------------------------------

let contractsCache = {}; // contract_id -> contract object
let selectedContractId = null;

// -------------------------------------------------------------
// Init
// -------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  loadContracts();
  document.getElementById("upload-form").addEventListener("submit", handleUpload);
  document.getElementById("file-input").addEventListener("change", handleFileChosen);
  document.getElementById("chat-form").addEventListener("submit", handleChatSubmit);
  document.getElementById("compare-form").addEventListener("submit", handleCompareSubmit);
});

// -------------------------------------------------------------
// Loading contracts (list)
// -------------------------------------------------------------

async function loadContracts() {
  let contracts;
  if (MOCK_MODE) {
    contracts = Object.values(MOCK_CONTRACTS);
  } else {
    const res = await fetch(`${API_BASE}/contracts`);
    contracts = await res.json();
  }

  contracts.forEach((c) => (contractsCache[c.contract_id] = c));
  renderContractList(contracts);
  renderCompareOptions(contracts);
  renderStats(contracts);

  if (contracts.length > 0 && !selectedContractId) {
    selectContract(contracts[0].contract_id);
  }
}

function renderContractList(contracts) {
  const list = document.getElementById("contract-list");
  list.innerHTML = "";

  if (contracts.length === 0) {
    list.innerHTML = '<li class="contract-list__empty">No contracts uploaded yet.</li>';
    return;
  }

  contracts.forEach((c) => {
    const li = document.createElement("li");
    li.className = "contract-row";
    if (c.contract_id === selectedContractId) li.classList.add("is-selected");
    li.dataset.contractId = c.contract_id;
    li.innerHTML = `
      <span class="contract-row__name">${escapeHtml(c.filename)}</span>
      <span class="contract-row__meta">${escapeHtml(c.contract_id)}</span>
    `;
    li.addEventListener("click", () => selectContract(c.contract_id));
    list.appendChild(li);
  });
}

function renderStats(contracts) {
  let upcoming = 0, overdue = 0, flags = 0;
  contracts.forEach((c) => {
    (c.obligations || []).forEach((o) => {
      if (o.status === "UPCOMING" || o.status === "DUE_SOON") upcoming++;
      if (o.status === "OVERDUE") overdue++;
    });
    flags += (c.review_flags || []).length;
  });

  document.getElementById("stat-contracts").textContent = contracts.length;
  document.getElementById("stat-upcoming").textContent = upcoming;
  document.getElementById("stat-overdue").textContent = overdue;
  document.getElementById("stat-flags").textContent = flags;
}

// -------------------------------------------------------------
// Selecting / rendering a single contract
// -------------------------------------------------------------

async function selectContract(contractId) {
  selectedContractId = contractId;

  document
    .querySelectorAll(".contract-row")
    .forEach((row) => row.classList.toggle("is-selected", row.dataset.contractId === contractId));

  let contract = contractsCache[contractId];
  if (!MOCK_MODE) {
    const res = await fetch(`${API_BASE}/contracts/${contractId}`);
    contract = await res.json();
    contractsCache[contractId] = contract;
  }

  renderContractDetail(contract);
  document.getElementById("chat-log").innerHTML = "";
}

function renderContractDetail(contract) {
  document.getElementById("detail-empty").hidden = true;
  document.getElementById("detail-content").hidden = false;

  document.getElementById("detail-filename").textContent = contract.filename;
  document.getElementById("ov-parties").textContent = (contract.parties || []).join(" · ");
  document.getElementById("ov-effective").textContent = contract.effective_date || "—";
  document.getElementById("ov-expires").textContent = contract.expiration_date || "—";

  const renewal = contract.renewal
    ? `${contract.renewal.type}${
        contract.renewal.notice_period_days != null
          ? ` — ${contract.renewal.notice_period_days} days' notice`
          : ""
      }`
    : "—";
  document.getElementById("ov-renewal").textContent = renewal;

  document.getElementById("ov-payment").textContent =
    (typeof contract.payment_terms === "string"
      ? contract.payment_terms
      : contract.payment_terms?.description) || "—";

  renderObligations(contract.obligations || []);
  renderFlags(contract.review_flags || []);
}

function renderObligations(obligations) {
  const list = document.getElementById("obligation-list");
  list.innerHTML = "";

  if (obligations.length === 0) {
    list.innerHTML = '<li class="contract-list__empty">No obligations extracted.</li>';
    return;
  }

  // Sort by status severity so overdue surfaces first (Python-side status is
  // authoritative; this is display-only ordering).
  const order = { OVERDUE: 0, DUE_SOON: 1, UPCOMING: 2, UNKNOWN: 3, COMPLETED: 4 };
  const sorted = [...obligations].sort(
    (a, b) => (order[a.status] ?? 5) - (order[b.status] ?? 5)
  );

  sorted.forEach((o) => {
    const li = document.createElement("li");
    li.className = "obligation-row";
    li.dataset.status = o.status || "UNKNOWN";
    li.innerHTML = `
      <div>
        <div class="obligation-row__action">${escapeHtml(o.action)}</div>
        <div class="obligation-row__meta">
          ${escapeHtml(o.party)} · due ${escapeHtml(o.deadline)}${
            o.frequency ? ` · ${escapeHtml(o.frequency)}` : ""
          } · §${escapeHtml(o.source?.section ?? "—")} p.${o.source?.page ?? "—"}
        </div>
      </div>
    `;
    list.appendChild(li);
  });
}

function renderFlags(flags) {
  const list = document.getElementById("flag-list");
  list.innerHTML = "";

  if (flags.length === 0) {
    list.innerHTML = '<li class="contract-list__empty">No items flagged for review.</li>';
    return;
  }

  flags.forEach((f) => {
    const li = document.createElement("li");
    li.className = "flag-row";
    li.innerHTML = `
      <div class="flag-row__type">${escapeHtml(f.type)}${
        f.severity ? ` · ${escapeHtml(f.severity)}` : ""
      }</div>
      <div class="flag-row__desc">${escapeHtml(f.description)}</div>
      <div class="flag-row__source">§${escapeHtml(f.source?.section ?? "—")}, p.${
        f.source?.page ?? "—"
      }</div>
    `;
    list.appendChild(li);
  });
}

// -------------------------------------------------------------
// Upload
// -------------------------------------------------------------

function handleFileChosen(e) {
  if (e.target.files.length > 0) {
    document.getElementById("upload-form").requestSubmit();
  }
}

async function handleUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById("file-input");
  const statusEl = document.getElementById("upload-status");
  if (!fileInput.files.length) return;

  statusEl.textContent = "Uploading…";

  if (MOCK_MODE) {
    await delay(500);
    statusEl.textContent = `Processed (mock): ${fileInput.files[0].name}`;
    fileInput.value = "";
    return;
  }

  try {
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    const res = await fetch(`${API_BASE}/contracts/upload`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error("Upload failed");
    const data = await res.json(); // { contract_id, status }
    statusEl.textContent = `Processed: ${data.contract_id}`;
    fileInput.value = "";
    await loadContracts();
    selectContract(data.contract_id);
  } catch (err) {
    statusEl.textContent = "Upload failed — check backend connection.";
  }
}

// -------------------------------------------------------------
// Chat / Q&A
// -------------------------------------------------------------

async function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById("chat-input");
  const question = input.value.trim();
  if (!question || !selectedContractId) return;

  const log = document.getElementById("chat-log");
  const entry = document.createElement("div");
  entry.className = "chat-qa";
  entry.innerHTML = `<div class="q">${escapeHtml(question)}</div><div class="a">Thinking…</div>`;
  log.prepend(entry);
  input.value = "";

  let response;
  if (MOCK_MODE) {
    await delay(400);
    response = /payment/i.test(question) ? MOCK_CHAT_ANSWERS.payment : MOCK_CHAT_ANSWERS.default;
  } else {
    const res = await fetch(`${API_BASE}/contracts/${selectedContractId}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    response = await res.json(); // { answer, sources }
  }

  const sourcesHtml = (response.sources || [])
    .map((s) => `§${escapeHtml(s.section ?? "—")}, p.${s.page ?? "—"}`)
    .join(" · ");

  entry.innerHTML = `
    <div class="q">${escapeHtml(question)}</div>
    <div class="a">${escapeHtml(response.answer)}</div>
    ${sourcesHtml ? `<div class="sources">Source: ${sourcesHtml}</div>` : ""}
  `;
}

// -------------------------------------------------------------
// Comparison
// -------------------------------------------------------------

function renderCompareOptions(contracts) {
  const v1 = document.getElementById("compare-v1");
  const v2 = document.getElementById("compare-v2");
  [v1, v2].forEach((select) => {
    const current = select.value;
    select.innerHTML = '<option value="">Version…</option>';
    contracts.forEach((c) => {
      const opt = document.createElement("option");
      opt.value = c.contract_id;
      opt.textContent = `${c.filename} (${c.contract_id})`;
      select.appendChild(opt);
    });
    select.value = current;
  });
}

async function handleCompareSubmit(e) {
  e.preventDefault();
  const v1 = document.getElementById("compare-v1").value;
  const v2 = document.getElementById("compare-v2").value;
  const resultsEl = document.getElementById("compare-results");

  if (!v1 || !v2 || v1 === v2) {
    resultsEl.innerHTML = '<p class="disclaimer">Choose two different contract versions.</p>';
    return;
  }

  resultsEl.innerHTML = '<p class="disclaimer">Comparing…</p>';

  let data;
  if (MOCK_MODE) {
    await delay(400);
    data = MOCK_COMPARISON;
  } else {
    const res = await fetch(`${API_BASE}/contracts/compare`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contract_id_v1: v1, contract_id_v2: v2 })
    });
    data = await res.json(); // { changes: [...] }
  }

  renderComparison(data.changes || []);
}

function renderComparison(changes) {
  const resultsEl = document.getElementById("compare-results");
  resultsEl.innerHTML = "";

  if (changes.length === 0) {
    resultsEl.innerHTML = '<p class="disclaimer">No material differences detected between these versions.</p>';
    return;
  }

  changes.forEach((c) => {
    const row = document.createElement("div");
    row.className = "change-row";
    row.innerHTML = `
      <div class="change-row__category">${escapeHtml(c.category)}</div>
      <div class="change-row__old">${escapeHtml(c.old_value)}</div>
      <div class="change-row__new">${escapeHtml(c.new_value)}</div>
    `;
    resultsEl.appendChild(row);
  });

  const note = document.createElement("p");
  note.className = "disclaimer";
  note.textContent = changes
    .map((c) => c.description)
    .join(" ");
  resultsEl.appendChild(note);
}

// -------------------------------------------------------------
// Utilities
// -------------------------------------------------------------

function escapeHtml(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}