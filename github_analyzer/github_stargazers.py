import ray
import time
import requests
import json
import time

users = []
locations = []
token = 'token 4ce3c2998285edb7ae2fcf56759ecc866578d68b'
headers = {'Authorization': token}
starsURL = 'https://api.github.com/repos/ray-project/ray/stargazers?page='

ray.init()

@ray.remote
def addLocationsForPage(page):
	locationsThisPage = []
	pageURL = starsURL + str(page)
	print(pageURL)
	response = requests.get(pageURL,headers=headers)
	print(str(len(response.json())) + ' users returned!')
	print(json.dumps(response.json(), indent=2))
	count = 0
	for user in response.json():
		count += 1
		if count%5 == 0:
			time.sleep(1)
		login = user['login']
		userURL = 'https://api.github.com/users/' + login
		userResponse = requests.get(userURL,headers=headers)
		try:
			location = userResponse.json()['location']
		except KeyError:
			print("Location not found!")
			print(json.dumps(userResponse.json(), indent=2))
			location = 'None'
		print(location)
		locationsThisPage.append(location)
	return locationsThisPage

futures = [addLocationsForPage.remote(page) for page in range(201,301)]
with open('ray_stargazers_locations.txt', 'a') as file:
	for f in ray.get(futures):
		print('Got ' + str(len(f)) + ' locations!')
		locations = locations + f
		for l in f:
			file.write("%s\n" % l)
file.close()