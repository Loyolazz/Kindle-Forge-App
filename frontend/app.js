const form = document.querySelector("#convertForm");
const fileInput = document.querySelector("#fileInput");
const folderInput = document.querySelector("#folderInput");
const folderButton = document.querySelector("#folderButton");
const fileLabel = document.querySelector("#fileLabel");
const fileMeta = document.querySelector("#fileMeta");
const fileList = document.querySelector("#fileList");
const fileOrderTools = document.querySelector("#fileOrderTools");
const sortFilesButton = document.querySelector("#sortFilesButton");
const reverseFilesButton = document.querySelector("#reverseFilesButton");
const mergePdfsButton = document.querySelector("#mergePdfsButton");
const dropZone = document.querySelector("#dropZone");
const coverInput = document.querySelector("#coverInput");
const coverLabel = document.querySelector("#coverLabel");
const coverUrlInput = document.querySelector("#coverUrlInput");
const titleInput = document.querySelector("#titleInput");
const metadataButton = document.querySelector("#metadataButton");
const metadataKind = document.querySelector("#metadataKind");
const metadataLanguage = document.querySelector("#metadataLanguage");
const metadataResults = document.querySelector("#metadataResults");
const modeInput = document.querySelector("#modeInput");
const qualityInput = document.querySelector("#qualityInput");
const qualityValue = document.querySelector("#qualityValue");
const gammaInput = document.querySelector("#gammaInput");
const gammaValue = document.querySelector("#gammaValue");
const splitInput = document.querySelector("#splitInput");
const protectFirstInput = document.querySelector("#protectFirstInput");
const splitSizeInput = document.querySelector("#splitSizeInput");
const convertButton = document.querySelector("#convertButton");
const previewButton = document.querySelector("#previewButton");
const openRootButton = document.querySelector("#openRootButton");
const refreshHistoryButton = document.querySelector("#refreshHistoryButton");
const clearHistoryButton = document.querySelector("#clearHistoryButton");
const deleteFilesButton = document.querySelector("#deleteFilesButton");
const statusTitle = document.querySelector("#statusTitle");
const statusDot = document.querySelector("#statusDot");
const resultList = document.querySelector("#resultList");
const previewGrid = document.querySelector("#previewGrid");
const previewTitle = document.querySelector("#previewTitle");
const previewDetail = document.querySelector("#previewDetail");
const prevPreviewButton = document.querySelector("#prevPreviewButton");
const nextPreviewButton = document.querySelector("#nextPreviewButton");
const zoomPreviewButton = document.querySelector("#zoomPreviewButton");
const progressList = document.querySelector("#progressList");
const historyList = document.querySelector("#historyList");
const messageBox = document.querySelector("#messageBox");

let selectedFiles = [];
let draggedFileIndex = null;
let previewItems = [];
let previewIndex = 0;
let previewZoomed = false;
let progressTimer = null;
let progressIndex = 0;

const progressSteps = [
  "Lendo arquivo",
  "Extraindo páginas",
  "Cortando margens",
  "Redimensionando para Kindle",
  "Gerando EPUB",
  "Salvando histórico",
];

const presets = {
  manga: { mode: "manga", quality: 85, gamma: 0.95, crop: true, split: true, protect: true, dither: false, color: false, splitMb: 200 },
  comic: { mode: "comic", quality: 86, gamma: 1, crop: true, split: true, protect: true, dither: true, color: false, splitMb: 200 },
  webtoon: { mode: "webtoon", quality: 84, gamma: 1, crop: true, split: false, protect: false, dither: false, color: false, splitMb: 200 },
  pdf: { mode: "auto", quality: 88, gamma: 0.9, crop: true, split: false, protect: true, dither: false, color: false, splitMb: 200 },
  quality: { mode: "auto", quality: 92, gamma: 1, crop: true, split: true, protect: true, dither: true, color: false, splitMb: 200 },
  light: { mode: "auto", quality: 72, gamma: 0.95, crop: true, split: true, protect: true, dither: false, color: false, splitMb: 180 },
  auto: { mode: "auto", quality: 85, gamma: 1, crop: true, split: true, protect: true, dither: false, color: false, splitMb: 200 },
};

const formatBytes = (bytes) => {
  if (!Number.isFinite(bytes) || bytes <= 0) return "0 KB";
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
};

const fileTitle = (name) => name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ").trim();

