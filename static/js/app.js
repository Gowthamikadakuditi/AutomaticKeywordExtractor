/**
 * Automatic Keyword and Keyphrase Extractor
 * Core Frontend Application Logic
 */

let currentAnalysisResult = null;
let selectedFile = null;

// High quality realistic sample texts for instant testing
const SAMPLE_TEXTS = {
    academic: `Recent advances in deep learning and natural language processing have revolutionized automatic text summarization and keyword extraction. Transformer architectures, particularly models utilizing self-attention mechanisms such as BERT and GPT, enable bidirectional contextual representations of complex documents. In this paper, we evaluate unsupervised statistical approaches alongside dense semantic embeddings across multi-domain research corpora. Our experimental results demonstrate that combining linguistic noun phrase chunking with inverse document frequency yields high precision and recall on technical literature. Furthermore, candidate phrase filtering eliminates non-topical stopwords while preserving domain-specific terminology.`,
    news: `The global artificial intelligence summit opened on Monday in Geneva, with international policymakers and technology executives gathering to discuss regulations on generative machine learning models. High-level delegations emphasized the critical importance of digital privacy, algorithmic transparency, and computational cybersecurity. Spokespersons from major tech consortia presented voluntary safety standards designed to mitigate algorithmic bias and automated disinformation. According to conference organizers, over forty nations signed the multilateral framework governing responsible artificial intelligence deployments.`,
    technical: `Kubernetes is an open-source container orchestration platform designed to automate the deployment, scaling, and management of containerized applications. When configuring a Kubernetes cluster, administrators define pods, services, and ingress controllers using YAML deployment manifests. The control plane manages worker nodes through the kube-apiserver, etcd distributed key-value store, and kube-scheduler. To ensure high availability and resilient microservices architecture, automated health probes monitor container states and trigger rolling updates without service downtime.`
};

document.addEventListener("DOMContentLoaded", () => {
    initTextCounter();
    initDropzone();
    checkBackendHealth();
});

// 1. LIVE TEXT COUNTER
function initTextCounter() {
    const textarea = document.getElementById("text-input");
    const wordBadge = document.getElementById("word-count");
    const charBadge = document.getElementById("char-count");

    if (!textarea) return;

    textarea.addEventListener("input", () => {
        const text = textarea.value.trim();
        const words = text ? text.split(/\s+/).length : 0;
        const chars = text.length;

        wordBadge.textContent = `${words} words`;
        charBadge.textContent = `${chars} characters`;
    });
}

// 2. SAMPLE TEXT LOADER
function loadSampleText(domain) {
    const textarea = document.getElementById("text-input");
    const domainSelect = document.getElementById("doc-type-select");

    // Switch to paste tab if not active
    const pasteTabBtn = document.getElementById("paste-tab");
    if (pasteTabBtn) {
        bootstrap.Tab.getOrCreateInstance(pasteTabBtn).show();
    }

    if (textarea && SAMPLE_TEXTS[domain]) {
        textarea.value = SAMPLE_TEXTS[domain];
        textarea.dispatchEvent(new Event("input"));
    }

    if (domainSelect) {
        domainSelect.value = domain;
    }

    hideErrorAlert();
}

// 3. FILE DROPZONE & PICKER
function initDropzone() {
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("file-input");

    if (!dropzone || !fileInput) return;

    ["dragenter", "dragover"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add("dragover");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove("dragover");
        }, false);
    });

    dropzone.addEventListener("drop", (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleSelectedFile(files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (fileInput.files.length > 0) {
            handleSelectedFile(fileInput.files[0]);
        }
    });
}

function handleSelectedFile(file) {
    const validExtensions = [".pdf", ".docx", ".txt"];
    const fileExt = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();

    if (!validExtensions.includes(fileExt)) {
        showErrorAlert(`Unsupported file extension '${fileExt}'. Please select a .pdf, .docx, or .txt file.`);
        clearSelectedFile();
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showErrorAlert("File size exceeds 10 MB limit. Please select a smaller document.");
        clearSelectedFile();
        return;
    }

    selectedFile = file;
    document.getElementById("selected-filename").textContent = file.name;
    document.getElementById("selected-filesize").textContent = `(${(file.size / 1024).toFixed(1)} KB)`;
    document.getElementById("file-info-container").classList.remove("d-none");
    hideErrorAlert();
}

