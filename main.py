from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from read_csv import read_data
from build_json import build_graph_json
from make_video_graphs import make_video_graphs
from firestore_utils import getAPIQuota

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/default-graphs")
def get_default_graphs(graph_num: int = Query(..., description="# of graph to retrieve")):
    '''
    Returns the default data that's generated to see the functionality.
    '''
    video_ids, user_to_videos = read_data(graph_num)
    graph_json = build_graph_json(video_ids, user_to_videos)
    return JSONResponse(content=graph_json)

@app.get("/make-video-graphs")
def func(links: str = Query(..., description="youtube video links"), commentCount: int = Query(..., description="Number of comments to fetch for each video")):
    try:
        return make_video_graphs(links, commentCount)
    except Exception as e:
        if 'raised_error_text:' in str(e):
            return JSONResponse(content={"error": str(e).split('raised_error_text:')[1]}, status_code=400)
        return JSONResponse(content={"error": "An error occurred. Please try again."}, status_code=400)

@app.get("/get-api-quota")
def get_api_quota():
    '''
    Get data from Firestore.
    '''
    rtrn = getAPIQuota()
    return JSONResponse(content={"quota": rtrn})

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