const naturalCompare = (a, b) =>
  new Intl.Collator("pt-BR", { numeric: true, sensitivity: "base" }).compare(
    a.webkitRelativePath || a.name,
    b.webkitRelativePath || b.name
  );

const setStatus = (state, title, message = "") => {
  statusTitle.textContent = title;
  statusDot.className = `status-dot ${state}`;
  messageBox.textContent = message;
  messageBox.classList.toggle("error", state === "error");
};

const friendlyApiError = (data, fallback) => {
  const message = data?.error || fallback;
  if (message === "Endpoint nao encontrado.") {
    return "O servidor local ainda está numa versão antiga. Feche o terminal do app e rode python run.py de novo.";
  }
  return message;
};

const setBusy = (busy) => {
  convertButton.disabled = busy;
  previewButton.disabled = busy;
  convertButton.querySelector("span").textContent = busy ? "Convertendo" : "Converter";
};

const startProgress = () => {
  clearInterval(progressTimer);
  progressIndex = 0;
  renderProgress();
  progressList.hidden = false;
  progressTimer = setInterval(() => {
    progressIndex = Math.min(progressSteps.length - 1, progressIndex + 1);
    renderProgress();
  }, 900);
};

const stopProgress = () => {
  clearInterval(progressTimer);
  progressTimer = null;
  progressIndex = progressSteps.length;
  renderProgress();
};

const renderProgress = () => {
  progressList.replaceChildren();
  progressSteps.forEach((step, index) => {
    const node = document.createElement("div");
    node.className = "progress-step";
    if (index < progressIndex) node.classList.add("done");
    if (index === Math.min(progressIndex, progressSteps.length - 1)) node.classList.add("active");
    node.textContent = step;
    progressList.append(node);
  });
};

const selectedFormats = () => [...form.querySelectorAll('input[name="format"]:checked')].map((item) => item.value);

const checkedField = (name) => form.querySelector(`input[name="${name}"]`);

const syncFiles = (files) => {
  selectedFiles = [...files].filter((file) => file.name);
  renderSelectedFiles();
  if (selectedFiles.length === 1 && !titleInput.value.trim()) {
    titleInput.value = fileTitle(selectedFiles[0].name);
  }
  if (selectedFiles.length > 1 && !titleInput.value.trim()) {
    titleInput.value = guessCollectionTitle(selectedFiles);
  }
};

const renderSelectedFiles = () => {
  if (!selectedFiles.length) {
    fileLabel.textContent = "Arraste arquivos, CBR/CBZ/PDF ou uma pasta";
    fileMeta.textContent = "Mangás, HQs, manhwas, PDFs e imagens";
    fileList.hidden = true;
    fileOrderTools.hidden = true;
    fileList.replaceChildren();
    return;
  }
  const total = selectedFiles.reduce((sum, file) => sum + file.size, 0);
  fileLabel.textContent = selectedFiles.length === 1 ? selectedFiles[0].name : `${selectedFiles.length} arquivos selecionados`;
  fileMeta.textContent = formatBytes(total);
  fileList.hidden = false;
  fileOrderTools.hidden = selectedFiles.length < 2;
  fileList.replaceChildren();
  selectedFiles.forEach((file, index) => {
    const chip = document.createElement("div");
    chip.className = "file-chip";
    chip.draggable = true;
    chip.dataset.index = String(index);
    chip.innerHTML = `
      <span class="file-index">${index + 1}</span>
      <span class="file-name">${file.webkitRelativePath || file.name}</span>
      <strong>${formatBytes(file.size)}</strong>
      <span class="file-controls">
        <button type="button" data-action="up" title="Subir">↑</button>
        <button type="button" data-action="down" title="Descer">↓</button>
        <button type="button" data-action="remove" title="Remover">×</button>
      </span>
    `;
    fileList.append(chip);
  });
};

const moveFile = (from, to) => {
  if (to < 0 || to >= selectedFiles.length || from === to) return;
  const next = [...selectedFiles];
  const [item] = next.splice(from, 1);
  next.splice(to, 0, item);
  selectedFiles = next;
  renderSelectedFiles();
};

fileList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const chip = button.closest(".file-chip");
  const index = Number(chip.dataset.index);
  const action = button.dataset.action;
  if (action === "up") moveFile(index, index - 1);
  if (action === "down") moveFile(index, index + 1);
  if (action === "remove") {
    selectedFiles.splice(index, 1);
    renderSelectedFiles();
  }
});

