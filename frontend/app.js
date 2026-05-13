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
const profileSelect = document.querySelector("#profileSelect");
const profilePill = document.querySelector("#profilePill");
const profileInfo = document.querySelector("#profileInfo");
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
const previewSourceBar = document.querySelector("#previewSourceBar");
const previewSourceSelect = document.querySelector("#previewSourceSelect");
const previewPageInput = document.querySelector("#previewPageInput");
const prevSourcePageButton = document.querySelector("#prevSourcePageButton");
const nextSourcePageButton = document.querySelector("#nextSourcePageButton");
const loadPreviewButton = document.querySelector("#loadPreviewButton");
const prevPreviewButton = document.querySelector("#prevPreviewButton");
const nextPreviewButton = document.querySelector("#nextPreviewButton");
const zoomPreviewButton = document.querySelector("#zoomPreviewButton");
const progressList = document.querySelector("#progressList");
const historyList = document.querySelector("#historyList");
const messageBox = document.querySelector("#messageBox");

let selectedFiles = [];
let draggedFileIndex = null;
let activePreviewFileIndex = 0;
let activePreviewPage = 0;
let activePreviewPageCount = null;
let previewItems = [];
let previewIndex = 0;
let previewZoomed = false;
let previewAutoTimer = null;
let previewRequestId = 0;
let selectedMetadataKey = "";
let progressTimer = null;
let progressIndex = 0;
let progressState = "idle";

const attachmentLimits = {
  total: 2500,
  pdf: 120,
  image: 2000,
};

const progressSteps = [
  {
    title: "Recebendo arquivos",
    detail: "Conferindo PDFs, capítulos, imagens e arquivos compactados.",
  },
  {
    title: "Extraindo páginas",
    detail: "Lendo as páginas na ordem escolhida para o volume.",
  },
  {
    title: "Tratando imagem",
    detail: "Aplicando corte de margem, contraste, cor e páginas duplas.",
  },
  {
    title: "Ajustando para o leitor",
    detail: "Redimensionando tudo para o leitor escolhido.",
  },
  {
    title: "Montando saída",
    detail: "Criando EPUB, CBZ ou PDF e dividindo partes quando precisar.",
  },
  {
    title: "Finalizando biblioteca",
    detail: "Salvando histórico, tamanho final e links de download.",
  },
];

