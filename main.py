from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
from io import BytesIO  # RÕ RÀNG, GỌN

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=["https://your-react-app.com"],  # Dùng cái này khi deploy thật
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr")
async def ocr(
    file: UploadFile = File(...),
    lang: str = Form(None)  # Nhận từ frontend
):
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents))  # Dùng BytesIO trực tiếp

        # === XÁC ĐỊNH NGÔN NGỮ ===
        if lang and lang.lower() in ["vie", "jpn"]:
            ocr_lang = lang.lower()
        else:
            try:
                osd = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
                script = osd.get("Script", "").lower()
                if any(x in script for x in ["han", "hiragana", "katakana", "japanese"]):
                    ocr_lang = "jpn"
                else:
                    ocr_lang = "vie"
            except:
                ocr_lang = "vie"

        # === OCR ===
        data = pytesseract.image_to_data(
            image,
            lang=ocr_lang,
            config='--oem 1 --psm 3',
            output_type=pytesseract.Output.DICT  # Không cần import Output
        )

        results = []
        for i in range(len(data["text"])):
            if int(data["level"][i]) == 5 and float(data["conf"][i]) > 30:
                text = data["text"][i].strip()
                if text:
                    box = [
                        data["left"][i],
                        data["top"][i],
                        data["left"][i] + data["width"][i],
                        data["top"][i] + data["height"][i]
                    ]
                    results.append({
                        "text": text,
                        "box": box,
                        "lang": ocr_lang
                    })

        return {
            "success": True,
            "detected_lang": ocr_lang,
            "results": results
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
