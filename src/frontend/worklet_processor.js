class AudioProcessor extends AudioWorkletProcessor {
    process(inputs, outputs, parameters) {
        // inputs is an array of inputs, each with channels
        const input = inputs[0]; // First input
        if (input.length > 0) {
            const channel = input[0]; // First channel (mono)
            // Post the Float32Array to the main thread
            this.port.postMessage(channel);
        }
        // Keep the processor alive
        return true;
    }
}

registerProcessor('audio-processor', AudioProcessor);
