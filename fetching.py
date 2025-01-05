from config import get_youtube_client
from export_csv import export_videos_csv, export_users_csv
from typing import List, Dict, Optional, TypedDict, Any
from itertools import islice

# Random vids
video_ids: List[str] = ["45PMCchaO_M", "6PQQUsJuFBU", "dHHB7k5aWRk", "1mk0By1xf8M", "spUTRgDHq_o"]

# NeetCode videos
# video_ids: List[str] = ["VHZDxOmRthE", "QHXET1G9Y5U", "IcxM8G1odzg", "el0YrkT-NPA"]

# Yung Lean videos
# video_ids: List[str] = ["X1A0maG9k7M", "iQPq68mP-t8", "vYdmrLYftlI", "tMgkt9jdjTU", "KOFw2UPLdPk"]

# mrbeast videos
# video_ids: List[str] = ["gs8qfL9PNac", "0BjlBnfHcHM", "Xj0Jtjg3lHQ", "bn0Kh9c4Zv4", "snX5YyflrGw"]

def fetch_comments_for_videos(video_ids: list[str], commentCount: int = 500) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch up to {commentCount} comments per video_id.
    Returns a dict of:
      {
        "VIDEO_ID": [
          {"channel_id": "UCxyz", "like_count": 123, "comment": "blabla"},
          {"channel_id": "UCabc", "like_count": 45, "comment": "blabla"},
          ...
        ],
        ...
      }
    """
    youtube = get_youtube_client()
    video_to_commenters = {}

    for vid in video_ids:
        all_commenters = []
        page_token = None

        try:
            for _ in range(commentCount // 100):
                response = youtube.commentThreads().list(
                    part="snippet",
                    videoId=vid,
                    maxResults=100,
                    pageToken=page_token
                ).execute()

                items = response.get("items", [])
                if not items:
                    print(f"No comments found for video: {vid}")
                    break

                for item in items:
                    try:
                        snippet = item["snippet"]["topLevelComment"]["snippet"]
                        ch_id = snippet["authorChannelId"]["value"]
                        like_count = snippet["likeCount"]
                        comment = snippet["textOriginal"]

                        all_commenters.append({
                            "channel_id": ch_id,
                            "like_count": like_count,
                            "comment": comment
                        })

                    except KeyError as e:
                        raise KeyError(
                            f"Missing key {e} in comment data for video {vid}. "
                            "This indicates a malformed API response."
                        )

                page_token = response.get("nextPageToken")
                if not page_token:
                    break

        except KeyError as e:
            print(f"Key error encountered: {e}")
            raise  # Rethrow to signal a critical failure in comment data parsing

        except Exception as e:
            print(f"Unexpected error fetching comments for video {vid}: {e}")
            raise  # Rethrow unexpected errors

        video_to_commenters[vid] = all_commenters

    return video_to_commenters

def build_inverted_index(video_to_commenters):
    """
    Convert video_to_commenters into a dict of:
      user_to_videos[user_id] = [
        {"video_id": ..., "like_count": ...},
        ...
      ]
    """
    user_to_videos = {}

    for vid, commenters in video_to_commenters.items():
        for commenter_data in commenters:
            user_id = commenter_data["channel_id"]
            like_count = commenter_data["like_count"]
            comment = commenter_data["comment"]

            if user_id not in user_to_videos:
                user_to_videos[user_id] = []

            user_to_videos[user_id].append({
                "video_id": vid,
                "like_count": like_count,
                "comment": comment
            })
    return user_to_videos

def add_video_metadata(video_ids):
    """
    Add video metadata to the video_ids list with error handling for missing keys or values.
    """
    youtube = get_youtube_client()
    video_ids_full = []

    for vid in video_ids:
        try:
            response = youtube.videos().list(
                part="snippet,statistics",
                id=vid
            ).execute()
            
            items = response.get("items", [])
            if not items:
                raise ValueError("No items found in response")
            
            snippet = items[0].get("snippet", {})
            stats = items[0].get("statistics", {})
            thumbnails = snippet.get("thumbnails", {})
            thumbnail = thumbnails.get("maxres", thumbnails.get("default", {}))

            video_ids_full.append({
                "video_id": vid,
                "title": snippet.get("title", None),
                "thumbnail_link": thumbnail.get("url", None),
                "channel_title": snippet.get("channelTitle", None),
                "view_count": stats.get("viewCount", None),
                "like_count": stats.get("likeCount", None),
                "comment_count": stats.get("commentCount", None)
            })
        
        except (IndexError, KeyError, ValueError) as e:
            print(f"Error processing video {vid}: {e}")
            video_ids_full.append({
                "video_id": vid,
                "title": None,
                "thumbnail_link": None,
                "channel_title": None,
                "view_count": None,
                "like_count": None,
                "comment_count": None,
                "error_proccessing": str(e)
            })
        
        except Exception as e:
            print(f"Unexpected error with video {vid}: {e}")
            video_ids_full.append({
                "video_id": vid,
                "title": None,
                "thumbnail_link": None,
                "channel_title": None,
                "view_count": None,
                "like_count": None,
                "comment_count": None,
                "error_proccessing": str(e)

            })

    return video_ids_full

def batch(iterable, size):
    """Yield successive n-sized chunks from an iterable."""
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk


def add_user_metadata(user_to_videos):
    """
    Add user metadata to the user_to_videos dict in batches (100 users per batch).
    """
    youtube = get_youtube_client()
    user_to_videos_full = {}

    user_ids = list(user_to_videos.keys())
    
    for batch_user_ids in batch(user_ids, 50):
        try:
            response = youtube.channels().list(
                part="snippet,statistics",
                id=",".join(batch_user_ids)
            ).execute()
            
            items = response.get("items", [])
            user_metadata_map = {item["id"]: item for item in items}
            
            for user_id in batch_user_ids:
                metadata = user_metadata_map.get(user_id, {})
                snippet = metadata.get("snippet", {})
                
                if metadata:
                    user_to_videos_full[user_id] = {
                        "user_id": user_id,
                        "channel_title": snippet.get("title", None),
                        "thumbnail_link": snippet.get("thumbnails", {}).get("default", {}).get("url", None),
                        "videos_json": user_to_videos[user_id],
                        "view_count": metadata.get("statistics", None).get("viewCount", None),
                        "subscriber_count": metadata.get("statistics", None).get("subscriberCount", None),
                        "video_count": metadata.get("statistics", None).get("videoCount", None)
                    }
                else:
                    print(f"Metadata not found for user_id: {user_id}")
                    user_to_videos_full[user_id] = {
                        "user_id": user_id,
                        "channel_title": None,
                        "videos_json": user_to_videos[user_id],
                        "error_processing": "Metadata not found"
                    }

        except (IndexError, KeyError, ValueError) as e:
            print(f"Error processing batch: {e}")
            for user_id in batch_user_ids:
                user_to_videos_full[user_id] = {
                    "channel_id": user_id,
                    "channel_title": None,
                    "video_ids": user_to_videos[user_id],
                    "error_processing": str(e)
                }
        
        except Exception as e:
            print(f"Unexpected error with batch: {e}")
            for user_id in batch_user_ids:
                user_to_videos_full[user_id] = {
                    "channel_id": user_id,
                    "channel_title": None,
                    "video_ids": user_to_videos[user_id],
                    "error_processing": str(e)
                }

    return user_to_videos_full

if __name__ == "__main__":

    print("Starting comment fetch...")
    video_to_commenters = fetch_comments_for_videos(video_ids)
    print("Fetch complete!\n")

    print("Building inverted index...")
    user_to_videos = build_inverted_index(video_to_commenters)
    print(f"Found {len(user_to_videos)} unique users.\n")

    video_ids_full = add_video_metadata(video_ids)
    user_to_videos_full = add_user_metadata(user_to_videos)

    print("Exporting to CSV...")
    export_videos_csv(video_ids_full, 4)
    export_users_csv(user_to_videos_full, 4)
    print("Done! Check 'videos.csv' and 'users.csv'.")