fileList.addEventListener("dragstart", (event) => {
  const chip = event.target.closest(".file-chip");
  if (!chip) return;
  draggedFileIndex = Number(chip.dataset.index);
  chip.classList.add("dragging");
  event.dataTransfer.effectAllowed = "move";
});

fileList.addEventListener("dragend", () => {
  draggedFileIndex = null;
  fileList.querySelectorAll(".file-chip").forEach((chip) => chip.classList.remove("dragging"));
});

fileList.addEventListener("dragover", (event) => {
  event.preventDefault();
  const chip = event.target.closest(".file-chip");
  if (!chip || draggedFileIndex === null) return;
  const targetIndex = Number(chip.dataset.index);
  if (targetIndex !== draggedFileIndex) {
    moveFile(draggedFileIndex, targetIndex);
    draggedFileIndex = targetIndex;
  }
});

sortFilesButton.addEventListener("click", () => {
  selectedFiles.sort(naturalCompare);
  renderSelectedFiles();
});

reverseFilesButton.addEventListener("click", () => {
  selectedFiles.reverse();
  renderSelectedFiles();
});

mergePdfsButton.addEventListener("click", () => {
  form.querySelector('input[name="groupMode"][value="volume"]').checked = true;
  checkedField("format").checked = true;
  setStatus("done", "Mesclagem ativada", "A conversão vai seguir a ordem visual da lista.");
});

const guessCollectionTitle = (files) => {
  const names = files.map((file) => fileTitle(file.webkitRelativePath || file.name));
  const cleaned = names.map((name) =>
    name
      .replace(/\b(chapter|capitulo|capítulo|cap|ch|vol|volume|v)\s*\d+([.,]\d+)?\b/gi, " ")
      .replace(/\b\d{1,4}\b/g, " ")
      .replace(/\s+/g, " ")
      .trim()
  );
  const words = (cleaned[0] || "Volume organizado").split(" ");
  while (words.length) {
    const prefix = words.join(" ");
    if (cleaned.every((name) => name.toLowerCase().startsWith(prefix.toLowerCase()))) return prefix;
    words.pop();
  }
  return "Volume organizado";
};

const applyPreset = (name) => {
  const preset = presets[name];
  if (!preset) return;
  document.querySelectorAll(".preset-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.preset === name);
  });
  modeInput.value = preset.mode;
  qualityInput.value = String(preset.quality);
  gammaInput.value = String(preset.gamma);
  splitSizeInput.value = String(preset.splitMb);
  checkedField("crop").checked = preset.crop;
  splitInput.checked = preset.split;
  protectFirstInput.checked = preset.protect;
  checkedField("dither").checked = preset.dither;
  checkedField("color").checked = preset.color;
  syncControlText();
};

const syncControlText = () => {
  qualityValue.textContent = qualityInput.value;
  gammaValue.textContent = Number(gammaInput.value).toFixed(2);
  if (modeInput.value === "webtoon") {
    splitInput.checked = false;
    splitInput.disabled = true;
    protectFirstInput.disabled = true;
  } else {
    splitInput.disabled = false;
    protectFirstInput.disabled = false;
  }
};

const buildPayload = (onlyFirst = false) => {
  const formats = selectedFormats();
  if (!formats.length) throw new Error("Marque pelo menos um formato.");
  if (!selectedFiles.length) throw new Error("Escolha arquivos ou uma pasta.");
  const payload = new FormData(form);
  payload.delete("file");
  payload.delete("format");
  payload.append("format", formats.join(","));
  payload.set("profile", "kindle11");
  const files = onlyFirst ? selectedFiles.slice(0, 1) : selectedFiles;
  files.forEach((file) => payload.append("file", file, file.webkitRelativePath || file.name));
  if (coverInput.files[0]) {
    payload.append("coverFile", coverInput.files[0], coverInput.files[0].name);
  }
  return payload;
};

fileInput.addEventListener("change", () => syncFiles(fileInput.files));
folderInput.addEventListener("change", () => syncFiles(folderInput.files));
folderButton.addEventListener("click", () => folderInput.click());

coverInput.addEventListener("change", () => {
  coverLabel.textContent = coverInput.files[0] ? coverInput.files[0].name : "Escolher capa personalizada";
  if (coverInput.files[0]) {
    form.querySelector('input[name="coverMode"][value="custom"]').checked = true;
    coverUrlInput.value = "";
  }
});

