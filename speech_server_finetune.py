import zmq
import torch
import tempfile
import os
import sys
from opencc import OpenCC
from transformers import WhisperProcessor, WhisperForConditionalGeneration

class SttServer:
    def __init__(self, model_path="./whisper-finetuned-final", processor_path="./processor_files"):
        self.service_name = "wav-to-text"

        # Load fine-tuned Whisper model
        print(f"Loading fine-tuned Whisper model from {model_path}...")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        device = os.environ.get('DEVICE', device)
        print(f"STT sets device as {device}")

        # Load processor and model from local directories
        self.processor = WhisperProcessor.from_pretrained(
            processor_path,
            local_files_only=True
        )

        self.model = WhisperForConditionalGeneration.from_pretrained(
            model_path,
            local_files_only=True
        ).to(device)

        # ✅ [FIXED] Clear default forced decoder ids to avoid conflicts
        self.model.generation_config.forced_decoder_ids = None

        print("Model and processor loaded successfully!")

        self.device = device
        self.cc = OpenCC('t2s')  # Traditional to Simplified

        self.url = os.environ.get('ZMQ_BACKEND_ROUTER_URL', 'tcp://localhost:5560')

        # Initialize ZMQ context and socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(self.url)

        # Register with broker
        self.socket.send_multipart([self.service_name.encode()])
    
    def process_audio(self, audio_data):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav.write(audio_data)
            temp_wav.flush()
            temp_path = temp_wav.name

        try:
            import librosa
            audio_array, sampling_rate = librosa.load(temp_path, sr=16000)  # pyright: ignore[reportUnusedVariable, reportUnusedVariable]

            inputs = self.processor(
                audio=audio_array,
                sampling_rate=16000,
                return_tensors="pt"
            )
            input_features = inputs.input_features.to(self.device)

            # Generate decoder prompts using processor
            forced_decoder_ids = self.processor.get_decoder_prompt_ids(
                task="transcribe"
            )

            # Generate transcription
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    input_features,
                    forced_decoder_ids=forced_decoder_ids
                )

            text = self.processor.batch_decode(
                predicted_ids,
                skip_special_tokens=True
            )[0]

            text = self.cc.convert(text)
            os.unlink(temp_path)
            return text

        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return f"Error in transcription: {str(e)}"

    def run(self):
        print("Fine-tuned Whisper speech-to-text server is running...")
        
        while True:
            try:
                print("STT server is waiting for a message ...")

                # multipart message format:
                # +------------+-----------+-------------+--------------+
                # | clientAddr | requestID | serviceType | inputPayload |
                # +------------+-----------+-------------+--------------+

                message = self.socket.recv_multipart()

                audio = message[3]
                result = self.process_audio(audio)
                print(f"The recognized text is {result}")
                
                self.socket.send_multipart(message[:3] + [result.encode()])
                
            except Exception as e:
                error_msg = f"Error processing request: {str(e)}"
                print(error_msg)
                self.socket.send_multipart(message[:3] + [b""])

def main():
    sys.stdout = sys.stderr

    # Paths to your fine-tuned model and processor files
    model_path = os.environ.get('MODEL_PATH', './whisper-finetuned-final')
    processor_path = os.environ.get('PROCESSOR_PATH', './processor_files')

    server = SttServer(model_path=model_path, processor_path=processor_path)
    server.run()

if __name__ == "__main__":
    main()
