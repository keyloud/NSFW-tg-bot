from fastapi import FastAPI, Body
from pydantic import BaseModel
from uuid import uuid4
import shutil, requests, os

app = FastAPI()

class GenerateRequest(BaseModel):
    image_url: str

@app.post("/generate")
def generate(req: GenerateRequest):
    # Заглушка — просто возвращает тот же файл
    fname = f"tmp/{uuid4()}.jpg"
    os.makedirs("tmp", exist_ok=True)
    with open(fname, "wb") as f:
        f.write(requests.get(req.image_url).content)
    # Заглушка генерации — можно заменить на свой пайплайн
    result_url = f"https://placehold.co/512x512?text=NSFW+Generated"
    return {"result_url": result_url}