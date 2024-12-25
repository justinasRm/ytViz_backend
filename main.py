from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from read_csv import read_data
from build_json import build_graph_json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/graph")
def get_graph_data():
     # for testing data is pre generated. Maybe there will be 5 presets of data that user can choose from, or input their own videos.

    # 1. Read data from CSV files
    video_ids, user_to_videos = read_data()

    # 2. Build the JSON structure for the graph
    graph_json = build_graph_json(video_ids, user_to_videos)
    # 3. Return as JSON
    return JSONResponse(content=graph_json)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