const deviceProfileGroups = [
  {
    label: "Kindle por geração",
    items: [
      { key: "kindle-basic-12", name: "Kindle Basic", generation: "12ª geração / 2024", resolution: "1072 x 1448", ppi: "300 ppi", note: "6 polegadas, melhor padrão para mangá atual." },
      { key: "kindle-basic-11", name: "Kindle Basic", generation: "11ª geração / 2022", resolution: "1072 x 1448", ppi: "300 ppi", note: "Seu Kindle Basic 11. Opção padrão." },
      { key: "kindle-basic-10", name: "Kindle Basic", generation: "10ª geração / 2019", resolution: "600 x 800", ppi: "167 ppi", note: "Modelo básico antigo; prefira arquivo leve." },
      { key: "kindle-paperwhite-12", name: "Kindle Paperwhite", generation: "12ª geração / 2024", resolution: "1264 x 1680", ppi: "300 ppi", note: "7 polegadas, bom para HQ e PDFs." },
      { key: "kindle-paperwhite-11", name: "Kindle Paperwhite", generation: "11ª geração / 2021", resolution: "1236 x 1648", ppi: "300 ppi", note: "6,8 polegadas." },
      { key: "kindle-paperwhite-10", name: "Kindle Paperwhite", generation: "10ª geração / 2018", resolution: "1072 x 1448", ppi: "300 ppi", note: "6 polegadas." },
      { key: "kindle-paperwhite-7", name: "Kindle Paperwhite", generation: "7ª geração / 2015", resolution: "1072 x 1448", ppi: "300 ppi", note: "Também conhecido como Paperwhite 3." },
      { key: "kindle-oasis-10", name: "Kindle Oasis", generation: "10ª geração / 2019", resolution: "1264 x 1680", ppi: "300 ppi", note: "7 polegadas." },
      { key: "kindle-oasis-9", name: "Kindle Oasis", generation: "9ª geração / 2017", resolution: "1264 x 1680", ppi: "300 ppi", note: "7 polegadas." },
      { key: "kindle-oasis-8", name: "Kindle Oasis", generation: "8ª geração / 2016", resolution: "1080 x 1440", ppi: "300 ppi", note: "6 polegadas." },
      { key: "kindle-voyage", name: "Kindle Voyage", generation: "7ª geração / 2014", resolution: "1080 x 1440", ppi: "300 ppi", note: "Tela 6 polegadas de alta densidade." },
      { key: "kindle-scribe-colorsoft-2025", name: "Kindle Scribe Colorsoft", generation: "3ª geração / 2025", resolution: "1980 x 2640", ppi: "300/150 ppi", note: "11 polegadas colorido. Perfil calculado por tela 11 pol. 300 ppi." },
      { key: "kindle-scribe-2025", name: "Kindle Scribe", generation: "3ª geração / 2025", resolution: "1980 x 2640", ppi: "300 ppi", note: "11 polegadas. Perfil calculado por tela 11 pol. 300 ppi." },
      { key: "kindle-scribe-12", name: "Kindle Scribe", generation: "12ª geração / 2024", resolution: "1860 x 2480", ppi: "300 ppi", note: "10,2 polegadas. Excelente para PDF e artbook." },
      { key: "kindle-scribe-11", name: "Kindle Scribe", generation: "11ª geração / 2022", resolution: "1860 x 2480", ppi: "300 ppi", note: "10,2 polegadas." },
      { key: "kindle-colorsoft-12", name: "Kindle Colorsoft", generation: "12ª geração / 2024", resolution: "1264 x 1680", ppi: "300/150 ppi", note: "Colorido; use presets com cor." },
      { key: "kindle-dx", name: "Kindle DX", generation: "2ª geração / 2009", resolution: "824 x 1200", ppi: "150 ppi", note: "Tela grande antiga." },
      { key: "kindle-fire", name: "Kindle Fire", generation: "tablet", resolution: "1200 x 1920", ppi: "colorido", note: "Use HQ colorida, revista ou artbook." },
    ],
  },
  {
    label: "Kobo",
    items: [
      { key: "kobo-clara-bw", name: "Kobo Clara BW", generation: "2024", resolution: "1072 x 1448", ppi: "300 ppi", note: "6 polegadas P&B." },
      { key: "kobo-clara-colour", name: "Kobo Clara Colour", generation: "2024", resolution: "1072 x 1448", ppi: "300/150 ppi", note: "6 polegadas colorido." },
      { key: "kobo-clara-2e", name: "Kobo Clara 2E", generation: "2022", resolution: "1072 x 1448", ppi: "300 ppi", note: "6 polegadas." },
      { key: "kobo-clara-hd", name: "Kobo Clara HD", generation: "2018", resolution: "1072 x 1448", ppi: "300 ppi", note: "6 polegadas." },
      { key: "kobo-libra-colour", name: "Kobo Libra Colour", generation: "2024", resolution: "1264 x 1680", ppi: "300/150 ppi", note: "7 polegadas colorido." },
      { key: "kobo-libra-2", name: "Kobo Libra 2", generation: "2021", resolution: "1264 x 1680", ppi: "300 ppi", note: "7 polegadas." },
      { key: "kobo-sage", name: "Kobo Sage", generation: "2021", resolution: "1440 x 1920", ppi: "300 ppi", note: "8 polegadas." },
      { key: "kobo-elipsa-2e", name: "Kobo Elipsa 2E", generation: "2023", resolution: "1404 x 1872", ppi: "227 ppi", note: "10,3 polegadas para PDFs." },
      { key: "kobo-elipsa", name: "Kobo Elipsa", generation: "2021", resolution: "1404 x 1872", ppi: "227 ppi", note: "10,3 polegadas." },
      { key: "kobo-nia", name: "Kobo Nia", generation: "2020", resolution: "758 x 1024", ppi: "212 ppi", note: "Arquivo leve recomendado." },
    ],
  },
  {
    label: "PocketBook e Nook",
    items: [
      { key: "pocketbook-verse-pro", name: "PocketBook Verse Pro", generation: "6 polegadas", resolution: "1072 x 1448", ppi: "300 ppi", note: "P&B moderno." },
      { key: "pocketbook-era", name: "PocketBook Era", generation: "7 polegadas", resolution: "1264 x 1680", ppi: "300 ppi", note: "Bom para HQ e mangá." },
      { key: "pocketbook-inkpad-3", name: "PocketBook InkPad 3", generation: "7,8 polegadas", resolution: "1404 x 1872", ppi: "300 ppi", note: "Tela grande P&B." },
      { key: "pocketbook-inkpad-color-3", name: "PocketBook InkPad Color 3", generation: "7,8 polegadas", resolution: "1404 x 1872", ppi: "300/150 ppi", note: "Colorido." },
      { key: "pocketbook-inkpad-x", name: "PocketBook InkPad X", generation: "10,3 polegadas", resolution: "1404 x 1872", ppi: "227 ppi", note: "PDFs e livros técnicos." },
      { key: "pocketbook-touch-lux-5", name: "PocketBook Touch Lux 5", generation: "6 polegadas", resolution: "758 x 1024", ppi: "212 ppi", note: "Arquivo leve recomendado." },
      { key: "nook-glowlight-4", name: "Nook GlowLight 4", generation: "6 polegadas", resolution: "1072 x 1448", ppi: "300 ppi", note: "P&B moderno." },
      { key: "nook-glowlight-4-plus", name: "Nook GlowLight 4 Plus", generation: "7,8 polegadas", resolution: "1404 x 1872", ppi: "300 ppi", note: "Tela maior." },
      { key: "nook-color", name: "Nook Color", generation: "tablet antigo", resolution: "600 x 1024", ppi: "colorido", note: "Use presets coloridos leves." },
      { key: "nook-hd-plus", name: "Nook HD Plus", generation: "tablet", resolution: "1280 x 1920", ppi: "colorido", note: "Revista e HQ colorida." },
    ],
  },
  {
    label: "Genérico, Android e tablets",
    items: [
      { key: "generic-eink", name: "Generic e-ink", generation: "6 polegadas antigo", resolution: "600 x 800", ppi: "167 ppi", note: "Compatibilidade e arquivo leve." },
      { key: "generic-hd-eink", name: "Generic HD e-ink", generation: "6 polegadas 300 ppi", resolution: "1072 x 1448", ppi: "300 ppi", note: "Opção segura para e-readers P&B." },
      { key: "generic-large-eink", name: "Generic large e-ink", generation: "8 polegadas", resolution: "1404 x 1872", ppi: "300 ppi", note: "PDF, HQ e apostila." },
      { key: "android-eink-6", name: "Android e-ink", generation: "6 polegadas", resolution: "1072 x 1448", ppi: "300 ppi", note: "Boox, Meebook e similares." },
      { key: "android-eink-7", name: "Android e-ink", generation: "7 polegadas", resolution: "1264 x 1680", ppi: "300 ppi", note: "Boox, Meebook e similares." },
      { key: "android-eink-10", name: "Android e-ink", generation: "10 polegadas", resolution: "1404 x 1872", ppi: "227 ppi", note: "PDFs grandes." },
      { key: "boox-palma", name: "Boox Palma", generation: "smart reader", resolution: "824 x 1648", ppi: "300 ppi", note: "Tela estreita; bom para webtoon." },
      { key: "boox-note-air", name: "Boox Note Air", generation: "10,3 polegadas", resolution: "1404 x 1872", ppi: "227 ppi", note: "PDFs, apostilas e artbooks." },
      { key: "tablet-compact", name: "Tablet compacto", generation: "7-8 polegadas", resolution: "1200 x 1920", ppi: "colorido", note: "HQ, revista e livro ilustrado." },
      { key: "tablet-large", name: "Tablet grande", generation: "10-13 polegadas", resolution: "1600 x 2560", ppi: "colorido", note: "PDFs técnicos e artbooks." },
      { key: "ipad", name: "Apple iPad", generation: "Retina", resolution: "1536 x 2048", ppi: "colorido", note: "Use presets coloridos." },
      { key: "galaxy", name: "Galaxy Tab", generation: "tablet", resolution: "1200 x 1920", ppi: "colorido", note: "Use presets coloridos." },
    ],
  },
  {
    label: "Sony e leitores antigos",
    items: [
      { key: "sony", name: "Sony Reader", generation: "padrão", resolution: "600 x 800", ppi: "antigo", note: "Arquivo leve recomendado." },
      { key: "sony-300", name: "Sony 300", generation: "antigo", resolution: "600 x 800", ppi: "antigo", note: "Arquivo leve recomendado." },
      { key: "sony-900", name: "Sony 900", generation: "antigo", resolution: "600 x 1024", ppi: "antigo", note: "Tela alta." },
      { key: "sony-landscape", name: "Sony Landscape", generation: "paisagem", resolution: "800 x 600", ppi: "antigo", note: "Modo paisagem." },
      { key: "sony-t3", name: "Sony T3", generation: "2013", resolution: "758 x 1024", ppi: "212 ppi", note: "Arquivo leve recomendado." },
      { key: "cybook-3", name: "Cybook 3", generation: "antigo", resolution: "600 x 800", ppi: "antigo", note: "Compatibilidade." },
      { key: "cybook-opus", name: "Cybook Opus", generation: "antigo", resolution: "600 x 800", ppi: "antigo", note: "Compatibilidade." },
      { key: "hanlin-v3", name: "Hanlin V3", generation: "antigo", resolution: "600 x 800", ppi: "antigo", note: "Compatibilidade." },
      { key: "hanlin-v5", name: "Hanlin V5", generation: "antigo", resolution: "600 x 800", ppi: "antigo", note: "Compatibilidade." },
      { key: "iliad", name: "iLiad", generation: "antigo", resolution: "768 x 1024", ppi: "antigo", note: "PDFs simples." },
      { key: "irexdr800", name: "IrexDR800", generation: "antigo", resolution: "768 x 1024", ppi: "antigo", note: "PDFs simples." },
      { key: "irexdr1000", name: "IrexDR1000", generation: "antigo", resolution: "1024 x 1280", ppi: "antigo", note: "PDFs simples." },
    ],
  },
];

