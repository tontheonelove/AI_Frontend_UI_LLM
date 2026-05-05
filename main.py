# main.py
import os
import base64
import io
import json
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import PyPDF2
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# อนุญาตให้ Frontend (localhost) เรียกใช้งาน API ได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ตั้งค่า OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    model = data.get("model")
    messages = data.get("messages", [])
    files_data = data.get("files", []) # รายชื่อไฟล์ที่ส่งมา (base64 + type)

    # --- ประมวลผลไฟล์ ---
    current_user_message = {"role": "user", "content": []}
    
    for f in files_data:
        file_type = f.get("type")
        file_content = f.get("content") # base64 string
        
        if file_type.startswith("image/"):
            # ถ้าเป็นรูปภาพ ส่งต่อเป็น Base64 ให้ Vision Model
            current_user_message["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:{file_type};base64,{file_content}"}
            })
        elif file_type == "application/pdf":
            # ถ้าเป็น PDF ให้แปลงกลับเป็นไฟล์แล้วอ่าน Text
            import base64 as b64
            pdf_bytes = b64.b64decode(file_content)
            try:
                pdf_file = io.BytesIO(pdf_bytes)
                reader = PyPDF2.PdfReader(pdf_file)
                text = "".join([page.extract_text() for page in reader.pages])
                current_user_message["content"].append({"type": "text", "text": f"📄 เนื้อหา PDF:\n{text}"})
            except Exception as e:
                print(f"PDF Error: {e}")
        elif file_type == "text/plain":
            # ถ้าเป็น Text file
            text_bytes = base64.b64decode(file_content)
            text = text_bytes.decode("utf-8")
            current_user_message["content"].append({"type": "text", "text": f"📄 เนื้อหา Text:\n{text}"})

    # เพิ่มข้อความ User ที่พิมพ์มา
    user_text = data.get("message", "")
    if user_text:
        current_user_message["content"].append({"type": "text", "text": user_text})
    
    # ถ้ามีไฟล์แต่ไม่มีข้อความ ให้เติม Prompt ช่วยหน่อย
    if not user_text and files_data:
        current_user_message["content"].append({"type": "text", "text": "วิเคราะห์ไฟล์ที่แนบมาให้หน่อย"})

    messages.append(current_user_message)

    # --- เรียก API OpenRouter (Streaming) ---
    try:
        response_stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        
        # ส่งข้อมูลกลับแบบ Streaming (Server-Sent Events)
        def event_generator():
            for chunk in response_stream:
                if chunk.choices[0].delta.content is not None:
                    yield f"data: {json.dumps({'token': chunk.choices[0].delta.content})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        return StreamingResponse(iter([f"data: Error: {str(e)}\n\n"]), media_type="text/event-stream")

# รันด้วยคำสั่ง: uvicorn main:app --reload