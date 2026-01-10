// Frontend Logic for AutoShavian

const btnRecord = document.getElementById('btn-record');
const btnTranscribe = document.getElementById('btn-transcribe');
const btnClear = document.getElementById('btn-clear');
const statusSpan = document.getElementById('status');
const outEnglish = document.getElementById('output-english');
const outShavian = document.getElementById('output-shavian');

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

        // Append text
        outEnglish.innerText += (outEnglish.innerText ? ' ' : '') + data.text;
        outShavian.innerText += (outShavian.innerText ? ' ' : '') + data.shavian;

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
                ws.send(inputData.buffer);
            }
        };

        isRecording = true;
        btnRecord.innerText = "Stop Recording";
        btnTranscribe.disabled = true;
        statusSpan.innerText = "Recording...";

    } catch (err) {
        console.error("Error accessing mic:", err);
        alert("Could not access microphone");
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

    btnRecord.innerText = "Start Recording";
    btnTranscribe.disabled = false;
    statusSpan.innerText = "Recording stopped. Ready to transcribe.";

    // Auto-trigger transcribe for convenience?
    // Let's make it manual as per button labels, or auto?
    // "Stop" usually implies "I'm done, process it".
    transcribe();
}

function transcribe() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        statusSpan.innerText = "Transcribing...";
        ws.send(JSON.stringify({ action: "transcribe" }));
    }
}

btnRecord.onclick = () => {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
};

btnTranscribe.onclick = transcribe;

btnClear.onclick = () => {
    outEnglish.innerText = "";
    outShavian.innerText = "";
};

// Start connection
connectWS();