const deviceProfiles = Object.fromEntries(deviceProfileGroups.flatMap((group) => group.items.map((item) => [item.key, item])));

const presets = {
  manga: { mode: "manga", quality: 85, gamma: 0.95, crop: true, split: true, protect: true, dither: false, color: false, splitMb: 200 },
  mangaTone: { mode: "manga", quality: 88, gamma: 1, crop: true, split: true, protect: true, dither: true, color: false, splitMb: 200 },
  mangaColor: { mode: "manga", quality: 88, gamma: 1, crop: true, split: true, protect: true, dither: false, color: true, splitMb: 200 },
  comic: { mode: "comic", quality: 86, gamma: 1, crop: true, split: true, protect: true, dither: true, color: false, splitMb: 200 },
  comicColor: { mode: "comic", quality: 88, gamma: 1, crop: true, split: true, protect: true, dither: false, color: true, splitMb: 200 },
  bd: { mode: "comic", quality: 90, gamma: 1, crop: true, split: true, protect: true, dither: true, color: true, splitMb: 220 },
  webtoon: { mode: "webtoon", quality: 84, gamma: 1, crop: true, split: false, protect: false, dither: false, color: false, splitMb: 200 },
  manhua: { mode: "comic", quality: 86, gamma: 0.98, crop: true, split: true, protect: true, dither: false, color: false, splitMb: 200 },
  lightNovel: { mode: "comic", quality: 88, gamma: 0.9, crop: true, split: false, protect: true, dither: true, color: false, splitMb: 200 },
  novel: { mode: "comic", quality: 84, gamma: 0.86, crop: true, split: false, protect: true, dither: false, color: false, splitMb: 180 },
  bookScan: { mode: "comic", quality: 86, gamma: 0.82, crop: true, split: false, protect: true, dither: false, color: false, splitMb: 190 },
  illustratedBook: { mode: "comic", quality: 88, gamma: 0.96, crop: true, split: false, protect: true, dither: true, color: false, splitMb: 210 },
  pdfScan: { mode: "auto", quality: 88, gamma: 0.9, crop: true, split: false, protect: true, dither: false, color: false, splitMb: 200 },
  pdfText: { mode: "auto", quality: 90, gamma: 0.85, crop: true, split: false, protect: false, dither: false, color: false, splitMb: 200 },
  textbook: { mode: "comic", quality: 90, gamma: 0.92, crop: true, split: false, protect: true, dither: true, color: false, splitMb: 220 },
  magazine: { mode: "comic", quality: 88, gamma: 1, crop: true, split: false, protect: true, dither: false, color: true, splitMb: 220 },
  artbook: { mode: "comic", quality: 93, gamma: 1, crop: false, split: true, protect: true, dither: false, color: true, splitMb: 260 },
  photoBook: { mode: "comic", quality: 90, gamma: 1, crop: false, split: false, protect: true, dither: false, color: true, splitMb: 240 },
  auto: { mode: "auto", quality: 85, gamma: 1, crop: true, split: true, protect: true, dither: false, color: false, splitMb: 200 },
};

