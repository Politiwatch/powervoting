# PowerVoting
[PowerVoting](https://powervoting.org) is a site that lets you compare the relative power of a vote in a federal election across the United States.

### Local Deployment
* Create a file called `.env` and set its contents to `API_KEYS=<a Google Civic Information API key>` (of course, replace the placeholder with an API key for the [Civic Information API](https://developers.google.com/civic-information/)).
* Run `pipenv shell`. (You may need to install Pipenv using `pip3 install pipenv` if you don't have it already.)
* Run the server using `python3 src/main.py`.