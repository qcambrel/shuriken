from googleapiclient.discovery import build
# from bs4 import BeautifulSoup
import requests

from typing import Union

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

import webbrowser
import secrets

import sqlite3
import random
import json
import time
import os


#  Depreciated due to Cloudflare 2.0
#
# def create_anime_list(season: str, year: str) -> list:
# 	"""Create a list of anime by season using data from Livechart.me."""
	
# 	request_url = f'https://www.livechart.me/{season}-{year}/tv'
# 	user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
# 	user_agent += 'AppleWebKit/537.36 (KHTML, like Gecko) '
# 	user_agent += 'Chrome/90.0.4430.93 Safari/537.36'

# 	headers = {'user-agent':user_agent}
# 	response = requests.get(request_url, headers=headers)
	
# 	soup = BeautifulSoup(response.text, 'html.parser')
# 	titles = []
# 	cards = soup.body.main.find_all('article')
# 	for card in cards:
# 		titles.append(card.div.h3.a.contents[0])
	
# 	return titles


# temporary substitute
def create_anime_list(season: str, year: str) -> list:
	"""Create a list of anime by season using data using date from MyAnimeList."""
	request_url = f'https://api.myanimelist.net/v2/anime/season/{year}/{season}?limit=500'
	access_token = os.getenv('MAL_ACCESS_TOKEN')
	headers = {'Authorization': f'Bearer {access_token}'}
	response = requests.get(request_url, headers=headers)

	results = json.loads(response.text)
	return [result['node']['title'] for result in results['data']]


def select_title(anime_list: list) -> str:
	"""Select a random title from the anime list."""
	
	return random.choice(anime_list)


def trim_anime_list(anime_list: list, random_title: str) -> list:
	"""Remove the selected title from the anime list."""
	
	return [title for title in anime_list if title != random_title]


def get_youtube_data(api_key: str, title: str) -> dict:
	"""Retrieve view count of most viewed video from YouTube."""

	youtube = build('youtube', 'v3', developerKey=api_key)
	youtube_data = []
	video = youtube.search().list(part='id', q=f'{title}', maxResults=1, order='viewCount', type='video').execute()
	print(video)
	video_id = video['items'][0]['id']['videoId']
	metadata = youtube.videos().list(part='statistics', id=video_id).execute()
	view_count = metadata['items'][0]['statistics']['viewCount']
	
	return {'Title':title, 'Views':view_count}


def get_myanimelist_data(title: str) -> dict:
	"""Gather score, rank, and other metadata from MyAnimeList."""
	
	base_url = 'https://api.myanimelist.net/v2/anime'
	access_token = os.getenv('MAL_ACCESS_TOKEN')
	headers = {'Authorization': f'Bearer {access_token}'}
	list_request_url = f'{base_url}?q={title}&limit=1'
	list_response = requests.get(list_request_url, headers=headers)	
	
	anime_search = json.loads(list_response.text)
	if anime_search['data']:
		anime_id = anime_search['data'][0]['node']['id']
		fields = '?fields=title,mean,rank,popularity,num_list_users,num_scoring_users,'
		fields += 'statistics,genres,num_episodes,start_season,broadcast,source,rating'
		details_request_url = f'{base_url}/{anime_id}{fields}'
		details_response = requests.get(details_request_url, headers=headers)
		details = json.loads(details_response.text)
		
		status = details['statistics']['status']
		start_season = details['start_season']
		broadcast = details['broadcast'] if 'broadcast' in details else ''
		genres = details['genres']
		nested_fields = ['statistics', 'genres', 'start_season', 'broadcast']
		
		myanimelist_data = {field:details[field] for field in details.keys() if field not in nested_fields}
		myanimelist_data['genres'] = [genre['name'] for genre in genres]
		
		for field in status:
			myanimelist_data[field] = status[field]
		
		for field in start_season:
			myanimelist_data[field] = start_season[field]
		
		for field in broadcast:
			myanimelist_data[field] = broadcast[field]

		return myanimelist_data


def setup_db(db_name: str):
	"""Set up the SQLite3 database."""
	
	sqlite3.register_adapter(list, list_to_json)
	sqlite3.register_converter('JSON', json_to_list)

	path = os.path.dirname(os.path.abspath(__file__))
	conn = sqlite3.connect(path + '/' + db_name, detect_types=sqlite3.PARSE_DECLTYPES)
	cur = conn.cursor()
	
	return cur, conn


def create_youtube_table(youtube_data: dict, cur, conn):
	"""Create the table where the YouTube data will be stored."""
	
	cur.execute("""CREATE TABLE IF NOT EXISTS YouTube (
		id INTEGER PRIMARY KEY, title TEXT, views INTEGER)""")
	
	cur.execute("SELECT MAX(id) FROM YouTube")
	max_id = cur.fetchall()[0][0]
	id = max_id + 1 if max_id else 1
	title = youtube_data['Title']
	views = int(youtube_data['Views'])
	
	cur.execute("""INSERT INTO YouTube (id, title, views) 
		VALUES (?, ?, ?)""", (id, title, views))
	
	conn.commit()