const quickPresets = {
  quality: { quality: 92, gamma: 1, dither: true, splitMb: 250 },
  light: { quality: 72, gamma: 0.95, dither: false, color: false, splitMb: 180 },
  eink: { quality: 86, gamma: 0.82, crop: true, dither: false, color: false },
  soft: { quality: 84, gamma: 1.08, dither: true, color: false },
  color: { quality: 88, gamma: 1, color: true, dither: false },
  send: { quality: 82, splitMb: 190, crop: true },
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
  sortFilesButton.disabled = busy;
  reverseFilesButton.disabled = busy;
  mergePdfsButton.disabled = busy;
  loadPreviewButton.disabled = busy;
  prevSourcePageButton.disabled = busy || activePreviewPage <= 0;
  nextSourcePageButton.disabled = busy || (activePreviewPageCount !== null && activePreviewPage >= activePreviewPageCount - 1);
  convertButton.querySelector("span").textContent = busy ? "Convertendo" : "Converter";
};

const setPreviewBusy = (busy) => {
  previewButton.disabled = busy;
  loadPreviewButton.disabled = busy;
  prevSourcePageButton.disabled = busy || activePreviewPage <= 0;
  nextSourcePageButton.disabled = busy || (activePreviewPageCount !== null && activePreviewPage >= activePreviewPageCount - 1);
};

const startProgress = () => {
  clearInterval(progressTimer);
  progressIndex = 0;
  progressState = "working";
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
  progressState = "done";
  renderProgress();
};

const failProgress = () => {
  clearInterval(progressTimer);
  progressTimer = null;
  progressState = "error";
  renderProgress();
};

const renderProgress = () => {
  progressList.replaceChildren();
  const total = progressSteps.length;
  const currentStep = progressSteps[Math.min(progressIndex, total - 1)];
  const completedCount = progressState === "done" ? total : Math.min(progressIndex, total - 1);
  const percent =
    progressState === "done"
      ? 100
      : progressState === "working"
        ? Math.min(96, Math.round(((progressIndex + 0.35) / total) * 100))
        : Math.round((completedCount / total) * 100);

  const summary = document.createElement("div");
  summary.className = `progress-summary ${progressState}`;
  const summaryTitle =
    progressState === "done" ? "Conversão concluída" : progressState === "error" ? "Conversão interrompida" : "Conversão em andamento";
  const summaryDetail =
    progressState === "done"
      ? `${total} de ${total} etapas concluídas.`
      : progressState === "error"
        ? `Parou em: ${currentStep.title}.`
        : `Etapa ${Math.min(progressIndex + 1, total)} de ${total}: ${currentStep.title}.`;
  summary.innerHTML = `
    <div class="progress-summary-head">
      <strong>${summaryTitle}</strong>
      <span>${percent}%</span>
    </div>
    <p>${summaryDetail}</p>
    <div class="progress-bar"><span style="width: ${percent}%"></span></div>
  `;
  progressList.append(summary);

  progressSteps.forEach((step, index) => {
    const node = document.createElement("div");
    node.className = "progress-step";
    const isDone = progressState === "done" || index < progressIndex;
    const isActive = progressState === "working" && index === Math.min(progressIndex, total - 1);
    const isError = progressState === "error" && index === Math.min(progressIndex, total - 1);
    if (isDone) node.classList.add("done");
    if (isActive) node.classList.add("active");
    if (isError) node.classList.add("error");

    const marker = document.createElement("span");
    marker.className = "progress-marker";
    marker.textContent = isDone ? "✓" : isError ? "!" : String(index + 1);

    const copy = document.createElement("span");
    copy.className = "progress-copy";
    const title = document.createElement("strong");
    title.textContent = step.title;
    const detail = document.createElement("span");
    detail.textContent = step.detail;
    copy.append(title, detail);
    node.append(marker, copy);
    progressList.append(node);
  });
};

const selectedFormats = () => [...form.querySelectorAll('input[name="format"]:checked')].map((item) => item.value);

const checkedField = (name) => form.querySelector(`input[name="${name}"]`);

const displayFileName = (file) => file?.webkitRelativePath || file?.name || "";

const isPdfFile = (file) => /\.pdf$/i.test(displayFileName(file));

const isImageFile = (file) => /\.(jpe?g|png|webp|gif|bmp|tiff?)$/i.test(displayFileName(file));

const currentPreviewFile = () => {
  if (!selectedFiles.length) return null;
  activePreviewFileIndex = Math.min(Math.max(activePreviewFileIndex, 0), selectedFiles.length - 1);
  return selectedFiles[activePreviewFileIndex];
};

const resetPreviewPage = () => {
  activePreviewPage = 0;
  activePreviewPageCount = null;
};

const syncFiles = (files) => {
  const limited = limitAttachedFiles([...files].filter((file) => file.name));
  selectedFiles = limited.files;
  activePreviewFileIndex = 0;
  resetPreviewPage();
  renderSelectedFiles();
  if (selectedFiles.length === 1 && !titleInput.value.trim()) {
    titleInput.value = fileTitle(selectedFiles[0].name);
  }
  if (selectedFiles.length > 1 && !titleInput.value.trim()) {
    titleInput.value = guessCollectionTitle(selectedFiles);
  }
  if (limited.skipped.total || limited.skipped.pdf || limited.skipped.image) {
    setStatus("done", "Limite aplicado", attachmentLimitMessage(limited));
  }
  schedulePreviewRefresh();
};

