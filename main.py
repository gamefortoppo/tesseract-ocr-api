from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
from pytesseract import Output  # THÊM DÒNG NÀY
import io

app = FastAPI(title="Tesseract OCR with Bounding Boxes")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi domain (dùng tạm)
    # allow_origins=["https://your-react-app.com"],  # Dùng cái này khi deploy thật
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
            output_type=Output.DATAFRAME  # Sử dụng Output.DATAFRAME
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