def create_myanimelist_table(myanimelist_data: dict, cur, conn):
	"""Create the table where the MyAnimeList data will be stored."""
	
	cur.execute("""CREATE TABLE IF NOT EXISTS MyAnimeList (
		id INTEGER PRIMARY KEY, title TEXT, score REAL, rank INTEGER, 
		popularity INTEGER, audience INTEGER, voters INTEGER, 
		watching INTEGER, completed INTEGER, on_hold INTEGER, 
		dropped INTEGER, plan_to_watch INTEGER, season TEXT, year INTEGER, 
		genres JSON, episodes INTEGER, air_day TEXT, air_time TEXT)""")
	
	cur.execute("SELECT MAX(id) FROM MyAnimeList")
	max_id = cur.fetchall()[0][0]
	id = max_id + 1 if max_id else 1
	
	title = myanimelist_data['title']
	score = float(myanimelist_data['mean']) if 'mean' in myanimelist_data else 0.0
	rank = int(myanimelist_data['rank'])
	popularity = int(myanimelist_data['popularity'])
	audience = int(myanimelist_data['num_list_users'])
	voters = int(myanimelist_data['num_scoring_users'])
	watching = int(myanimelist_data['watching'])
	completed = int(myanimelist_data['completed'])
	on_hold = int(myanimelist_data['on_hold'])
	dropped = int(myanimelist_data['dropped'])
	plan_to_watch = myanimelist_data['plan_to_watch']
	season = myanimelist_data['season']
	year = myanimelist_data['year']
	genres = myanimelist_data['genres']
	episodes = myanimelist_data['num_episodes']
	air_day = myanimelist_data['day_of_the_week'] if 'day_of_the_week' in myanimelist_data else ''
	air_time = myanimelist_data['start_time'] if 'start_time' in myanimelist_data else ''

	cur.execute("""INSERT INTO MyAnimeList (
		id, title, score, rank, popularity, 
		audience, voters, watching, completed, 
		on_hold, dropped, plan_to_watch, season,
		year, genres, episodes, air_day, air_time) 
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
		?, ?, ?, ?, ?, ?)""",
		(id, title, score, rank, popularity, audience,
		 voters, watching, completed, on_hold, dropped, 
		 plan_to_watch, season, year, genres, episodes,
		 air_day, air_time))
	
	conn.commit()


def list_to_json(items: list):
	return json.dumps(items).encode('utf8')


def json_to_list(data) -> list:
	return json.loads(data).decode('utf8')


def table_exists(table, cur, conn) -> tuple:
	"""Check if the tables have been created."""

	cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
	return cur.fetchall()


def in_youtube_table(title: str, cur, conn) -> Union[tuple, bool]:
	"""Check if the title is already stored in the YouTube table."""

	if table_exists('YouTube', cur, conn):
		cur.execute("SELECT title FROM YouTube WHERE title = ?", (title,))
		return cur.fetchall()
	else:
		return False


def in_myanimelist_table(title: str, cur, conn) -> Union[tuple, bool]:
	"""Check if the title is already stored in the MyAnimeList table."""

	if table_exists('MyAnimeList', cur, conn):
		cur.execute("SELECT title FROM MyAnimeList WHERE title = ?", (title,))
		return cur.fetchall()
	else:
		return False


def in_both_tables(title: str, cur, conn) -> bool:
	"""Check if the title populates both tables in the database."""

	return in_myanimelist_table(title, cur, conn) and in_youtube_table(title, cur, conn)


def log_message(message: str, wait=0.5):
	st.text(message)
	time.sleep(wait)


def search(title: str, cur, conn, need_youtube=True, need_myanimelist=True):
	"""Retrieve and store title data from YouTube and MyAnimeList."""

	if need_myanimelist:
		log_message('Scanning MyAnimeList...')
		myanimelist_data = get_myanimelist_data(title)
		if myanimelist_data:
			create_myanimelist_table(myanimelist_data, cur, conn)
		else:
			log_message(f'No MyAnimeList data available for {title}.')
			log_message(f'Search canceled for this title.')
			return None
	
	if need_youtube:
		log_message('Extracting data from YouTube...')
		api_key = os.getenv('YOUTUBE_API_KEY')
		youtube_data = get_youtube_data(api_key, title)
		create_youtube_table(youtube_data, cur, conn)
	
	if need_youtube and need_myanimelist:
		log_message(f'{title} was added to the database.')
	elif need_youtube:
		log_message(f'YouTube data for {title} was added to the database.')
	elif need_myanimelist:
		log_message(f'MyAnimeList data for {title} was added to the database.')	


def search_by_title(title: str, cur, conn):
	"""Retrieve data on user provided title."""

	if in_both_tables(title, cur, conn):
		log_message(f'{title} is already in database.')
	elif in_youtube_table(title, cur, conn):
		log_message(f'YouTube data for {title} is already added.')
		log_message('Adding MyAnimeList data...')
		search(title, cur, conn, need_youtube=False)
	elif in_myanimelist_table(title, cur, conn):
		log_message(f'MyAnimeList data for {title} is already added.')
		log_message('Adding YouTube data...')
		search(title, cur, conn, need_myanimelist=False)
	else:
		search(title, cur, conn)


