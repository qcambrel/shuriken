import requests
import secrets
import webbrowser


class MALAccessManager:
	def __init__(self):
		if 'MAL_ACCESS_TOKEN' in os.environ:
			self.access_token = os.getenv('MAL_ACCESS_TOKEN')
			self.testing = input('Would you like to test your access token? [y/n] ')
			if self.testing == 'y':
				self.test_token()
		else:
			self.client_id = os.getenv('MAL_CLIENT_ID')
			self.client_secret = os.getenv('MAL_CLIENT_SECRET')
			self.code_verifier = self.code_challenge = self.get_new_code_verifier()
			self.open_authorization_link()
			os.environ['MAL_CODE_VERIFIER'] = self.code_verifier
			self.authorization_code = input('Enter the authorization code: ')
			os.environ['MAL_AUTH_CODE'] = self.authorization_code
			print('Authorization code saved.')
			self.access_token = self.generate_new_token()['access_token']
			os.environ['MAL_ACCESS_TOKEN'] = self.access_token
			print('Access token saved.')
			self.test_token()


	def get_new_code_verifier(self) -> str:
		"""Generate a new code verifier and code challenge."""
	
		token = secrets.token_urlsafe(100)
		return token[:128]


	def open_authorization_link(self):
		"""Open the authorization link to access the auth code."""

		url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={self.client_id}&code_challenge={self.code_challenge}'
		webbrowser.open_new_tab(url)


	def generate_new_token(self):
		"""Generate new token using the auth code."""
		
		url = 'https://myanimelist.net/v1/oauth2/token'
		data = {
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'code': self.authorization_code,
			'code_verifier': self.code_verifier,
			'grant_type': 'authorization_code'
		}

		response = requests.post(url, data)
		response.raise_for_status()

		token = response.json()
		response.close()

		return token


	def test_token(self):
		"""Test new access token."""
		
		url = 'https://api.myanimelist.net/v2/users/@me'
		response = requests.get(url, headers={'Authorization': f'Bearer {self.access_token}'})
		response.raise_for_status()
		user = response.json()
		response.close()
		print(f'Welcome {user["name"]}!')