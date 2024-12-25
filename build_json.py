
def build_graph_json(videos, user_to_videos) -> dict:
    """
    Builds a dict with 'nodes' and 'edges' for a graph:
      - `videos` is a list of dicts (one dict per video).
      - `user_to_videos` is a list of dicts (one dict per user),
        each with `user_id` plus other fields, including a `videos_json` list.

    Output:
      {
        "nodes": [...],
        "edges": [...]
      }
    """
    nodes = []
    edges = []

    # 1. Add video nodes
    # Example object in `videos`:
    # {
    #   "video_id": "45PMCchaO_M",
    #   "title": "Asking Our Dads For Advice...",
    #   "thumbnail_link": "https://...",
    #   ...
    # }
    for video_data in videos:
        nodes.append({
            "id": video_data["video_id"],
            "type": "video",
            "title": video_data.get("title"),
            "thumbnail_link": video_data.get("thumbnail_link"),
            "channel_title": video_data.get("channel_title"),
            "view_count": video_data.get("view_count"),
            "like_count": video_data.get("like_count"),
            "comment_count": video_data.get("comment_count"),
        })

    # 2. Add user nodes & build edges from each user's videos_json
    # Example object in `user_to_videos`:
    # {
    #   "user_id": "UCO8kpQxz8pDGEGktVU0doyA",
    #   "videos_json": [ ... ],
    #   "channel_title": "Stunpid.",
    #   "thumbnail_link": "https://...",
    #   "view_count": "0",
    #   "subscriber_count": "2",
    #   "video_count": "0"
    # }
    for user_data in user_to_videos:
        user_id = user_data["user_id"]
        videos_json = user_data.get("videos_json", [])

        nodes.append({
            "id": user_id,
            "type": "user",
            "channel_title": user_data.get("channel_title"),
            "thumbnail_link": user_data.get("thumbnail_link"),
            "view_count": user_data.get("view_count"),
            "subscriber_count": user_data.get("subscriber_count"),
            "video_count": user_data.get("video_count"),
        })

        for vid_info in videos_json:
            edges.append({
                "source": user_id,
                "target": vid_info["video_id"],
                "like_count": vid_info.get("like_count", 0),
                "comment": vid_info.get("comment", "")
            })

    return {"nodes": nodes, "edges": edges}
