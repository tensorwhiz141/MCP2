# # # from fastapi import FastAPI, UploadFile, File, Form
# # # from fastapi.responses import JSONResponse
# # # from transformers import pipeline
# # # from PyPDF2 import PdfReader
# # # from pdf2image import convert_from_bytes
# # # from PIL import Image
# # # import pytesseract
# # # import uuid
# # # from datetime import datetime
# # # import os

# # # app = FastAPI()
# # # pdf_storage = {}
# # # pdf_text = {}

# # # # HuggingFace model
# # # generator = pipeline("text2text-generation", model="google/flan-t5-base")

# # # # OCR path (adjust if needed)
# # # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # # @app.post("/api/upload/pdf")
# # # async def upload_pdf(file: UploadFile = File(...)):
# # #     try:
# # #         pdf_id = f"{uuid.uuid4().hex}_{file.filename}"
# # #         content = await file.read()

# # #         # Save to temp (optional)
# # #         temp_path = f"temp_{pdf_id}"
# # #         with open(temp_path, "wb") as f:
# # #             f.write(content)

# # #         # Extract text
# # #         text = ""
# # #         try:
# # #             reader = PdfReader(temp_path)
# # #             for page in reader.pages:
# # #                 text += page.extract_text() or ""
# # #         except Exception:
# # #             pass

# # #         # If no text found, OCR fallback
# # #         if not text.strip():
# # #             images = convert_from_bytes(content)
# # #             for img in images:
# # #                 text += pytesseract.image_to_string(img)

# # #         pdf_storage[pdf_id] = {
# # #             "filename": file.filename,
# # #             "text": text,
# # #             "size": len(content),
# # #             "upload_time": datetime.now().isoformat()
# # #         }
# # #         os.remove(temp_path)

# # #         return {
# # #             "status": "success",
# # #             "file_id": pdf_id,
# # #             "filename": file.filename,
# # #             "text_length": len(text),
# # #             "upload_time": pdf_storage[pdf_id]["upload_time"]
# # #         }

# # #     except Exception as e:
# # #         return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# # # @app.post("/api/chat/pdf")
# # # async def chat_pdf(pdf_id: str = Form(...), question: str = Form(...), session_id: str = Form(None)):
# # #     try:
# # #         if pdf_id not in pdf_storage:
# # #             return {"status": "error", "message": "PDF not found"}

# # #         text = pdf_storage[pdf_id]["text"]
# # #         prompt = f"{question}\n\nContext:\n{text[:4000]}"  # limit context

# # #         result = generator(prompt, max_new_tokens=512, do_sample=True)
# # #         answer = result[0]["generated_text"]

# # #         return {
# # #             "status": "success",
# # #             "answer": answer,
# # #             "rag_enabled": True,
# # #             "llm_powered": True,
# # #             "content_chunked": len(text) > 4000,
# # #             "document_summary": answer[:150] + "...",
# # #             "pdf_id": pdf_id
# # #         }

# # #     except Exception as e:
# # #         return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
# # import streamlit as st
# # import os
# # import pandas as pd
# # import mimetypes
# # from dotenv import load_dotenv
# # from PyPDF2 import PdfReader
# # from PIL import Image, ImageFilter
# # import pytesseract
# # from transformers import pipeline
# # from pdf2image import convert_from_bytes
# # import torch
# # from integration.nipun_adapter import NipunAdapter

# # # Create your adapter instance
# # adapter = NipunAdapter()

# # # Optional: Set Tesseract path manually
# # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # # Load Hugging Face token (if needed for private models)
# # load_dotenv()
# # hf_token = os.getenv("HF_TOKEN")

# # # Streamlit config
# # st.set_page_config(page_title="AI File & Prompt Analyzer", layout="centered")
# # st.title("📄 AI File & Prompt Analyzer (HuggingFace + OCR + PDF Reader)")

# # # File uploader
# # uploaded_files = st.file_uploader("📂 Upload file(s) [PDF, Image, CSV, TXT]", accept_multiple_files=True)

# # # Optional manual text input
# # st.markdown("### ✍️ Or paste your own content below (optional):")
# # manual_text_input = st.text_area(" ", placeholder="Paste or type any content here...")

