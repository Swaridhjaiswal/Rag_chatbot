import streamlit as st
import requests
import threading
import websocket
import json
import base64
from io import BytesIO
from PIL import Image


FASTAPI_URL = "http://localhost:8000"
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
STABILITY_API_KEY = "sk-v4yRBfsglViBk2rALxHR8Ar505oJeIbHV4zPI4UgLHVAbqc0"

st.title("📚 RAG + LLM + Image Generation App")

# --- PDF Upload Section ---
st.header("📄 Upload PDF for RAG")
pdf_file = st.file_uploader("Upload your PDF", type=["pdf"])
if pdf_file is not None:
    files = {"file": (pdf_file.name, pdf_file, "application/pdf")}
    response = requests.post(f"{FASTAPI_URL}/upload-pdf/", files=files)

    if response.status_code == 200:
        res_data = response.json()
        if "message" in res_data:
            st.success(res_data["message"])
        else:
            st.warning("No message in response: " + str(res_data))
    else:
        try:
            error_msg = response.json().get("error", "Unknown error")
        except Exception:
            error_msg = response.text
        st.error(f"Upload failed: {error_msg}")


# --- RAG Query Section ---
st.header("🔍 Ask a question (RAG)")

query = st.text_input("Enter your question")
if st.button("Submit RAG Query"):
    payload = {"query": query}
    response = requests.post(f"{FASTAPI_URL}/rag", json=payload)
    st.write(f"Task ID: {response.json().get('task_id')}")

# --- Streaming RAG (WebSocket) ---
st.header("📡 Streaming RAG (WebSocket)")

stream_query = st.text_input("Enter query for streaming RAG")
if st.button("Start Streaming RAG"):
    def on_message_rag(ws, message):
        st.write(message)

    def run_websocket_rag():
        ws = websocket.WebSocketApp(f"ws://localhost:8000/ws/rag/stream",
                                    on_message=on_message_rag)
        ws.on_open = lambda ws: ws.send(json.dumps({"query": stream_query}))
        ws.run_forever()

    threading.Thread(target=run_websocket_rag).start()

# --- LLM Interface Section ---
st.header("💬 LLM Interface")

data_input = st.text_area("Enter data for LLM Interface")
if st.button("Submit to Interface"):
    payload = {"data": data_input}
    response = requests.post(f"{FASTAPI_URL}/interface", json=payload)
    st.write(response.json())

# --- Streaming Interface (WebSocket) ---
st.header("📡 Streaming Interface (WebSocket)")

stream_interface_input = st.text_input("Enter data for streaming Interface")
if st.button("Start Streaming Interface"):
    def on_message_interface(ws, message):
        st.write(message)

    def run_websocket_interface():
        ws = websocket.WebSocketApp(f"ws://localhost:8000/ws/interface/stream",
                                    on_message=on_message_interface)
        ws.on_open = lambda ws: ws.send(json.dumps({"data": stream_interface_input}))
        ws.run_forever()

    threading.Thread(target=run_websocket_interface).start()

# --- Image Generation Section (Stability AI via FastAPI) ---
st.header("🎨 Image Generation (Stability AI)")

prompt = st.text_input("Enter prompt for image generation")
if st.button("Generate Image"):
    data = {"prompt": prompt}
    
    response = requests.post(f"{FASTAPI_URL}/image_generation", json=data)
    
    if response.status_code == 200:
        try:
            data = response.json()
            image_base64 = data.get("image_base64")

            if image_base64:
                image_data = base64.b64decode(image_base64)
                image = Image.open(BytesIO(image_data))
                st.image(image, caption="Generated Image", use_container_width=True)
            else:
                st.error("Failed to generate image: Base64 not found.")
        except ValueError:
            st.error("Invalid JSON response from server.")
    else:
        st.error(f"Server responded with status code {response.status_code}: {response.text}")


# --- Streaming Image Generation (WebSocket) ---
st.header("📡 Streaming Image Generation (WebSocket)")

stream_image_prompt = st.text_input("Enter prompt for streaming Image Generation")
if st.button("Start Streaming Image Gen"):
    def on_message_image(ws, message):
        
        if message.startswith("[IMAGE-GEN-RESULT]:"):
            image_base64 = message.replace("[IMAGE-GEN-RESULT]: ", "")
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            st.image(image, caption="Generated Image (Streaming)", use_container_width=True)
        else:
            st.write(message)


    def run_websocket_image():
        ws = websocket.WebSocketApp(f"ws://localhost:8000/ws/image_generation/stream",
                                    on_message=on_message_image)
        ws.on_open = lambda ws: ws.send(json.dumps({"prompt": stream_image_prompt}))
        ws.run_forever()

    threading.Thread(target=run_websocket_image).start()
