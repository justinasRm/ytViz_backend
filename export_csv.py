import csv
import json

def export_videos_csv(video_ids):
    """
    Creates 'videos.csv' file, adds pre-defined data(update this file if the paramaters comming in change).
    """

    # video_ids
    # "{'video_id': '45PMCchaO_M', 'title': 'Asking Our Dads For Advice | Short & Simple', 'thumbnail_link': 'https://i.ytimg.com/vi/45PMCchaO_M/maxresdefault.jpg', 'channel_title': 'Short & Simple', 'view_count': '15036', 'like_count': '1473', 'comment_count': '232'}"

    with open("videos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["video_id", "title", "thumbnail_link", "channel_title", "view_count", "like_count", "comment_count"])
        for video in video_ids:
            video_id = video.get("video_id")
            title = video.get("title")
            thumbnail_link = video.get("thumbnail_link")
            channel_title = video.get("channel_title")
            view_count = video.get("view_count")
            like_count = video.get("like_count")
            comment_count = video.get("comment_count")
            writer.writerow([video_id, title, thumbnail_link, channel_title, view_count, like_count, comment_count])

def export_users_csv(user_to_videos):
    """
    Creates 'users.csv' file.
    """
    with open("users.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["user_id", "videos_json", "channel_title", "thumbnail_link", "view_count", "subscriber_count", "video_count"])

        for user_id, rest in user_to_videos.items():
            videos_json = json.dumps(rest['videos_json'])  # Converts list of dicts to JSON

            writer.writerow([user_id, videos_json, rest['channel_title'], rest['thumbnail_link'], rest['view_count'], rest['subscriber_count'], rest['video_count']])
