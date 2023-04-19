# DiscogsPlus

DiscogsPlus is a work-in-progress project that aims to improve the user experience of Discogs by offering advanced search, filtering, and recommendation features. It includes a YouTube playlist generator based on search parameters and a recommendation system using collaborative filtering.

## Introduction

DiscogsPlus is an advanced search engine for Discogs, designed to help users discover obscure music and create YouTube playlists based on specific search parameters. The project's motivation is to enhance the Discogs experience by providing more refined search options and seamless integration with YouTube playlists.

## Technical Overview

The project is built using Python, Flask, and PostgreSQL. It utilizes the Discogs Data Dump for obtaining music data and the YouTube API for creating and managing playlists. The data is extracted from the Discogs Data Dump and stored in a local PostgreSQL database. A subset of the data, focused primarily on the electronic genre, is hosted in the cloud to improve performance.

The main components of the project include:

- Flask web application for user interaction
- PostgreSQL database for storing music data
- API for accessing YouTube services

## Advanced Search Features

DiscogsPlus offers advanced search and filtering options, allowing users to discover music that fits their specific interests. The search options include:

- Filtering by specific range of years
- Filtering by countries
- Filtering by styles
- Filtering by artists with only one release
- Filtering by records without a master release


## YouTube Playlist Generation

Users can create YouTube playlists based on their search parameters. The process involves:

1. Fetching search results based on user input
2. Querying the YouTube API for videos corresponding to the search results
3. Adding the videos to a new or existing YouTube playlist

## Challenges and Limitations

During the project development, challenges were faced with handling large volumes of data and optimizing the search algorithm to avoid request timeouts. The current web application has limitations regarding request processing time, causing occasional timeouts when the response takes longer than 30 seconds.

## Future Enhancements

Planned improvements and features to be added in the future include:

- Personalized recommendations using user's collection and wantlist data
- Additional search and filtering options


## Installation and Usage

To set up and run the DiscogsPlus project locally, follow these steps:

### Prerequisites

- Python 3.7 or later
- pip (Python package installer)
- PostgreSQL

### Setup

1. Clone the repository:
  ```
  git clone https://github.com/justinpakzad/DiscogsPlus.git
  ```
2. Create a virtual environment and activate it:
  ```
  python -m venv venv
  source venv/bin/activate # For Linux/MacOS
  venv\Scripts\activate # For Windows
  ```
3. Install the required Python packages:
  ```
  pip install -r requirements.txt
  ```
4. Set up the PostgreSQL database:

  - You can download the Discogs Data Dump and extract the necessary data from [https://github.com/philipmat/discogs-xml2db].

  - Create a new PostgreSQL database and import the extracted data.


5. Set up the environment variables:

  - Create a `.env` file in the project root directory.
  - Add the following variables and replace the placeholders with your actual values:
  ```
  # Database configuration
  HOST=<your_database_host>
  DATABASE_NAME=<your_database_name>
  USER_DB=<your_database_username>
  PASSWORD=<your_database_password>
  PORT=<your_database_port>

  # YouTube API credentials
  YOUTUBE_CLIENT_SECRETS_FILE=<path_to_your_client_secrets_file>
  ```
  Replace the placeholders with your actual credentials and API keys.
### Running the Project

1. Start the Flask development server:
  ```
  python app.py
  ```

2. Open your web browser and navigate to `http://localhost:5000` to access the DiscogsPlus web application.

3. Use the search and filtering options to find music and create YouTube playlists based on your preferences.

Please note that this project is primarily intended for local use and demonstration. Some features may not be fully functional when deployed to a web server.