def search_by_season(anime_list: list, cur, conn) -> list:
	"""Retrieve data on a random title from the selected season and year."""

	log_message('Choosing a random title...')
	random_title = select_title(anime_list)
	search_by_title(random_title, cur, conn)
	
	log_message('Trimming anime list...')
	anime_list = trim_anime_list(anime_list, random_title)
	log_message('Trimming completed.')
	
	return anime_list


def get_new_code_verifier() -> str:
	"""Generate a new code verifier and code challenge."""
	
	token = secrets.token_urlsafe(100)
	return token[:128]


def open_authorization_link(code_challenge: str, client_id: str):
	"""Open the authorization link to access the auth code."""

	url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={client_id}&code_challenge={code_challenge}'
	webbrowser.open_new_tab(url)


def generate_new_token(authorization_code: str, code_verifier: str, client_id: str, client_secret: str) -> dict:
	"""Generate new token using the auth code."""
	
	url = 'https://myanimelist.net/v1/oauth2/token'
	data = {
		'client_id': client_id,
		'client_secret': client_secret,
		'code': authorization_code,
		'code_verifier': code_verifier,
		'grant_type': 'authorization_code'
	}

	response = requests.post(url, data)
	response.raise_for_status()

	token = response.json()
	response.close()

	return token


def test_token(access_token: str):
	"""Test new access token."""
	
	url = 'https://api.myanimelist.net/v2/users/@me'
	response = requests.get(url, headers={'Authorization': f'Bearer {access_token}'})
	response.raise_for_status()
	user = response.json()
	response.close()
	st.text(f'Welcome {user["name"]}!')


def analyze_data(cur, conn):
	"""Analyze the data."""

	if table_exists(cur, conn):
		st.text('Analysis is not ready yet.')
	else:
		st.text('Database is empty.')
		

# The SeasonalSearch class handles iterative search requests.
class SeasonalSearch:
	def __init__(self, season: str, year: str, cur, conn, limit: int):
		self.season = season
		self.year = year
		self.cur = cur
		self.conn = conn
		self.limit = limit if limit <= 20 and limit >= 1 else 20 if limit >= 1 else 1

	def run(self):
		log_message('Creating anime list...')
		self.anime_list = create_anime_list(self.season, self.year)
		
		try:
			df = pd.read_sql(
				"""SELECT YouTube.title FROM YouTube INNER JOIN 
				MyAnimeList ON YouTube.id=MyAnimeList.id""", 
				conn
			)
			
			title_count = len(df['title'])
		except pd.io.sql.DatabaseError:
			title_count = 0

		for _ in range(self.limit):
			self.anime_list = search_by_season(self.anime_list, self.cur, self.conn)
		
		new_df = pd.read_sql(
			"""SELECT YouTube.title FROM YouTube INNER JOIN 
			MyAnimeList ON YouTube.id=MyAnimeList.id""", 
			conn
		)
		
		success_count = len(new_df['title']) - title_count
		st.text(f'{success_count} titles successfully stored.')


if __name__ == '__main__':
	cur, conn = setup_db('anime.db')
	
	st.title('Shuriken')
	
	season = st.selectbox('Season', ('spring', 'summer', 'fall', 'winter'))
	years = reversed(range(1972, int(time.ctime().split(' ')[-1]) + 1))
	year = st.selectbox('Year', tuple(years))
	limit = int(st.text_input('Title Limit (default: 1 | max: 20)', '1'))
	if st.button('Search Season'):
		seasonal_search = SeasonalSearch(season, year, cur, conn, limit)
		seasonal_search.run()

	anime = st.text_input('Title')
	if st.button('Search Title'):
		search_by_title(anime, cur, conn)
	
	if st.button('Analyze'):
		analyze_data(cur, conn)
	
	client_id = os.getenv('MAL_CLIENT_ID')
	client_secret = os.getenv('MAL_CLIENT_SECRET')
	if st.button('Get Auth Code'):
		code_verifier = code_challenge = get_new_code_verifier()
		open_authorization_link(code_challenge, client_id)
		os.environ['MAL_CODE_VERIFIER'] = code_verifier
	
	authorization_code = st.text_input('Auth Code')
	if authorization_code:
		os.environ['MAL_AUTH_CODE'] = authorization_code
		st.text('Authorization code saved.')
	
	if st.button('Refresh Token'):
		code_verifier = os.getenv('MAL_CODE_VERIFIER')
		authorization_code = os.getenv('MAL_AUTH_CODE')
		token = generate_new_token(authorization_code, code_verifier, client_id, client_secret)
		os.environ['MAL_ACCESS_TOKEN'] = token['access_token']
		st.text('Access token saved.')

	if st.button('Test Token'):
		access_token = os.getenv('MAL_ACCESS_TOKEN')
		test_token(access_token)