function clearSelectedFile() {
    selectedFile = null;
    const fileInput = document.getElementById("file-input");
    if (fileInput) fileInput.value = "";
    document.getElementById("file-info-container").classList.add("d-none");
}

// 4. CHECK BACKEND HEALTH
async function checkBackendHealth() {
    try {
        const resp = await fetch("/api/health");
        if (resp.ok) {
            const data = await resp.json();
            const badge = document.getElementById("backend-status-badge");
            if (badge) {
                badge.innerHTML = `<i class="bi bi-circle-fill me-1 small"></i> API Ready (${data.python_version})`;
                badge.className = "badge bg-success-subtle text-success border border-success-subtle py-2 px-3";
            }
        }
    } catch (err) {
        const badge = document.getElementById("backend-status-badge");
        if (badge) {
            badge.innerHTML = `<i class="bi bi-x-circle me-1 small"></i> API Offline`;
            badge.className = "badge bg-danger-subtle text-danger border border-danger-subtle py-2 px-3";
        }
    }
}
function onMethodChanged() {
    hideInfoAlert();
}
// 6. TRIGGER EXTRACTION
async function triggerExtraction() {
    hideErrorAlert();
    hideInfoAlert();

    const activeTab = document.querySelector("#inputTabs .nav-link.active");
    const isUploadTab = activeTab && activeTab.id === "upload-tab";

    const topN = document.getElementById("top-n-select").value;
    const method = document.getElementById("method-select").value;
    const docType = document.getElementById("doc-type-select").value;
    const candidateType = document.getElementById("candidate-type-select").value;

    let payload;
    let isMultipart = false;

    if (isUploadTab) {
        if (!selectedFile) {
            showErrorAlert("Please select or drop a document (.pdf, .docx, .txt) before analyzing.");
            return;
        }
        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("top_n", topN);
        formData.append("method", method);
        formData.append("doc_type", docType);
        formData.append("candidate_type", candidateType);
        payload = formData;
        isMultipart = true;
    } else {
        const text = document.getElementById("text-input").value.trim();
        if (!text) {
            showErrorAlert("Please paste text or enter content to extract keywords.");
            return;
        }
        payload = {
            text: text,
            top_n: parseInt(topN, 10),
            method: method,
            doc_type: docType,
            candidate_type: candidateType
        };
    }

    setLoadingState(true);

    try {
        const fetchOptions = {
            method: "POST",
            body: isMultipart ? payload : JSON.stringify(payload)
        };
        if (!isMultipart) {
            fetchOptions.headers = { "Content-Type": "application/json" };
        }

        const response = await fetch("/api/extract", {
            ...fetchOptions
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            showErrorAlert(result.error || "Failed to extract keywords from document.");
            setLoadingState(false);
            return;
        }

        currentAnalysisResult = result;
        renderResults(result);

    } catch (err) {
        showErrorAlert(`Network or server connection error: ${err.message}`);
    } finally {
        setLoadingState(false);
    }
}

// 7. RENDER RESULTS
function renderResults(data) {
    const resultsContainer = document.getElementById("results-container");
    resultsContainer.classList.remove("d-none");

    // Summary Statistics
    const stats = data.statistics || {};
    document.getElementById("stat-words").textContent = (stats.total_words || 0).toLocaleString();
    document.getElementById("stat-unique").textContent = (stats.unique_words || 0).toLocaleString();
    document.getElementById("stat-sentences").textContent = stats.total_sentences || 0;
    document.getElementById("stat-extracted").textContent = data.keywords ? data.keywords.length : 0;
    document.getElementById("stat-time").textContent = `${stats.processing_time_ms || 0} ms`;
    document.getElementById("stat-reading").textContent = `${stats.estimated_reading_time_sec || 0}s`;

    // Algorithm Banner
    const algoInfo = data.algorithm_info || {};
    document.getElementById("algo-banner-title").textContent = `${algoInfo.name || data.algorithm} (${algoInfo.type || "Algorithm"})`;
    document.getElementById("algo-banner-desc").textContent = algoInfo.description || "";
    document.getElementById("chart-score-label").textContent = algoInfo.score_label || "Relevance Score";
    document.getElementById("results-subtitle").textContent = `Top keywords extracted for ${data.document_type} domain using ${data.algorithm}`;

    // Populate Table
    const tbody = document.getElementById("results-table-body");
    tbody.innerHTML = "";

    const keywords = data.keywords || [];
    keywords.forEach(kw => {
        const tr = document.createElement("tr");

        const isPhrase = kw.type === "keyphrase";
        const badgeClass = isPhrase ? "badge-keyphrase" : "badge-keyword";
        const badgeIcon = isPhrase ? "bi-chat-left-text" : "bi-tag";
        const typeLabel = isPhrase ? "Keyphrase" : "Keyword";

        const scorePercent = Math.min(100, Math.max(5, Math.round(kw.score * 100)));

        tr.innerHTML = `
            <td class="fw-bold text-muted">#${kw.rank}</td>
            <td class="fw-semibold text-navy">
                <span>${escapeHtml(kw.text)}</span>
            </td>
            <td>
                <span class="badge ${badgeClass} px-2 py-1">
                    <i class="bi ${badgeIcon} me-1"></i>${typeLabel}
                </span>
            </td>
            <td>
                <div class="fw-bold text-indigo">${kw.score.toFixed(4)}</div>
                <div class="score-progress-bar">
                    <div class="score-progress-fill" style="width: ${scorePercent}%;"></div>
                </div>
            </td>
            <td>
                <span class="badge bg-light text-dark border font-monospace">${kw.raw_score}</span>
            </td>
            <td>
                <span class="badge bg-light text-secondary border px-2">${kw.frequency}x</span>
            </td>
            <td class="text-muted small">${kw.word_count} ${kw.word_count === 1 ? "word" : "words"}</td>
        `;

        tbody.appendChild(tr);
    });

    // Render Charts
    if (typeof renderCharts === "function") {
        renderCharts(keywords, algoInfo.score_label);
    }

    // Smooth scroll down to results
    resultsContainer.scrollIntoView({ behavior: "smooth", block: "start" });
}

// 8. EXPORT ACTIONS
async function exportData(format) {
    if (!currentAnalysisResult) {
        showErrorAlert("No analysis data available to export. Please extract keywords first.");
        return;
    }

    try {
        const response = await fetch(`/api/export/${format}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(currentAnalysisResult)
        });

        if (!response.ok) {
            const err = await response.json();
            showErrorAlert(err.error || "Failed to download export file.");
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `keywords_extracted.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

    } catch (err) {
        showErrorAlert(`Export error: ${err.message}`);
    }
}

// 9. UI HELPERS
function setLoadingState(isLoading) {
    const btn = document.getElementById("extract-btn");
    const spinner = document.getElementById("btn-spinner");
    const btnText = document.getElementById("btn-text");
    const loadingState = document.getElementById("loading-state");

    if (isLoading) {
        btn.disabled = true;
        spinner.classList.remove("d-none");
        btnText.textContent = "Processing NLP...";
        loadingState.classList.remove("d-none");
    } else {
        btn.disabled = false;
        spinner.classList.add("d-none");
        btnText.innerHTML = '<i class="bi bi-stars me-2"></i>Extract Keywords';
        loadingState.classList.add("d-none");
    }
}

function showErrorAlert(message) {
    const alert = document.getElementById("error-alert");
    const msg = document.getElementById("error-message");
    msg.textContent = message;
    alert.classList.remove("d-none");
    alert.classList.add("show");
    alert.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hideErrorAlert() {
    const alert = document.getElementById("error-alert");
    alert.classList.add("d-none");
    alert.classList.remove("show");
}

function showInfoAlert(message) {
    const alert = document.getElementById("info-alert");
    const msg = document.getElementById("info-message");
    msg.textContent = message;
    alert.classList.remove("d-none");
    alert.classList.add("show");
}

function hideInfoAlert() {
    const alert = document.getElementById("info-alert");
    alert.classList.add("d-none");
    alert.classList.remove("show");
}

function resetForm() {
    document.getElementById("text-input").value = "";
    document.getElementById("text-input").dispatchEvent(new Event("input"));
    clearSelectedFile();
    hideErrorAlert();
    hideInfoAlert();
    document.getElementById("results-container").classList.add("d-none");
    currentAnalysisResult = null;
}

function escapeHtml(string) {
    const div = document.createElement("div");
    div.innerText = string;
    return div.innerHTML;
}
