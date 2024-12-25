import csv
import json

def read_data():
    """
    Reads 'videos.csv' and 'users.csv' from project
    and returns:
        video_ids (list of strings)
        user_to_videos (dict):
            {
              "user_id": [
                {"video_id": "vidA", "like_count": 10, "comment": "..."},
                ...
              ],
              ...
            }
    """
    video_data = []
    with open('videos.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # Automatically uses the first row as headers
        for row in reader:
            video_data.append(row)

    user_to_videos = []
    with open('users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'videos_json' in row:
                try:
                    row['videos_json'] = json.loads(row['videos_json'])
                except json.JSONDecodeError:
                    row['videos_json'] = []
                    print(f"Warning: Failed to decode 'videos_json' for user_id: {row.get('user_id', 'UNKNOWN')}")

            user_to_videos.append(row)
    
    return video_data, user_to_videos
