# STT Production System

A production-ready Speech-to-Text (STT) system built around a fine-tuned Whisper model, designed to run in a containerized microservices architecture.

**Repository**: [https://github.com/MirxaWaqarBaig/SST-Prod.git](https://github.com/MirxaWaqarBaig/SST-Prod.git)

## Overview

This system provides high-quality speech-to-text transcription using a fine-tuned Whisper model with GPU acceleration. It's designed as a microservice that integrates with a broker and gateway system for scalable deployment.

## Architecture

The system consists of three main components:

- **STT Server**: Fine-tuned Whisper model service for audio transcription
- **Broker**: ZMQ-based message broker for inter-service communication
- **Gateway**: HTTP API gateway for client requests

## Prerequisites

- Docker and Docker Compose
- NVIDIA GPU with CUDA support (for optimal performance)
- At least 8GB RAM
- 10GB+ free disk space for model files

## Project Structure

```
STT_Prod/
├── docker-compose_STT.yml          # Docker Compose configuration
├── Dockerfile.STT                  # STT service Dockerfile
├── requirements_STT.txt            # Python dependencies
├── speech_server_finetune.py       # Main STT server application
├── test_stt.sh                     # API testing script
├── processor_files/                # Whisper processor files
│   ├── tokenizer_config.json
│   ├── vocab.json
│   └── ...
└── whisper-finetuned-final/        # Fine-tuned Whisper model
    ├── model.safetensors
    ├── config.json
    └── ...
```

## Setup Instructions

### 1. Clone This Repository

```bash
# Clone the STT Production repository
git clone https://github.com/MirxaWaqarBaig/SST-Prod.git
cd SST-Prod
```

### 2. Build External Dependencies

You'll need to build the broker and gateway images from their respective repositories:

```bash
# Clone the broker repository and build the image
git clone <broker-repo-url>
cd <broker-repo>
docker build -t ss-broker .

# Clone the gateway repository and build the image  
git clone <gateway-repo-url>
cd <gateway-repo>
docker build -t ss-gateway .
```

### 3. Download Model Files

Download the required model files from Google Drive:

**Download Link**: [https://drive.google.com/file/d/1XQezBUMg-KBpmi8dlT3Dx59OhIU6OBfD/view?usp=sharing](https://drive.google.com/file/d/1XQezBUMg-KBpmi8dlT3Dx59OhIU6OBfD/view?usp=sharing)

After downloading, extract the files to the SST-Prod directory. You should have:
- `whisper-finetuned-final/` folder with the fine-tuned model files
- `processor_files/` folder with tokenizer and processor files

### 4. Build STT Service Image

From the SST-Prod directory:

```bash
# Build the STT service Docker image
docker build -f Dockerfile.STT -t ss-whisper .
```

### 5. Verify Model Files

Ensure the following directories contain the required files:

- `whisper-finetuned-final/`: Should contain the fine-tuned model files
- `processor_files/`: Should contain tokenizer and processor files

### 6. Run the Services

Start all services using Docker Compose:

```bash
# Start all services
docker-compose -f docker-compose_STT.yml up -d

# View logs
docker-compose -f docker-compose_STT.yml logs -f
```

### 7. Verify Deployment

Check that all services are running:

```bash
# Check service status
docker-compose -f docker-compose_STT.yml ps

# Expected output should show:
# - stt-broker (running)
# - whisper-stt (running) 
# - stt-gateway (running)
```

## API Usage

### Endpoints

#### Local Development
- **URL**: `http://localhost:8000/api/wav-to-text`
- **Method**: POST
- **Content-Type**: multipart/form-data

#### Production
- **URL**: `http://chatbot.sharestyleai.com:8000/api/wav-to-text`
- **Method**: POST
- **Content-Type**: multipart/form-data

### Request Format

```bash
# Local testing
curl -X POST http://localhost:8000/api/wav-to-text \
  -F "audio_file=@/path/to/your/audio.wav"

# Production testing
curl -X POST http://chatbot.sharestyleai.com:8000/api/wav-to-text \
  -F "audio_file=@/path/to/your/audio.wav"
```

### Example Usage

```bash
# Test with the provided script (uses production endpoint)
chmod +x test_stt.sh
./test_stt.sh
```

## Configuration

### Environment Variables

The STT service supports the following environment variables:

- `DEVICE`: Device to use for inference (`cuda` or `cpu`, default: `cuda`)
- `MODEL_PATH`: Path to the fine-tuned model directory
- `PROCESSOR_PATH`: Path to the processor files directory
- `ZMQ_BACKEND_ROUTER_URL`: ZMQ broker backend URL

### GPU Configuration

The system is configured to use NVIDIA GPUs by default. To run on CPU only:

```bash
# Edit docker-compose_STT.yml and remove the deploy section from stt-server
# Or set DEVICE=cpu in the environment variables
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size or use CPU inference
   - Check GPU memory usage: `nvidia-smi`

2. **Model Loading Errors**
   - Verify model files are present in `whisper-finetuned-final/`
   - Check file permissions and paths

3. **ZMQ Connection Issues**
   - Ensure broker service is running first
   - Check network connectivity between services

4. **Audio Processing Errors**
   - Verify audio file format (WAV recommended)
   - Check audio file is not corrupted

### Logs and Debugging

```bash
# View all service logs
docker-compose -f docker-compose_STT.yml logs

# View specific service logs
docker-compose -f docker-compose_STT.yml logs stt-server
docker-compose -f docker-compose_STT.yml logs broker
docker-compose -f docker-compose_STT.yml logs gateway

# Follow logs in real-time
docker-compose -f docker-compose_STT.yml logs -f stt-server
```

## Performance Optimization

### GPU Optimization
- Ensure CUDA drivers are properly installed
- Monitor GPU memory usage during inference
- Consider using mixed precision if supported

### Memory Optimization
- The model requires significant RAM (8GB+ recommended)
- Monitor memory usage: `docker stats`

## Dependencies

### Python Packages
- torch==2.6.0
- transformers==4.51.3
- librosa==0.10.0
- numpy==1.26.4
- pyzmq==26.2.1
- opencc==1.1.9
- soundfile==0.13.1
- audioread==3.0.1
- safetensors==0.5.3
- accelerate==1.5.2
- tqdm==4.67.1

### System Requirements
- Python 3.10.12
- FFmpeg (for audio processing)
- CUDA (for GPU acceleration)

## Model Information

This system uses a fine-tuned Whisper model with the following characteristics:

- **Architecture**: WhisperForConditionalGeneration
- **Model Size**: ~1.5GB (model.safetensors)
- **Languages**: Optimized for Chinese (Traditional to Simplified conversion)
- **Input**: 16kHz audio
- **Output**: Transcribed text

## Production Deployment

For production deployment:

1. **Security**: Configure proper network security and access controls
2. **Monitoring**: Set up logging and monitoring for all services
3. **Scaling**: Consider horizontal scaling for high-throughput scenarios
4. **Backup**: Regular backup of model files and configurations
5. **Updates**: Plan for model updates and service restarts

## Support

For issues and questions:

1. Check the logs for error messages
2. Verify all dependencies are correctly installed
3. Ensure model files are present and accessible
4. Test with the provided test script

## License



## Contributing