metadataButton.addEventListener("click", async () => {
  const query = titleInput.value.trim() || (selectedFiles[0] ? fileTitle(selectedFiles[0].name) : "");
  if (!query) {
    setStatus("error", "Sem busca", "Digite um título ou escolha arquivos primeiro.");
    return;
  }
  metadataButton.disabled = true;
  metadataButton.textContent = "Buscando";
  setStatus("working", "Buscando dados", query);
  try {
    const response = await fetch(
      `/api/metadata?q=${encodeURIComponent(query)}&kind=${encodeURIComponent(metadataKind.value)}&language=${encodeURIComponent(metadataLanguage.value)}`
    );
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Busca falhou.");
    renderMetadata(data.items || []);
    setStatus("done", "Dados encontrados", `${(data.items || []).length} resultado(s).`);
  } catch (error) {
    setStatus("error", "Busca falhou", error.message || "Não consegui buscar metadados.");
  } finally {
    metadataButton.disabled = false;
    metadataButton.textContent = "Buscar metadados";
  }
});

document.querySelectorAll(".preset-button").forEach((button) => {
  button.addEventListener("click", () => applyPreset(button.dataset.preset));
});

qualityInput.addEventListener("input", syncControlText);
gammaInput.addEventListener("input", syncControlText);

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
  });
});

dropZone.addEventListener("drop", async (event) => {
  const files = await filesFromDataTransfer(event.dataTransfer);
  syncFiles(files);
});

previewButton.addEventListener("click", async () => {
  try {
    const payload = buildPayload(true);
    setBusy(true);
    setStatus("working", "Gerando prévia", selectedFiles[0].name);
    const response = await fetch("/api/preview", { method: "POST", body: payload });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Prévia falhou.");
    renderPreview(data.previews || (data.images || []).map((src) => ({ src, label: "Prévia", detail: "" })));
    setStatus("done", "Prévia pronta", `${previewItems.length} imagem(ns) processada(s).`);
  } catch (error) {
    setStatus("error", "Falhou", error.message || "Não foi possível gerar prévia.");
  } finally {
    setBusy(false);
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = buildPayload(false);
    setBusy(true);
    startProgress();
    setStatus("working", "Convertendo", selectedFiles.length === 1 ? selectedFiles[0].name : `${selectedFiles.length} arquivos`);
    resultList.hidden = true;
    resultList.replaceChildren();
    const response = await fetch("/api/convert", { method: "POST", body: payload });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Conversão falhou.");
    renderResults(data.items || [data]);
    stopProgress();
    await loadHistory();
  } catch (error) {
    stopProgress();
    setStatus("error", "Falhou", error.message || "Não foi possível converter.");
  } finally {
    setBusy(false);
  }
});

openRootButton.addEventListener("click", () => openOutput(""));

const filesFromDataTransfer = async (dataTransfer) => {
  const items = [...dataTransfer.items];
  const entries = items.map((item) => item.webkitGetAsEntry?.()).filter(Boolean);
  if (!entries.length) return [...dataTransfer.files];
  const files = [];
  for (const entry of entries) {
    files.push(...(await filesFromEntry(entry)));
  }
  return files;
};

const filesFromEntry = (entry) =>
  new Promise((resolve) => {
    if (entry.isFile) {
      entry.file((file) => resolve([file]), () => resolve([]));
      return;
    }
    if (!entry.isDirectory) {
      resolve([]);
      return;
    }
    const reader = entry.createReader();
    const all = [];
    const read = () => {
      reader.readEntries(async (entries) => {
        if (!entries.length) {
          resolve(all);
          return;
        }
        for (const child of entries) {
          all.push(...(await filesFromEntry(child)));
        }
        read();
      });
    };
    read();
  });

const renderPreview = (items) => {
  previewItems = items || [];
  previewIndex = 0;
  previewZoomed = false;
  renderPreviewPage();
};

const renderPreviewPage = () => {
  previewGrid.replaceChildren();
  previewGrid.classList.toggle("zoomed", previewZoomed);
  if (!previewItems.length) {
    previewTitle.textContent = "Prévia";
    previewDetail.textContent = "Aguardando arquivo";
    const frame = document.createElement("div");
    frame.className = "kindle-frame";
    frame.innerHTML = '<div class="kindle-screen"><span>Prévia</span></div>';
    previewGrid.append(frame);
    return;
  }
  const item = previewItems[previewIndex];
  previewTitle.textContent = `${item.label || "Prévia"} — Página ${previewIndex + 1} de ${previewItems.length}`;
  previewDetail.textContent = item.detail || `${item.width || 1072} x ${item.height || 1448}`;
  const image = document.createElement("img");
  image.src = item.src;
  image.alt = item.label || "Prévia processada";
  previewGrid.append(image);
};

