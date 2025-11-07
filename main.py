from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import pytesseract
import io

app = FastAPI(title="Tesseract OCR with Bounding Boxes")

@app.post("/ocr")
async def ocr_with_boxes(file: UploadFile = File(...)):
    try:
        # Đọc ảnh
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Dùng pytesseract để lấy data dạng DataFrame (có bounding box)
        data = pytesseract.image_to_data(
            image,
            lang='vie',
            config='--oem 1 --psm 3',
            output_type=pytesseract.Output.DATAFRAME
        )

        # Lọc và xử lý: chỉ lấy từ (level=5), conf > 0, text không rỗng
        results = []
        for _, row in data.iterrows():
            if int(row['level']) == 5 and float(row['conf']) > 0:
                text = str(row['text']).strip()
                if text:
                    x = row['left']
                    y = row['top']
                    w = row['width']
                    h = row['height']
                    box = [x, y, x + w, y + h]  # [x1, y1, x2, y2]
                    results.append({
                        "text": text,
                        "box": box
                    })

        return JSONResponse({"success": True, "results": results})

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