# # # Initialize combined text
# # all_text = ""

# # # Function to extract text from various file types
# # def extract_text_from_file(uploaded_file):
# #     mime_type, _ = mimetypes.guess_type(uploaded_file.name)

# #     if mime_type:
# #         if mime_type.startswith("image"):
# #             image = Image.open(uploaded_file)
# #             gray = image.convert("L").filter(ImageFilter.SHARPEN)
# #             gray = gray.point(lambda x: 0 if x < 160 else 255)
# #             try:
# #                 return pytesseract.image_to_string(gray)
# #             except Exception as e:
# #                 st.error(f"OCR failed: {e}")
# #                 return ""

# #         elif mime_type == "application/pdf":
# #             try:
# #                 text = ""
# #                 pdf_reader = PdfReader(uploaded_file)
# #                 for page in pdf_reader.pages:
# #                     content = page.extract_text()
# #                     if content:
# #                         text += content

# #                 if not text.strip():
# #                     st.warning("No text found in PDF. Trying OCR fallback...")
# #                     uploaded_file.seek(0)
# #                     pdf_images = convert_from_bytes(uploaded_file.read())
# #                     for image in pdf_images:
# #                         text += pytesseract.image_to_string(image)
# #                 return text
# #             except Exception as e:
# #                 st.error(f"PDF read failed: {e}")
# #                 return ""

# #         elif mime_type.startswith("text") or uploaded_file.name.endswith((".csv", ".txt")):
# #             try:
# #                 df = pd.read_csv(uploaded_file, encoding="utf-8")
# #                 return df.to_string()
# #             except:
# #                 try:
# #                     return uploaded_file.read().decode("utf-8", errors="ignore")
# #                 except:
# #                     st.error("Couldn't read text file.")
# #                     return ""

# #         else:
# #             try:
# #                 return uploaded_file.read().decode("utf-8", errors="ignore")
# #             except:
# #                 st.error("Could not decode file.")
# #                 return ""
# #     else:
# #         st.warning("Unknown file type.")
# #         return ""

# # # Process uploaded files
# # if uploaded_files:
# #     for file in uploaded_files:
# #         all_text += extract_text_from_file(file) + "\n"

# # # Include manually pasted text
# # if manual_text_input.strip():
# #     all_text += manual_text_input.strip()

# # # Prompt input
# # st.markdown("### 💬 Prompt to Run:")
# # prompt = st.text_area("Prompt", "Analyze the above content and provide a complete summary with key points.")

# # # Generate response
# # if st.button("▶ Run"):
# #     if not all_text.strip():
# #         st.error("Please upload a file or enter some text.")
# #     else:
# #         full_prompt = f"{prompt}\n\nContext:\n{all_text}"
# #         with st.spinner("Generating response..."):
# #             try:
# #                 # Load Hugging Face pipeline on demand
# #                 generator = pipeline("text2text-generation", model="google/flan-t5-base")
# #                 result = generator(full_prompt, max_new_tokens=1024, do_sample=True)
# #                 response = result[0]["generated_text"]

# #                 # Format output into bullets
# #                 bullets = "\n".join([f"- {line.strip()}" for line in response.split("\n") if line.strip()])
# #                 st.success("✅ Response Generated!")
# #                 st.markdown("### 🧠 Model Output:")
# #                 st.markdown(bullets)
# #                 st.download_button("📥 Download Output", bullets, file_name="summary.txt")
# #             except Exception as e:
# #                 st.error(f"Error generating output: {e}")
# import streamlit as st
# import os
# import pandas as pd
# import mimetypes
# from dotenv import load_dotenv  
# from PyPDF2 import PdfReader
# from PIL import Image, ImageFilter
# import pytesseract
# from transformers import pipeline
# from pdf2image import convert_from_bytes

# # ✅ Import your custom adapter
# from integration.nipun_adapter import NipunAdapter

# # Create adapter instance
# adapter = NipunAdapter()

# # Optional: Tesseract OCR path
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # Load Hugging Face token if needed
# load_dotenv()
# hf_token = os.getenv("HF_TOKEN")