prevPreviewButton.addEventListener("click", () => {
  if (!previewItems.length) return;
  previewIndex = (previewIndex - 1 + previewItems.length) % previewItems.length;
  renderPreviewPage();
});

nextPreviewButton.addEventListener("click", () => {
  if (!previewItems.length) return;
  previewIndex = (previewIndex + 1) % previewItems.length;
  renderPreviewPage();
});

zoomPreviewButton.addEventListener("click", () => {
  previewZoomed = !previewZoomed;
  zoomPreviewButton.textContent = previewZoomed ? "Sair" : "Zoom";
  renderPreviewPage();
});

const renderMetadata = (items) => {
  metadataResults.hidden = false;
  metadataResults.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "message-box";
    empty.textContent = "Nenhum resultado encontrado. Tente o nome da série sem número de capítulo.";
    metadataResults.append(empty);
    return;
  }
  items.forEach((item) => {
    const card = document.createElement("div");
    const confidence = Number(item.confidence || 0);
    card.className = `metadata-card ${confidence < 55 ? "low-confidence" : ""}`;

    const cover = document.createElement("img");
    cover.className = "metadata-cover";
    cover.alt = "";
    cover.src = item.cover_url || "";

    const text = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = item.title || "Sem título";
    const meta = document.createElement("span");
    meta.textContent = [item.author, item.year, item.source].filter(Boolean).join(" · ");
    const description = document.createElement("span");
    description.textContent = item.description ? item.description.slice(0, 150) : "";
    const tag = document.createElement("span");
    tag.className = `confidence-tag ${confidence < 55 ? "low" : ""}`;
    tag.textContent = confidence ? `${confidence}% confiança` : "Sem score";
    const warning = document.createElement("span");
    warning.textContent = item.warning || "";
    text.append(title, meta, description, tag, warning);

    const actions = document.createElement("div");
    actions.className = "item-actions";
    const allButton = metadataAction("Tudo", () => applyMetadata(item, "all"));
    const coverButton = metadataAction("Só capa", () => applyMetadata(item, "cover"));
    const descButton = metadataAction("Só descrição", () => applyMetadata(item, "description"));
    actions.append(allButton, coverButton, descButton);

    card.append(cover, text, actions);
    metadataResults.append(card);
  });
};

const metadataAction = (label, handler) => {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.addEventListener("click", handler);
  return button;
};

const applyMetadata = (item, mode) => {
  if (mode === "all") {
    titleInput.value = item.title || titleInput.value;
    form.elements.author.value = item.author || form.elements.author.value;
    form.elements.series.value = item.series || item.title || form.elements.series.value;
    form.elements.publisher.value = item.publisher || form.elements.publisher.value;
    form.elements.language.value = item.language || form.elements.language.value;
    form.elements.description.value = item.description || form.elements.description.value;
  }
  if (mode === "description") {
    form.elements.description.value = item.description || form.elements.description.value;
  }
  if ((mode === "all" || mode === "cover") && item.cover_url) {
    coverUrlInput.value = item.cover_url || "";
    form.querySelector('input[name="coverMode"][value="online"]').checked = true;
    coverLabel.textContent = `Capa online: ${item.source}`;
  }
  setStatus("done", "Metadados aplicados", `${item.source || "Fonte online"} · ${item.confidence || 0}%`);
};

const renderResults = (items) => {
  resultList.hidden = false;
  resultList.replaceChildren();
  items.forEach((item) => resultList.append(resultNode(item)));
  const pages = items.reduce((sum, item) => sum + (item.pages || 0), 0);
  const files = items.reduce((sum, item) => sum + (item.files?.length || 0), 0);
  setStatus("done", "Concluído", `${items.length} item(ns), ${pages} página(s), ${files} arquivo(s).`);
};

