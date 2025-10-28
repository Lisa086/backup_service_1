from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 100 * 1024 * 1024  
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".zip"}

def secure_filename(filename: str) -> str:
    return os.path.basename(filename)

@app.get("/")
def root():
    return {"message": "Сервис резервного копирования работает"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Тип файла не разрешен")
    
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Файл слишком большой")
    
    file_location = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(file_location, "wb") as f:
            f.write(content)
    except Exception:
        raise HTTPException(status_code=500, detail="Не удалось сохранить файл")
    
    return {"filename": filename, "status": "файл загружен"}

@app.get("/download/{filename}")
async def download_file(filename: str):
    filename = secure_filename(filename)
    file_location = os.path.join(UPLOAD_DIR, filename)

    if not os.path.commonprefix([os.path.realpath(file_location), os.path.realpath(UPLOAD_DIR)]) == os.path.realpath(UPLOAD_DIR):
        raise HTTPException(status_code=400, detail="Недопустимый путь файла")
    
    if os.path.exists(file_location):
        return FileResponse(file_location, media