# # Streamlit config
# st.set_page_config(page_title="AI File & Prompt Analyzer", layout="centered")
# st.title("📄 AI File & Prompt Analyzer (HuggingFace + OCR + PDF Reader)")

# # File uploader
# uploaded_files = st.file_uploader("📂 Upload file(s) [PDF, Image, CSV, TXT]", accept_multiple_files=True)

# # Optional manual text input
# st.markdown("### ✍️ Or paste your own content below (optional):")
# manual_text_input = st.text_area(" ", placeholder="Paste or type any content here...")

# # Initialize combined text
# all_text = ""

# # Function to extract text from file
# def extract_text_from_file(uploaded_file):
#     mime_type, _ = mimetypes.guess_type(uploaded_file.name)

#     if mime_type:
#         if mime_type.startswith("image"):
#             image = Image.open(uploaded_file)
#             gray = image.convert("L").filter(ImageFilter.SHARPEN)
#             gray = gray.point(lambda x: 0 if x < 160 else 255)
#             try:
#                 return pytesseract.image_to_string(gray)
#             except Exception as e:
#                 st.error(f"OCR failed: {e}")
#                 return ""

#         elif mime_type == "application/pdf":
#             try:
#                 text = ""
#                 pdf_reader = PdfReader(uploaded_file)
#                 for page in pdf_reader.pages:
#                     content = page.extract_text()
#                     if content:
#                         text += content

#                 if not text.strip():
#                     st.warning("No text found in PDF. Trying OCR fallback...")
#                     uploaded_file.seek(0)
#                     pdf_images = convert_from_bytes(uploaded_file.read())
#                     for image in pdf_images:
#                         text += pytesseract.image_to_string(image)
#                 return text
#             except Exception as e:
#                 st.error(f"PDF read failed: {e}")
#                 return ""

#         elif mime_type.startswith("text") or uploaded_file.name.endswith((".csv", ".txt")):
#             try:
#                 df = pd.read_csv(uploaded_file, encoding="utf-8")
#                 return df.to_string()
#             except:
#                 try:
#                     return uploaded_file.read().decode("utf-8", errors="ignore")
#                 except:
#                     st.error("Couldn't read text file.")
#                     return ""

#         else:
#             try:
#                 return uploaded_file.read().decode("utf-8", errors="ignore")
#             except:
#                 st.error("Could not decode file.")
#                 return ""
#     else:
#         st.warning("Unknown file type.")
#         return ""

# # Process uploaded files
# if uploaded_files:
#     for file in uploaded_files:
#         all_text += extract_text_from_file(file) + "\n"

# # Include manually pasted text
# if manual_text_input.strip():
#     all_text += manual_text_input.strip()

# # Prompt input
# st.markdown("### 💬 Prompt to Run:")
# prompt = st.text_area("Prompt", "Analyze the above content and provide a complete summary with key points.")

# # ▶ Run button
# if st.button("▶ Run"):
#     if not all_text.strip():
#         st.error("Please upload a file or enter some text.")
#     else:
#         # 👇 Combine prompt + context
#         full_prompt = f"{prompt}\n\nContext:\n{all_text}"

#         # 👇 Use your NipunAdapter first
#         adapter_result = adapter.analyze_prompt(full_prompt)

#         if "The result of" in adapter_result:
#             # ✅ Adapter handled the prompt
#             st.success("✅ Adapter Response Generated!")
#             st.markdown("### 🧮 Adapter Output:")
#             st.markdown(adapter_result)
#             st.download_button("📥 Download Output", adapter_result, file_name="adapter_output.txt")

#         else:
#             # ✅ Fallback to Hugging Face LLM
#             with st.spinner("Generating response with LLM..."):
#                 try:
#                     generator = pipeline(
#                         "text2text-generation",
#                         model="google/flan-t5-base"
#                     )
#                     result = generator(full_prompt, max_new_tokens=1024, do_sample=True)
#                     response = result[0]["generated_text"]

#                     bullets = "\n".join([f"- {line.strip()}" for line in response.split("\n") if line.strip()])
#                     st.success("✅ LLM Response Generated!")
#                     st.markdown("### 🧠 Model Output:")
#                     st.markdown(bullets)
#                     st.download_button("📥 Download Output", bullets, file_name="summary.txt")
#                 except Exception as e:
#                     st.error(f"Error generating output: {e}")

