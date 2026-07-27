const CLASSES = [
  "airplane",
  "automobile",
  "bird",
  "cat",
  "deer",
  "dog",
  "frog",
  "horse",
  "ship",
  "truck",
];

const modelUrl = new URL("./resnet50_cifar10.onnx", document.baseURI).href;

const toggleButton = document.getElementById("toggleDetails");
const detailsPanel = document.getElementById("detailsPanel");
const imageInput = document.getElementById("imageInput");
const previewCanvas = document.getElementById("previewCanvas");
const previewHint = document.getElementById("previewHint");
const loadModelButton = document.getElementById("loadModelButton");
const runButton = document.getElementById("runButton");
const modelStatus = document.getElementById("modelStatus");
const statusLine = document.getElementById("statusLine");
const predictionBanner = document.getElementById("predictionBanner");
const predictionList = document.getElementById("predictionList");
const latencyValue = document.getElementById("latencyValue");
const topClassValue = document.getElementById("topClassValue");

const previewContext = previewCanvas?.getContext("2d");
const preprocessCanvas = document.createElement("canvas");
preprocessCanvas.width = 224;
preprocessCanvas.height = 224;
const preprocessContext = preprocessCanvas.getContext("2d");

let sessionPromise = null;
let currentImage = null;
let currentFileName = "";

function setStatus(text, tone = "idle") {
  if (statusLine) {
    statusLine.textContent = text;
    statusLine.dataset.tone = tone;
  }
  if (modelStatus) {
    modelStatus.textContent = text;
    modelStatus.dataset.tone = tone;
  }
}

function softmax(values) {
  const max = Math.max(...values);
  const exps = values.map((value) => Math.exp(value - max));
  const sum = exps.reduce((accumulator, value) => accumulator + value, 0);
  return exps.map((value) => value / sum);
}

function formatConfidence(probability) {
  return `${(probability * 100).toFixed(1)}%`;
}

function renderPreview(image) {
  if (!previewContext || !previewCanvas) {
    return;
  }

  previewContext.clearRect(0, 0, previewCanvas.width, previewCanvas.height);
  previewContext.fillStyle = "#f8f4ec";
  previewContext.fillRect(0, 0, previewCanvas.width, previewCanvas.height);

  const scale = Math.min(
    previewCanvas.width / image.width,
    previewCanvas.height / image.height,
  );
  const width = image.width * scale;
  const height = image.height * scale;
  const x = (previewCanvas.width - width) / 2;
  const y = (previewCanvas.height - height) / 2;

  previewContext.drawImage(image, x, y, width, height);
}

function setPredictionState(message) {
  if (predictionBanner) {
    predictionBanner.textContent = message;
  }
}

function renderPredictions(probabilities) {
  if (!predictionList) {
    return;
  }

  predictionList.innerHTML = probabilities
    .map(
      ({ className, probability }) => `
        <li class="prediction-item">
          <div class="prediction-meta">
            <span>${className}</span>
            <strong>${formatConfidence(probability)}</strong>
          </div>
          <div class="prediction-bar"><span style="width: ${Math.max(probability * 100, 2)}%"></span></div>
        </li>
      `,
    )
    .join("");
}

async function loadImageFromFile(file) {
  const image = new Image();
  image.src = URL.createObjectURL(file);

  await new Promise((resolve, reject) => {
    image.onload = resolve;
    image.onerror = reject;
  });

  currentImage = image;
  currentFileName = file.name;
  renderPreview(image);

  if (previewHint) {
    previewHint.textContent = `Loaded ${file.name}.`;
  }

  if (runButton) {
    runButton.disabled = false;
  }
}

