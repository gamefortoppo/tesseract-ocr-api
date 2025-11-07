from fastapi import FastAPI, File, UploadFile
import pytesseract
from PIL import Image
import io

app = FastAPI()

@app.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    img = Image.open(io.BytesIO(await file.read()))
    text = pytesseract.image_to_string(img, lang='vie', config='--oem 1 --psm 3')
    return {"text": text}