const renderSelectedFiles = () => {
  if (!selectedFiles.length) {
    fileLabel.textContent = "Arraste arquivos, CBR/CBZ/PDF ou uma pasta";
    fileMeta.textContent = `Até ${attachmentLimits.pdf} PDFs ou ${attachmentLimits.image} imagens por vez`;
    fileList.hidden = true;
    fileOrderTools.hidden = true;
    mergePdfsButton.disabled = true;
    fileList.replaceChildren();
    renderPreviewSourceControls();
    return;
  }
  const total = selectedFiles.reduce((sum, file) => sum + file.size, 0);
  const pdfCount = selectedFiles.filter(isPdfFile).length;
  const imageCount = selectedFiles.filter(isImageFile).length;
  fileLabel.textContent = selectedFiles.length === 1 ? selectedFiles[0].name : `${selectedFiles.length} arquivos selecionados`;
  fileMeta.textContent = `${formatBytes(total)} · ${pdfCount} PDF(s) · ${imageCount} imagem(ns)`;
  fileList.hidden = false;
  fileOrderTools.hidden = selectedFiles.length < 2;
  fileList.replaceChildren();
  selectedFiles.forEach((file, index) => {
    const chip = document.createElement("div");
    chip.className = "file-chip";
    chip.classList.toggle("active", index === activePreviewFileIndex);
    chip.draggable = true;
    chip.dataset.index = String(index);

    const indexNode = document.createElement("span");
    indexNode.className = "file-index";
    indexNode.textContent = String(index + 1);

    const nameNode = document.createElement("span");
    nameNode.className = "file-name";
    nameNode.textContent = displayFileName(file);

    const sizeNode = document.createElement("strong");
    sizeNode.textContent = formatBytes(file.size);

    const controls = document.createElement("span");
    controls.className = "file-controls";
    [
      ["preview", "Ver", "Mostrar na prévia"],
      ["up", "↑", "Subir"],
      ["down", "↓", "Descer"],
      ["remove", "×", "Remover"],
    ].forEach(([action, label, title]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.action = action;
      button.title = title;
      button.textContent = label;
      controls.append(button);
    });

    chip.append(indexNode, nameNode, sizeNode, controls);
    fileList.append(chip);
  });
  const canMergePdfs = selectedFiles.length >= 2 && selectedFiles.every(isPdfFile);
  mergePdfsButton.disabled = !canMergePdfs;
  mergePdfsButton.title = canMergePdfs ? "Mesclar PDFs na ordem visual" : "Selecione pelo menos dois PDFs";
  renderPreviewSourceControls();
};

const limitAttachedFiles = (files) => {
  const result = {
    files: [],
    skipped: { total: 0, pdf: 0, image: 0 },
    counts: { total: 0, pdf: 0, image: 0 },
  };
  files.forEach((file) => {
    const isPdf = isPdfFile(file);
    const isImage = isImageFile(file);
    if (result.files.length >= attachmentLimits.total) {
      result.skipped.total += 1;
      return;
    }
    if (isPdf && result.counts.pdf >= attachmentLimits.pdf) {
      result.skipped.pdf += 1;
      return;
    }
    if (isImage && result.counts.image >= attachmentLimits.image) {
      result.skipped.image += 1;
      return;
    }
    result.files.push(file);
    result.counts.total += 1;
    if (isPdf) result.counts.pdf += 1;
    if (isImage) result.counts.image += 1;
  });
  return result;
};

const attachmentLimitMessage = (limited) => {
  const skipped = [];
  if (limited.skipped.pdf) skipped.push(`${limited.skipped.pdf} PDF(s)`);
  if (limited.skipped.image) skipped.push(`${limited.skipped.image} imagem(ns)`);
  if (limited.skipped.total) skipped.push(`${limited.skipped.total} arquivo(s) acima do limite total`);
  return `Foram anexados ${limited.files.length} arquivo(s). Ignorado: ${skipped.join(", ")}.`;
};

const moveFile = (from, to) => {
  if (to < 0 || to >= selectedFiles.length || from === to) return;
  const next = [...selectedFiles];
  const [item] = next.splice(from, 1);
  next.splice(to, 0, item);
  selectedFiles = next;
  if (activePreviewFileIndex === from) {
    activePreviewFileIndex = to;
  } else if (from < activePreviewFileIndex && activePreviewFileIndex <= to) {
    activePreviewFileIndex -= 1;
  } else if (to <= activePreviewFileIndex && activePreviewFileIndex < from) {
    activePreviewFileIndex += 1;
  }
  renderSelectedFiles();
};