import streamlit as st
import os
import pandas as pd
import mimetypes
from dotenv import load_dotenv  
from PyPDF2 import PdfReader
from PIL import Image, ImageFilter
import pytesseract
from transformers import pipeline
from pdf2image import convert_from_bytes

# Optional: Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load Hugging Face token if needed
load_dotenv()
hf_token = os.getenv("HF_TOKEN")

# Streamlit config
st.set_page_config(page_title="AI File & Prompt Analyzer", layout="centered")
st.title("📄 AI File & Prompt Analyzer (HuggingFace + OCR + PDF Reader)")

# File uploader
uploaded_files = st.file_uploader(
    "📂 Upload file(s) [PDF, Image, CSV, TXT]",
    accept_multiple_files=True
)

# Optional manual text input
st.markdown("### ✍️ Or paste your own content below (optional):")
manual_text_input = st.text_area(" ", placeholder="Paste or type any content here...")

# Initialize combined text
all_text = ""

# Function to extract text from file
def extract_text_from_file(uploaded_file):
    mime_type, _ = mimetypes.guess_type(uploaded_file.name)

    if mime_type:
        if mime_type.startswith("image"):
            image = Image.open(uploaded_file)
            gray = image.convert("L").filter(ImageFilter.SHARPEN)
            gray = gray.point(lambda x: 0 if x < 160 else 255)
            try:
                return pytesseract.image_to_string(gray)
            except Exception as e:
                st.error(f"OCR failed: {e}")
                return ""

        elif mime_type == "application/pdf":
            try:
                text = ""
                pdf_reader = PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    content = page.extract_text()
                    if content:
                        text += content

                if not text.strip():
                    st.warning("No text found in PDF. Trying OCR fallback...")
                    uploaded_file.seek(0)
                    pdf_images = convert_from_bytes(uploaded_file.read())
                    for image in pdf_images:
                        text += pytesseract.image_to_string(image)
                return text
            except Exception as e:
                st.error(f"PDF read failed: {e}")
                return ""

        elif mime_type.startswith("text") or uploaded_file.name.endswith((".csv", ".txt")):
            try:
                df = pd.read_csv(uploaded_file, encoding="utf-8")
                return df.to_string()
            except:
                try:
                    return uploaded_file.read().decode("utf-8", errors="ignore")
                except:
                    st.error("Couldn't read text file.")
                    return ""

        else:
            try:
                return uploaded_file.read().decode("utf-8", errors="ignore")
            except:
                st.error("Could not decode file.")
                return ""
    else:
        st.warning("Unknown file type.")
        return ""

# Process uploaded files
if uploaded_files:
    for file in uploaded_files:
        all_text += extract_text_from_file(file) + "\n"

# Include manually pasted text
if manual_text_input.strip():
    all_text += manual_text_input.strip()

# Prompt input
st.markdown("### 💬 Prompt to Run:")
prompt = st.text_area(
    "Prompt",
    "Analyze the above content and provide a complete summary with key points."
)

# ▶ Run button
if st.button("▶ Run"):
    if not all_text.strip():
        st.error("Please upload a file or enter some text.")
    else:
        # 👇 Combine prompt + context
        full_prompt = f"{prompt}\n\nContext:\n{all_text}"

        # ✅ Use Hugging Face LLM only
        with st.spinner("Generating response with LLM..."):
            try:
                generator = pipeline(
                    "text2text-generation",
                    model="google/flan-t5-base"
                )
                result = generator(full_prompt, max_new_tokens=1024, do_sample=True)
                response = result[0]["generated_text"]

                bullets = "\n".join(
                    [f"- {line.strip()}" for line in response.split("\n") if line.strip()]
                )
                st.success("✅ LLM Response Generated!")
                st.markdown("### 🧠 Model Output:")
                st.markdown(bullets)
                st.download_button(
                    "📥 Download Output",
                    bullets,
                    file_name="summary.txt"
                )
            except Exception as e:
                st.error(f"Error generating output: {e}")
