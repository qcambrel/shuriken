from googleapiclient.discovery import build


class YouTubeQuery:
	def __init__(self, api_key: str):
		self.youtube_client = build('youtube', 'v3', developerKey=api_key)

	def search_title(self, title: str) -> dict:
		"""Retrieve view count of most viewed video from YouTube."""
		video = self.youtube_client.search().list(part='id', q=f'{title}', maxResults=1, order='viewCount').execute()
		video_id = video['items'][0]['id']['videoId']
		metadata = youtube.videos().list(part='statistics', id=video_id).execute()
		view_count = metadata['items'][0]['statistics']['viewCount']
		return {'Title':title, 'Views':view_count}
	