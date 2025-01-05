from config import get_youtube_client
from fastapi.responses import JSONResponse
from fetching import fetch_comments_for_videos, get_youtube_client, build_inverted_index, add_user_metadata
from build_json import build_graph_json
from pprint import pprint

def make_video_graphs(links: str, commentCount: int):
    error = ''
    # example 'links':  https://www.youtube.com/watch?v=4H4sScCB1cY,https://www.youtube.com/watch?v=8tDOeQqnrYQ
    idsList = []
    print('commentCount: ', commentCount)
    for link in links.split(','):
        if '=' not in link or 'https://www.youtube.com/watch?v=' not in link or len(link.split('=')[1]) != 11:
            error = "Couldn't find video id in the link: " + link + ".\nMake sure the link is in the format: https://www.youtube.com/watch?v={11_CHARACTER_VIDEO_ID}"
            return JSONResponse(content={"error": error}, status_code=400)
        id = link.split('=')[1]
        idsList.append(id)

    # idsList = ['4H4sScCB1cY', '8tDOeQqnrYQ', ...]

    videoMetadata = check_video_ids(idsList)
    print(videoMetadata)
    print('videoMetadata')
    if 'error' in videoMetadata:
        return JSONResponse(content=videoMetadata, status_code=400)
    
    # now getting comments for each video

    print("Starting comment fetch...")
    video_to_commenters = fetch_comments_for_videos(idsList, commentCount)
    print("Fetch complete!\n")

    print("Building inverted index...")
    user_to_videos = build_inverted_index(video_to_commenters)
    print(f"Found {len(user_to_videos)} unique users.\n")

    # video_ids_full = add_video_metadata(video_ids)
    userMetadata = add_user_metadata(user_to_videos)

    # return JSONResponse(content={"videos": videoMetadata["videos"], "users": userMetadata}, status_code=200)
    #  userMetadata is a hashMap. Dont need the keys. Remove keys, return just values(turn to a set)
    #  videoMetadata is a list of video objects.
    userMetadata = list(userMetadata.values())
    graph_json = build_graph_json(videoMetadata["videos"], userMetadata)
    return JSONResponse(content=graph_json)



def check_video_ids(video_ids: list[str]) -> dict:
    """
    Check if the video_ids are valid video ids.
    """
    youtube = get_youtube_client()
    video_metadata: list[dict] = []
    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=','.join(video_ids)
        ).execute()
        
        items = response.get("items", [])

        correct_ids = []
        for i in items:
            correct_ids.append(i['id'])

        incorrect_ids = list(set(video_ids) - set(correct_ids))

        if len(items) != len(video_ids):
            return {"error": "Some of the video IDs are invalid.\n Couldn't get information about " + ','.join(incorrect_ids) + " video/s."}
        
        if not items:
            return {"error": "Couldn't get information about any videos."}
        
        for video in items:
            snippet = video.get("snippet", {})
            stats = video.get("statistics", {})
            thumbnails = snippet.get("thumbnails", {})
            thumbnail = thumbnails.get("maxres", thumbnails.get("default", {}))

            video_metadata.append({
                "video_id": video.get("id", None),
                "title": snippet.get("title", None),
                "thumbnail_link": thumbnail.get("url", None),
                "channel_title": snippet.get("channelTitle", None),
                "view_count": stats.get("viewCount", None),
                "like_count": stats.get("likeCount", None),
                "comment_count": stats.get("commentCount", None)
            })


        return {"videos": video_metadata}
    except Exception as e:
        print(f"Error validating video IDs: {e}")
        # invalid_ids.extend(video_ids)  # Mark all as invalid if an error occurs

    # return {"valid": valid_ids, "invalid": invalid_ids}
