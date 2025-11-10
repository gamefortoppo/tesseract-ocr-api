from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
from io import BytesIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Danh sách PSM hợp lệ
VALID_PSM = {"3", "4", "6", "11", "12"}

@app.post("/ocr")
async def ocr(
    file: UploadFile = File(...),
    lang: str = Form(None),
    psm: str = Form("3")  # Mặc định là 3
):
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents))

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

        # === XỬ LÝ PSM ===
        if psm not in VALID_PSM:
            psm = "3"  # Fallback an toàn

        config = f'--oem 1 --psm {psm}'

        # === OCR ===
        data = pytesseract.image_to_data(
            image,
            lang=ocr_lang,
            config=config,
            output_type=pytesseract.Output.DICT
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
                        "lang": ocr_lang,
                        "psm": psm  # Trả về để FE biết
                    })

        return {
            "success": True,
            "detected_lang": ocr_lang,
            "used_psm": psm,
            "results": results
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
