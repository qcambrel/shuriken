import requests
import pandas as pd
import json
import os


class AnimeList:
	def __init__(self, season: str, year: str, title=None: str):
		"""Create a list of anime by season using data scraped from Livechart.me."""
		self.season = season
		self.year = year
		self.request_url = f'https://api.myanimelist.net/v2/anime/season/{self.year}/{self.season}?limit=500'
		self.access_token = os.getenv('MAL_ACCESS_TOKEN')
		self.headers = {'Authorization': f'Bearer {self.access_token}'}
		self.response = requests.get(self.request_url, headers=self.headers)

		self.results = json.loads(self.response.text)
		self.title_data = []
		for result in self.results['data']:
			# self.title_data[result['node']['id']] = {'title': result['node']['title']}
			self.search_title(result['node']['id'])
		self.sort_media()


	def search_title(self, anime_id: int):
		"""Query MAL API with anime id to get anime data."""

		fields = '?fields=id,title,main_picture,alternative_titles,start_date,end_date,' \
				 'synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,' \
				 'updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,' \
				 'source,average_episode_duration,rating,pictures,background,related_anime,related_manga,' \
				 'recommendations,studios,statistics'
		request_url = f'https://api.myanimelist.net/v2/anime/{anime_id}{fields}'
		response = requests.get(request_url, headers=self.headers)
		self.title_data.append(json.loads(response.text))


	def sort_media(self):
		"""Sort titles into groups by media type."""
		
		self.tv_titles = [title for title in self.title_data if title['media_type'] == 'tv']
		self.movie_titles = [title for title in self.title_data if title['media_type'] == 'movie']

	
	def save(self, path=None):
		"""Write the anime list to CSV."""

		data = [[title['title'], title['id'], self.season, self.year] for title in self.tv_titles]
		df = pd.DataFrame(data=data, columns=['Title', 'ID', 'Season', 'Year'])
		path = f'data/csv/{self.year}/{self.season}-{self.year}.csv' if path is None else path
		df.to_csv(path, index=False)



if __name__ == '__main__':
	import unittest

	class TestAnimeList(unittest.TestCase):
		def setUp(self):
			self.spring_2020_list = AnimeList('spring', '2020')

		def test_spring_2020_list_success(self):
			self.assertEqual(self.spring_2020_list.response.status_code, 200)

		def test_spring_2020_list_contents(self):
			self.assertEqual(len(self.spring_2020_list.tv_titles), 116)

		def test_save_spring_2020_list(self):
			print(self.spring_2020_list.response.status_code)
			self.test_file = f'{self.spring_2020_list.season}-{self.spring_2020_list.year}-test.csv'
			self.spring_2020_list.save(path=f'tmp/{self.test_file}')
			self.temp_data = os.listdir('tmp')
			self.assertTrue(self.test_file in self.temp_data)

	unittest.main()