async function ensureSession() {
  if (sessionPromise) {
    return sessionPromise;
  }

  if (typeof ort === "undefined") {
    throw new Error("ONNX Runtime Web failed to load.");
  }

  if (window.location.protocol === "file:") {
    throw new Error("Open the page through a local web server so the ONNX file can be fetched.");
  }

  ort.env.wasm.wasmPaths = "https://cdn.jsdelivr.net/npm/onnxruntime-web/dist/";
  setStatus("Loading ONNX model...", "loading");

  sessionPromise = ort.InferenceSession.create(modelUrl, {
    executionProviders: ["wasm"],
    graphOptimizationLevel: "all",
  }).then((session) => {
    setStatus("Model loaded and ready.", "ready");
    return session;
  });

  return sessionPromise;
}

function preprocessImage(image) {
  if (!preprocessContext) {
    throw new Error("Canvas API is unavailable in this browser.");
  }

  preprocessContext.clearRect(0, 0, preprocessCanvas.width, preprocessCanvas.height);
  preprocessContext.drawImage(image, 0, 0, preprocessCanvas.width, preprocessCanvas.height);

  const { data } = preprocessContext.getImageData(0, 0, preprocessCanvas.width, preprocessCanvas.height);
  const floatData = new Float32Array(3 * 224 * 224);
  const mean = [0.485, 0.456, 0.406];
  const std = [0.229, 0.224, 0.225];
  const pixels = 224 * 224;

  for (let index = 0; index < pixels; index += 1) {
    const base = index * 4;
    const red = data[base] / 255;
    const green = data[base + 1] / 255;
    const blue = data[base + 2] / 255;

    floatData[index] = (red - mean[0]) / std[0];
    floatData[pixels + index] = (green - mean[1]) / std[1];
    floatData[pixels * 2 + index] = (blue - mean[2]) / std[2];
  }

  return new ort.Tensor("float32", floatData, [1, 3, 224, 224]);
}

async function runInference() {
  if (!currentImage) {
    setStatus("Choose an image before running inference.", "error");
    return;
  }

  try {
    if (runButton) {
      runButton.disabled = true;
    }

    const session = await ensureSession();
    const inputName = session.inputNames[0];
    const outputName = session.outputNames[0];
    const inputTensor = preprocessImage(currentImage);

    setStatus(`Classifying ${currentFileName || "image"}...`, "loading");
    const start = performance.now();
    const outputs = await session.run({ [inputName]: inputTensor });
    const elapsed = performance.now() - start;
    const logits = Array.from(outputs[outputName].data);
    const probabilities = softmax(logits)
      .map((probability, index) => ({ className: CLASSES[index], probability }))
      .sort((left, right) => right.probability - left.probability);

    renderPredictions(probabilities.slice(0, 3));

    if (predictionBanner) {
      predictionBanner.textContent = `Top prediction: ${probabilities[0].className}`;
    }
    if (latencyValue) {
      latencyValue.textContent = `${elapsed.toFixed(2)} ms`;
    }
    if (topClassValue) {
      topClassValue.textContent = probabilities[0].className;
    }

    setStatus(`Prediction complete. Top class: ${probabilities[0].className}.`, "ready");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Inference failed.";
    setStatus(message, "error");
  } finally {
    if (runButton) {
      runButton.disabled = !currentImage;
    }
  }
}

toggleButton?.addEventListener("click", () => {
  const hidden = detailsPanel.classList.toggle("hidden");
  toggleButton.textContent = hidden ? "Show rollout checklist" : "Hide rollout checklist";
});

loadModelButton?.addEventListener("click", async () => {
  try {
    await ensureSession();
  } catch (error) {
    const message = error instanceof Error ? error.message : "Model loading failed.";
    setStatus(message, "error");
  }
});

imageInput?.addEventListener("change", async (event) => {
  const target = event.target;
  const file = target?.files?.[0];
  if (!file) {
    return;
  }

  try {
    await loadImageFromFile(file);
    setPredictionState("Image ready. Run inference to classify it.");
    setStatus("Image loaded. Load the model or run inference.", "ready");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to load image.";
    setStatus(message, "error");
  }
});

runButton?.addEventListener("click", runInference);

setPredictionState("Awaiting inference.");

if (window.location.protocol === "file:") {
  setStatus("Open this page through a local web server so the ONNX file can be fetched.", "error");
}