fileList.addEventListener("click", (event) => {
  const chip = event.target.closest(".file-chip");
  if (!chip) return;
  const index = Number(chip.dataset.index);
  const button = event.target.closest("button[data-action]");
  if (!button) {
    selectPreviewFile(index);
    return;
  }
  const action = button.dataset.action;
  if (action === "preview") selectPreviewFile(index);
  if (action === "up") {
    moveFile(index, index - 1);
    schedulePreviewRefresh();
  }
  if (action === "down") {
    moveFile(index, index + 1);
    schedulePreviewRefresh();
  }
  if (action === "remove") {
    selectedFiles.splice(index, 1);
    if (activePreviewFileIndex === index) {
      activePreviewFileIndex = Math.min(index, Math.max(0, selectedFiles.length - 1));
      resetPreviewPage();
    } else if (index < activePreviewFileIndex) {
      activePreviewFileIndex -= 1;
    }
    renderSelectedFiles();
    if (selectedFiles.length) {
      schedulePreviewRefresh();
    } else {
      renderPreview([]);
    }
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
  schedulePreviewRefresh();
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
  const activeFile = currentPreviewFile();
  selectedFiles.sort(naturalCompare);
  activePreviewFileIndex = Math.max(0, selectedFiles.indexOf(activeFile));
  renderSelectedFiles();
  schedulePreviewRefresh();
});

reverseFilesButton.addEventListener("click", () => {
  const length = selectedFiles.length;
  selectedFiles.reverse();
  activePreviewFileIndex = length - 1 - activePreviewFileIndex;
  renderSelectedFiles();
  schedulePreviewRefresh();
});

mergePdfsButton.addEventListener("click", async () => {
  await mergeSelectedPdfs();
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
  setControlValues(preset);
  document.querySelectorAll(".quick-preset-button").forEach((button) => button.classList.remove("active"));
  syncControlText();
  schedulePreviewRefresh();
};

const applyQuickPreset = (name) => {
  const preset = quickPresets[name];
  if (!preset) return;
  setControlValues(preset);
  document.querySelectorAll(".quick-preset-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.quickPreset === name);
  });
  syncControlText();
  schedulePreviewRefresh();
};

const setControlValues = (preset) => {
  if (preset.mode !== undefined) modeInput.value = preset.mode;
  if (preset.quality !== undefined) qualityInput.value = String(preset.quality);
  if (preset.gamma !== undefined) gammaInput.value = String(preset.gamma);
  if (preset.splitMb !== undefined) splitSizeInput.value = String(preset.splitMb);
  if (preset.crop !== undefined) checkedField("crop").checked = preset.crop;
  if (preset.split !== undefined) splitInput.checked = preset.split;
  if (preset.protect !== undefined) protectFirstInput.checked = preset.protect;
  if (preset.dither !== undefined) checkedField("dither").checked = preset.dither;
  if (preset.color !== undefined) checkedField("color").checked = preset.color;
};

const syncControlText = () => {
  qualityValue.textContent = qualityInput.value;
  gammaValue.textContent = Number(gammaInput.value).toFixed(2);
  syncProfileText();
  if (modeInput.value === "webtoon") {
    splitInput.checked = false;
    splitInput.disabled = true;
    protectFirstInput.disabled = true;
  } else {
    splitInput.disabled = false;
    protectFirstInput.disabled = false;
  }
};

const buildProfileOptions = () => {
  profileSelect.replaceChildren();
  deviceProfileGroups.forEach((group) => {
    const optgroup = document.createElement("optgroup");
    optgroup.label = group.label;
    group.items.forEach((profile) => {
      const option = document.createElement("option");
      option.value = profile.key;
      option.textContent = `${profile.name} · ${profile.generation} · ${profile.resolution} · ${profile.ppi}`;
      if (profile.key === "kindle-basic-11") option.selected = true;
      optgroup.append(option);
    });
    profileSelect.append(optgroup);
  });
};

const syncProfileText = () => {
  const profile = deviceProfiles[profileSelect.value] || deviceProfiles["kindle-basic-11"];
  profilePill.textContent = `${profile.name} · ${profile.resolution}`;
  profileInfo.innerHTML = `
    <div>
      <strong>${profile.name}</strong>
      <span>${profile.generation}</span>
    </div>
    <div>
      <strong>${profile.resolution}</strong>
      <span>${profile.ppi}</span>
    </div>
    <p>${profile.note}</p>
  `;
};

const buildPayload = (files = selectedFiles, extras = {}, options = {}) => {
  if (!files.length) throw new Error("Escolha arquivos ou uma pasta.");
  const payload = new FormData(form);
  payload.delete("file");
  payload.delete("format");
  if (!options.skipFormats) {
    const formats = selectedFormats();
    if (!formats.length) throw new Error("Marque pelo menos um formato.");
    payload.append("format", formats.join(","));
  }
  payload.set("profile", profileSelect.value || "kindle11");
  payload.set("profileLabel", deviceProfiles[profileSelect.value]?.name || "Leitor selecionado");
  files.forEach((file) => payload.append("file", file, file.webkitRelativePath || file.name));
  Object.entries(extras).forEach(([key, value]) => {
    payload.set(key, String(value));
  });
  if (coverInput.files[0]) {
    payload.append("coverFile", coverInput.files[0], coverInput.files[0].name);
  }
  return payload;
};

const mergeSelectedPdfs = async () => {
  if (selectedFiles.length < 2) {
    setStatus("error", "Poucos PDFs", "Escolha pelo menos dois PDFs para mesclar.");
    return;
  }
  if (!selectedFiles.every(isPdfFile)) {
    setStatus("error", "Só PDFs", "Remova CBR, CBZ, imagens ou outros formatos antes de mesclar.");
    return;
  }
  try {
    const originalCount = selectedFiles.length;
    const payload = buildPayload(selectedFiles, {}, { skipFormats: true });
    setBusy(true);
    mergePdfsButton.textContent = "Mesclando";
    setStatus("working", "Mesclando PDFs", "Usando a ordem visual da lista.");
    resultList.hidden = true;
    resultList.replaceChildren();
    const response = await fetch("/api/merge-pdfs", { method: "POST", body: payload });
    const data = await response.json();
    if (!response.ok) throw new Error(friendlyApiError(data, "Não consegui mesclar os PDFs."));
    renderResults([data]);
    const mergedFiles = [];
    for (const merged of data.files || []) {
      if (merged?.url) {
        const fileResponse = await fetch(merged.url);
        if (fileResponse.ok) {
          const blob = await fileResponse.blob();
          mergedFiles.push(new File([blob], merged.name, { type: "application/pdf" }));
        }
      }
    }
    if (mergedFiles.length) syncFiles(mergedFiles);
    form.querySelector('input[name="groupMode"][value="batch"]').checked = true;
    const resultCount = data.files?.length || mergedFiles.length || 1;
    const resultText = resultCount > 1 ? `${resultCount} partes abaixo de ${data.limitMb || 200} MB` : "1 PDF";
    setStatus("done", "PDFs mesclados", `${originalCount} PDFs viraram ${resultText}.`);
    await loadHistory();
  } catch (error) {
    setStatus("error", "Mesclagem falhou", error.message || "Não foi possível mesclar os PDFs.");
  } finally {
    setBusy(false);
    mergePdfsButton.textContent = "Mesclar PDFs";
    renderSelectedFiles();
  }
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

document.querySelectorAll(".quick-preset-button").forEach((button) => {
  button.addEventListener("click", () => applyQuickPreset(button.dataset.quickPreset));
});

profileSelect.addEventListener("change", () => {
  syncProfileText();
  schedulePreviewRefresh();
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

const selectPreviewFile = (index, load = true) => {
  if (index < 0 || index >= selectedFiles.length) return;
  activePreviewFileIndex = index;
  resetPreviewPage();
  renderSelectedFiles();
  if (load) generateSourcePreview();
};

const renderPreviewSourceControls = () => {
  previewSourceBar.hidden = !selectedFiles.length;
  previewSourceSelect.replaceChildren();
  if (!selectedFiles.length) {
    previewPageInput.value = "1";
    setPreviewBusy(false);
    return;
  }
  currentPreviewFile();
  selectedFiles.forEach((file, index) => {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `${index + 1}. ${displayFileName(file)}`;
    previewSourceSelect.append(option);
  });
  previewSourceSelect.value = String(activePreviewFileIndex);
  previewPageInput.value = String(activePreviewPage + 1);
  if (activePreviewPageCount !== null) {
    previewPageInput.max = String(activePreviewPageCount);
  } else {
    previewPageInput.removeAttribute("max");
  }
  prevSourcePageButton.disabled = activePreviewPage <= 0;
  nextSourcePageButton.disabled = activePreviewPageCount !== null && activePreviewPage >= activePreviewPageCount - 1;
};

const schedulePreviewRefresh = () => {
  clearTimeout(previewAutoTimer);
  if (!selectedFiles.length) return;
  previewAutoTimer = setTimeout(() => generateSourcePreview({ silent: true }), 350);
};

const selectedPreviewItems = (data) =>
  data.previews || (data.images || []).map((src) => ({ src, label: "Prévia", detail: "" }));

const generateSourcePreview = async ({ silent = false } = {}) => {
  const file = currentPreviewFile();
  if (!file) {
    renderPreview([]);
    return false;
  }
  clearTimeout(previewAutoTimer);
  const requestId = ++previewRequestId;
  try {
    const payload = buildPayload([file], { previewPage: activePreviewPage });
    setPreviewBusy(true);
    renderPreviewSourceControls();
    if (!silent) {
      setStatus("working", "Gerando prévia", `${displayFileName(file)} · página ${activePreviewPage + 1}`);
    }
    const response = await fetch("/api/preview", { method: "POST", body: payload });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Prévia falhou.");
    if (requestId !== previewRequestId) return false;
    activePreviewPageCount = Number.isFinite(Number(data.pageCount)) && Number(data.pageCount) > 0 ? Number(data.pageCount) : null;
    renderPreview(selectedPreviewItems(data), "after");
    renderPreviewSourceControls();
    if (!silent) {
      const total = activePreviewPageCount ? ` de ${activePreviewPageCount}` : "";
      setStatus("done", "Prévia pronta", `${displayFileName(file)} · página ${activePreviewPage + 1}${total}`);
    }
    return true;
  } catch (error) {
    if (requestId !== previewRequestId) return false;
    setStatus("error", "Prévia falhou", error.message || "Não foi possível gerar prévia.");
    return false;
  } finally {
    if (requestId === previewRequestId) setPreviewBusy(false);
  }
};

const setPreviewPage = async (pageIndex) => {
  const previous = activePreviewPage;
  activePreviewPage = Math.max(0, pageIndex);
  renderPreviewSourceControls();
  const ok = await generateSourcePreview();
  if (!ok) {
    activePreviewPage = previous;
    renderPreviewSourceControls();
  }
};

previewButton.addEventListener("click", async () => {
  await generateSourcePreview();
});

previewSourceSelect.addEventListener("change", () => {
  selectPreviewFile(Number(previewSourceSelect.value));
});

loadPreviewButton.addEventListener("click", () => {
  setPreviewPage(Number(previewPageInput.value || 1) - 1);
});

previewPageInput.addEventListener("change", () => {
  setPreviewPage(Number(previewPageInput.value || 1) - 1);
});

previewPageInput.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  event.preventDefault();
  setPreviewPage(Number(previewPageInput.value || 1) - 1);
});

prevSourcePageButton.addEventListener("click", () => {
  if (activePreviewPage <= 0) return;
  setPreviewPage(activePreviewPage - 1);
});

nextSourcePageButton.addEventListener("click", () => {
  setPreviewPage(activePreviewPage + 1);
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = buildPayload(selectedFiles);
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
    failProgress();
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

const renderPreview = (items, preferredKind = "") => {
  previewItems = items || [];
  const preferredIndex = preferredKind ? previewItems.findIndex((item) => item.kind === preferredKind) : -1;
  previewIndex = preferredIndex >= 0 ? preferredIndex : 0;
  previewZoomed = false;
  zoomPreviewButton.textContent = "Zoom";
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
  const file = currentPreviewFile();
  const fileLabelText = file ? ` — ${displayFileName(file)}` : "";
  const viewCount = previewItems.length > 1 ? ` · visão ${previewIndex + 1}/${previewItems.length}` : "";
  previewTitle.textContent = `${item.label || "Prévia"}${fileLabelText}`;
  previewDetail.textContent = `${item.detail || `${item.width || 1072} x ${item.height || 1448}`}${viewCount}`;
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
  selectedMetadataKey = "";
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "message-box";
    empty.textContent = "Nenhum resultado encontrado. Tente o nome da série sem número de capítulo.";
    metadataResults.append(empty);
    return;
  }
  items.forEach((item, index) => {
    const card = document.createElement("div");
    const confidence = Number(item.confidence || 0);
    const key = metadataKey(item, index);
    card.className = `metadata-card ${confidence < 55 ? "low-confidence" : ""}`;
    card.dataset.key = key;
    card.addEventListener("click", () => markMetadataSelection(key));

    const cover = document.createElement("img");
    cover.className = "metadata-cover";
    cover.alt = item.cover_url ? `Capa de ${item.title || "resultado"}` : "";
    cover.src = item.cover_url || "";

    const text = document.createElement("div");
    text.className = "metadata-copy";
    if (index === 0 && confidence >= 65) {
      const recommended = document.createElement("span");
      recommended.className = "metadata-badge";
      recommended.textContent = "Recomendado";
      text.append(recommended);
    }
    const title = document.createElement("strong");
    title.textContent = item.title || "Sem título";
    const meta = document.createElement("span");
    meta.textContent = [item.author, item.year, item.language, item.source].filter(Boolean).join(" · ");
    const description = document.createElement("span");
    description.textContent = item.description ? item.description.slice(0, 180) : "Sem descrição nessa fonte.";
    const tag = document.createElement("span");
    tag.className = `confidence-tag ${confidence < 55 ? "low" : ""}`;
    tag.textContent = confidence ? `${confidence}% confiança` : "Sem score";
    const meter = document.createElement("span");
    meter.className = "confidence-meter";
    meter.innerHTML = `<i style="width: ${Math.max(4, Math.min(100, confidence || 0))}%"></i>`;
    const warning = document.createElement("span");
    warning.className = "metadata-warning";
    warning.textContent = item.warning || "";
    text.append(title, meta, description, tag, meter, warning);

    const actions = document.createElement("div");
    actions.className = "item-actions";
    const allButton = metadataAction("Aplicar tudo", () => applyMetadata(item, "all", key));
    const coverButton = metadataAction("Capa", () => applyMetadata(item, "cover", key));
    const descButton = metadataAction("Descrição", () => applyMetadata(item, "description", key));
    actions.append(allButton, coverButton, descButton);
    if (item.external_url) {
      const sourceLink = document.createElement("a");
      sourceLink.href = item.external_url;
      sourceLink.target = "_blank";
      sourceLink.rel = "noreferrer";
      sourceLink.textContent = "Fonte";
      sourceLink.addEventListener("click", (event) => event.stopPropagation());
      actions.append(sourceLink);
    }

    card.append(cover, text, actions);
    metadataResults.append(card);
  });
  markMetadataSelection(metadataKey(items[0], 0));
};

const metadataKey = (item, index) => `${index}:${item.source || ""}:${item.title || ""}:${item.year || ""}`;

const markMetadataSelection = (key) => {
  selectedMetadataKey = key;
  metadataResults.querySelectorAll(".metadata-card").forEach((card) => {
    card.classList.toggle("selected", card.dataset.key === selectedMetadataKey);
  });
};

const metadataAction = (label, handler) => {
  const button = document.createElement("button");
  button.type = "button";
  button.textContent = label;
  button.addEventListener("click", (event) => {
    event.stopPropagation();
    handler();
  });
  return button;
};

const applyMetadata = (item, mode, key = "") => {
  if (key) markMetadataSelection(key);
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
  const isMerge = item.kind === "merge-pdf";
  const splitText = item.split ? " dividido em partes" : "";
  const modeText = item.mode || (isMerge ? "PDF mesclado" : "Convertido");
  node.innerHTML = `
    <div class="result-head">
      <strong>${item.title}</strong>
      <span>${item.pages} pág. · ${modeText}${splitText}</span>
    </div>
  `;
  const io = document.createElement("div");
  io.className = "io-summary";
  const inputSize = item.input ? formatBytes(item.input.size) : "";
  const outputSize = item.outputSize ? formatBytes(item.outputSize) : "";
  const targetLabel = item.profile?.label || "Leitor selecionado";
  const targetResolution = item.profile?.resolution ? ` · ${item.profile.resolution.replace("x", " x ")}` : "";
  const mergeDetail = item.split
    ? `${outputSize} · dividido para Send to Kindle`
    : `${outputSize} · PDF mesclado na ordem visual`;
  const outputDetail = isMerge ? mergeDetail : `${outputSize} · Otimizado para ${targetLabel}${targetResolution}`;
  io.innerHTML = `
    <div class="io-box">
      <span class="eyebrow">Entrada</span>
      <strong>${item.input?.name || item.title}</strong>
      <span>${inputSize}${item.input?.count ? ` · ${item.input.count} arquivo(s)` : ""}</span>
    </div>
    <div class="io-box">
      <span class="eyebrow">Saída</span>
      <strong>${item.files?.[0]?.name || "Arquivo convertido"}</strong>
      <span>${outputDetail}</span>
    </div>
  `;
  const tags = document.createElement("div");
  tags.className = "status-tags";
  const tagValues = isMerge
    ? ["PDF mesclado", item.sendToKindleSafe ? `≤ ${item.limitMb || 200} MB` : "ver tamanho", `${item.files?.length || 1} arquivo(s)`, `${item.pages} páginas`]
    : [item.mode, targetLabel, `${item.pages} páginas`, item.split ? "partes" : "único"];
  tagValues.forEach((value) => {
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
buildProfileOptions();
syncFiles([]);
syncControlText();
renderPreview([]);
loadHistory();
