FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY chroma_db/ ./chroma_db/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 7860
ENV LLM_PROVIDER=groq

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860"]