const resultNode = (item) => {
  const node = document.createElement("div");
  node.className = "result-item";
  const splitText = item.split ? " dividido em partes" : "";
  node.innerHTML = `
    <div class="result-head">
      <strong>${item.title}</strong>
      <span>${item.pages} pág. · ${item.mode}${splitText}</span>
    </div>
  `;
  const io = document.createElement("div");
  io.className = "io-summary";
  const inputSize = item.input ? formatBytes(item.input.size) : "";
  const outputSize = item.outputSize ? formatBytes(item.outputSize) : "";
  io.innerHTML = `
    <div class="io-box">
      <span class="eyebrow">Entrada</span>
      <strong>${item.input?.name || item.title}</strong>
      <span>${inputSize}${item.input?.count ? ` · ${item.input.count} arquivo(s)` : ""}</span>
    </div>
    <div class="io-box">
      <span class="eyebrow">Saída</span>
      <strong>${item.files?.[0]?.name || "Arquivo convertido"}</strong>
      <span>${outputSize} · Otimizado para Kindle Basic 11</span>
    </div>
  `;
  const tags = document.createElement("div");
  tags.className = "status-tags";
  [item.mode, "Kindle Basic 11", `${item.pages} páginas`, item.split ? "partes" : "único"].forEach((value) => {
    const tag = document.createElement("span");
    tag.className = "status-tag";
    tag.textContent = value;
    tags.append(tag);
  });
  const actions = document.createElement("div");
  actions.className = "item-actions";
  item.files.forEach((file) => {
    const link = document.createElement("a");
    link.href = file.url;
    link.download = file.name;
    link.textContent = `${file.name} · ${formatBytes(file.size)}`;
    actions.append(link);
  });
  const folder = document.createElement("button");
  folder.type = "button";
  folder.textContent = "Abrir pasta";
  folder.addEventListener("click", () => openOutput(item.jobId));
  actions.append(folder);
  node.append(io, tags, actions);
  return node;
};

const loadHistory = async () => {
  try {
    const response = await fetch("/api/history");
    const data = await response.json();
    renderHistory(data.items || []);
  } catch {
    renderHistory([]);
  }
};

const renderHistory = (items) => {
  historyList.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "message-box";
    empty.textContent = "Nenhuma conversão ainda.";
    historyList.append(empty);
    return;
  }
  items.slice(0, 8).forEach((item) => {
    const node = document.createElement("div");
    node.className = "history-item";
    node.innerHTML = `
      <div class="history-head">
        <strong>${item.title}</strong>
        <span>${item.pages} pág.</span>
      </div>
    `;
    const actions = document.createElement("div");
    actions.className = "item-actions";
    const first = item.files?.[0];
    if (first) {
      const link = document.createElement("a");
      link.href = first.url;
      link.download = first.name;
      link.textContent = "Baixar";
      actions.append(link);
    }
    const folder = document.createElement("button");
    folder.type = "button";
    folder.textContent = "Abrir pasta";
    folder.addEventListener("click", () => openOutput(item.jobId));
    actions.append(folder);
    node.append(actions);
    historyList.append(node);
  });
};

const openOutput = async (jobId) => {
  const url = jobId ? `/api/open-output?job=${encodeURIComponent(jobId)}` : "/api/open-output";
  await fetch(url);
};

refreshHistoryButton.addEventListener("click", loadHistory);
clearHistoryButton.addEventListener("click", async () => {
  if (!window.confirm("Limpar o histórico da biblioteca? Os arquivos convertidos continuam na pasta de saída.")) return;
  clearHistoryButton.disabled = true;
  try {
    const response = await fetch("/api/history/clear", { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(friendlyApiError(data, "Não consegui limpar."));
    renderHistory([]);
    setStatus("done", "Biblioteca limpa", "O histórico foi apagado; os arquivos continuam salvos.");
  } catch (error) {
    setStatus("error", "Falhou", error.message || "Não foi possível limpar a biblioteca.");
  } finally {
    clearHistoryButton.disabled = false;
  }
});
deleteFilesButton.addEventListener("click", async () => {
  const ok = window.confirm(
    "Apagar os arquivos convertidos listados na biblioteca? Isso remove as pastas de saída desses itens e também limpa o histórico."
  );
  if (!ok) return;
  deleteFilesButton.disabled = true;
  try {
    const response = await fetch("/api/history/delete-files", { method: "POST" });
    const data = await response.json();
    if (!response.ok) throw new Error(friendlyApiError(data, "Não consegui apagar os arquivos."));
    renderHistory([]);
    resultList.hidden = true;
    resultList.replaceChildren();
    setStatus("done", "Arquivos apagados", `${data.deleted || 0} pasta(s) de conversão removida(s).`);
  } catch (error) {
    setStatus("error", "Falhou", error.message || "Não foi possível apagar os arquivos.");
  } finally {
    deleteFilesButton.disabled = false;
  }
});
syncFiles([]);
syncControlText();
renderPreview([]);
loadHistory();
