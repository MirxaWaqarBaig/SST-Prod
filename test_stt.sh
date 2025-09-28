#!/bin/sh

#curl -v -X POST http://localhost:8001/api/wav-to-text \
#  -F "audio_file=@/home/waqar/TTS_STT_Graph_RAG_production_V4/coXTTS.wav"

#http://localhost:8000/api/wav-to-text
#http://chatbot.sharestyleai.com:8000/api/wav-to-text
curl -v -X POST http://chatbot.sharestyleai.com:8000/api/wav-to-text \
  -F "audio_file=@/home/waqar/TTS(ITTS)_STT_system_RAG_production__V5/output_wav/np_04.wav"
