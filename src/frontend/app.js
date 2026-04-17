// Frontend Logic for AutoShavian

const btnRecord = document.getElementById('btn-record');
const btnTranslate = document.getElementById('btn-translate');
const btnClear = document.getElementById('btn-clear');
const statusSpan = document.getElementById('status');
const inputEnglish = document.getElementById('input-english');
const outShavian = document.getElementById('output-shavian');
const modeToggle = document.getElementById('mic-mode-toggle');

let ws;
let audioContext;
let processor;
let input;
let isRecording = false;

// Initialize WebSocket
function connectWS() {
    ws = new WebSocket('ws://localhost:8000/ws/transcribe');

    ws.onopen = () => {
        console.log('Connected to backend');
        statusSpan.innerText = 'Connected';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received:', data);

        // Check if data is from a manual translation request
        if (data.is_translation) {
            // Update English text with IPA append
            // Reconstruct the English text with IPA in brackets
            // e.g. "Hello" -> "Hello [/həˈloʊ/]"
            // We'll replace the text in the box with the translated text if it's the exact same
            // to avoid duplicates, or just append if it's new (for simplicity, we'll replace the exact text translated)
            // But since the user might have modified the text box while waiting, it's safest to just update the full text.
            inputEnglish.value = data.english_with_ipa;
            outShavian.innerText = data.shavian;
            statusSpan.innerText = 'Translated';
            return;
        }

        // Otherwise, it's an automatic VAD transcription
        const isDirectToShavian = modeToggle.checked;

        if (isDirectToShavian) {
            // Option 1 Direct Mode: Skip English box (or append to it automatically) and append Shavian directly
            inputEnglish.value += (inputEnglish.value ? ' ' : '') + data.english_with_ipa;
            outShavian.innerText += (outShavian.innerText ? ' ' : '') + data.shavian;
        } else {
            // Speech to English mode: Just append to the English box
            inputEnglish.value += (inputEnglish.value ? ' ' : '') + data.text;
        }

        statusSpan.innerText = 'Transcribed';
    };

    ws.onclose = () => {
        console.log('Disconnected');
        statusSpan.innerText = 'Disconnected (Refresh to reconnect)';
    };

    ws.onerror = (err) => {
        console.error('WS Error:', err);
        statusSpan.innerText = 'Error';
    };
}

// Audio Handling
async function startRecording() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert("WebSocket not connected");
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        input = audioContext.createMediaStreamSource(stream);

        // Load the worklet
        await audioContext.audioWorklet.addModule('worklet_processor.js');
        processor = new AudioWorkletNode(audioContext, 'audio-processor');

        input.connect(processor);
        processor.connect(audioContext.destination);

        processor.port.onmessage = (event) => {
            if (!isRecording) return;
            const inputData = event.data;
            // inputData is a Float32Array from the processor
            if (ws && ws.readyState === WebSocket.OPEN) {
                // Determine mode to tell backend how to handle it?
                // Actually backend can just stream text, we handle formatting locally.
                ws.send(inputData.buffer);
            }
        };

        isRecording = true;
        btnRecord.innerText = "Stop Mic";
        statusSpan.innerText = "Recording...";

    } catch (err) {
        console.error("Error accessing mic:", err);
        alert("Could not access microphone. Ensure you are using http://localhost or HTTPS.");
    }
}

function stopRecording() {
    isRecording = false;
    if (processor) {
        processor.disconnect();
        input.disconnect();
    }
    if (audioContext) {
        audioContext.close();
    }

    btnRecord.innerText = "Start Mic";

    if (ws && ws.readyState === WebSocket.OPEN) {
        statusSpan.innerText = "Transcribing...";
        // Tell backend to flush VAD buffer
        ws.send(JSON.stringify({ action: "flush" }));
    }
}

btnRecord.onclick = () => {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
};

btnTranslate.onclick = () => {
    const textToTranslate = inputEnglish.value.trim();
    if (!textToTranslate) return;

    if (ws && ws.readyState === WebSocket.OPEN) {
        statusSpan.innerText = "Translating...";
        // Send translation request to backend
        ws.send(JSON.stringify({
            action: "translate_text",
            text: textToTranslate
        }));
    } else {
        alert("WebSocket not connected");
    }
};

btnClear.onclick = () => {
    inputEnglish.value = "";
    outShavian.innerText = "";
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "clear" }));
    }
};

// Start connection
connectWS();
