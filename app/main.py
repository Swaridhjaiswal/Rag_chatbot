from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from celery_service1.tasks_general import rag_task, interface_task, image_generation_task
from celery_service2.tasks_stream import stream_rag_task, stream_interface_task, stream_image_gen_task
import asyncio
from fastapi import UploadFile, File, APIRouter
from fastapi.responses import JSONResponse
import shutil
import base64 
import openai
import requests
import os
from celery_service1.utils.pdf_utils import extract_text_from_pdf, split_text
from celery_service1.utils.vectorstore import add_document_chunks

STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
STABILITY_API_KEY = "sk-v4yRBfsglViBk2rALxHR8Ar505oJeIbHV4zPI4UgLHVAbqc0"
app = FastAPI()
router = APIRouter()

class RAGRequest(BaseModel):
    query: str
    
class InterfaceRequest(BaseModel):
    data: str
    
class ImageRequest(BaseModel):
    prompt: str

#--- POST EndPoints (Celery Worker 1 - General) ---
@app.post("/rag")
def rag(request: RAGRequest):
    task = rag_task.delay(request.query)
    return {"task_id": task.id}

@app.post("/interface")
def interface(request: InterfaceRequest):    
    task = interface_task.delay(request.data)
    return {"task_id": task.id}

@app.post("/image_generation")
def image_gen(request: ImageRequest):
    print("Received prompt:", request.prompt)  # DEBUG

    if not request.prompt.strip():
        return JSONResponse(content={"error": "Prompt is empty"}, status_code=400)
    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",  # Expecting base64-encoded image in JSON response
    }
    data = {
        "text_prompts": [
            {"text": request.prompt}
        ],
        "cfg_scale": 7,
        "clip_guidance_preset": "FAST_BLUE",
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30
    }
    
    try:
        response = requests.post(STABILITY_API_URL, json=data, headers=headers)
        response.raise_for_status()  # Check for request success
        
        image_data = response.json()
        # Extract the base64-encoded image from the response
        image_base64 = image_data.get("artifacts")[0].get("base64")
        
        return JSONResponse(content={"image_base64": image_base64}, status_code=200)
        
    except requests.exceptions.RequestException as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    #task= image_generation_task.delay(request.prompt)
    #return {"task_id": task.id}

#--- WebSocket EndPoints (Celery Worker 2- Streaming) ---
@app.websocket("/ws/rag/stream")
async def stream_rag(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        query = data.get("query")
        use_local = data.get("use_local_llm", False)
        
        response= stream_rag_task.delay(query, use_local)
        while not response.ready():
            await websocket.send_text(f"[RAG] Processing..")
            await asyncio.sleep(1)
            
        result = response.get()
        await websocket.send_text(f"[RAG-RESULT]: {result}")
        await websocket.close()
        
    except WebSocketDisconnect():
        print("RAG WebSocket Disconnected.")
        
@app.websocket("/ws/interface/stream")
async def stream_interface(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        input_data = data.get("data")
        use_local=data.get("use_local_llm", True)
        
        response = stream_interface_task.delay(input_data, use_local)
        while not response.ready():
            await websocket.send_text("[Interface] Processing..")
            await asyncio.sleep(1)
        
        result = response.get()
        await websocket.send_text(f"[INTERFACE-RESULT]: {result}")
        await websocket.close()
        
    except WebSocketDisconnect:
        print("Interface Websocket Disconnected.")

@app.websocket("/ws/image_generation/stream") 
async def stream_image_gen(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        prompt = data.get("prompt")
        print(f"[WebSocket] Prompt received: {prompt}")
        await websocket.send_text(f"[Image] Generating image for: {prompt}")

        payload = {
            "text_prompts": [
                {"text": prompt}
            ],
            "cfg_scale": 7,
            "clip_guidance_preset": "FAST_BLUE",
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }

        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        print("[WebSocket] Sending request to Stability API...")
        response = requests.post(STABILITY_API_URL, json=payload, headers=headers)
        print(f"[WebSocket] Response status: {response.status_code}")
        response.raise_for_status()

        image_base64 = response.json().get("artifacts")[0].get("base64")
        print("[WebSocket] Image base64 received. Sending to frontend...")
        await websocket.send_text(f"[IMAGE-GEN-RESULT]: {image_base64}")
        await websocket.close()

    except WebSocketDisconnect:
        print("Image Generation WebSocket disconnected.")
    except Exception as e:
        error_msg = f"[WebSocket] Error occurred: {str(e)}"
        print(error_msg)
        await websocket.send_text(error_msg)
        await websocket.close()


@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    file_location = f"uploads/{file.filename}"

    try:
        # Save file
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract and chunk
        text = extract_text_from_pdf(file_location)
        chunks = split_text(text)

        # Store chunks silently
        add_document_chunks(file.filename, chunks)

        return {"message": "PDF processed and stored successfully."}

    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(file_location):
            os.remove(file_location)
app.include_router(router)           
        
        

        
            