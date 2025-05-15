from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
import os
from io import BytesIO
from PIL import Image
import torch
from diffusers import StableDiffusionImg2ImgPipeline
import httpx
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI()

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4",
    variant="fp16",
    torch_dtype=torch.float16,
    use_auth_token=os.getenv("HF_TOKEN")
)
pipe = pipe.to("cuda")

class GenerateRequest(BaseModel):
    image_url: str

@app.post("/generate") 
async def generate(req: GenerateRequest):
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(req.image_url)
            if resp.status_code != 200:
                return JSONResponse(status_code=400, content={"error": "Не удалось загрузить изображение из Telegram."})

        try:
            image = Image.open(BytesIO(resp.content)).convert("RGB")
            image = image.resize((512, 512))
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Не удалось обработать изображение: {str(e)}"})

        prompt = "nude, erotic, sensual, beautiful, realistic, 8k"
        try:
            generated = pipe(prompt=prompt, image=image, strength=0.75, guidance_scale=7.5).images[0]
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Генерация не удалась: {str(e)}"})

        os.makedirs("output", exist_ok=True)
        out_fname = f"output/{uuid4()}.jpg"
        generated.save(out_fname)

        API_URL = os.getenv("API_URL", "http://localhost:8000")
        result_url = f"{API_URL}/output/{os.path.basename(out_fname)}"

        return {"result_url": result_url}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Unexpected server error: {str(e)}"})

