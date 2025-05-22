# blueeye
X BOT (beta)
markdown
# Blue Eye X Bot

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

Blue Eye X Bot is a Python 3.12-based automation tool that posts curated technology news and historical tech events to Twitter (X). It fetches articles from [Digiato](https://digiato.com/), summarizes them using OpenAI's GPT-4, and shares them with relevant hashtags. Additionally, it posts daily Persian calendar updates with tech-related historical events, accompanied by custom day-of-week images.

## Features

- **Automated News Sharing**: Scrapes and summarizes the latest tech articles from Digiato every 30 minutes.
- **Historical Tech Events**: Posts daily Persian (Jalali) calendar updates with three historical tech events for the current date.
- **Smart Hashtag Generation**: Uses OpenAI to generate relevant English tech hashtags for posts.
- **Persian Calendar Support**: Displays dates in the Persian calendar with custom daily images.
- **Twitter API Integration**: Uses Twitter API v1.1 for media uploads and v2 for tweeting.
- **Link Tracking**: Stores posted article links to prevent duplicates.

## Prerequisites

- **Python 3.12**
- Twitter Developer Account with API keys (v1.1 and v2 access)
- OpenAI API key
- Required Python libraries (listed in `requirements.txt`)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/blue-eye-x-bot.git
   cd blue-eye-x-bot
Install Dependencies:
bash
pip install -r requirements.txt
Set Up API Keys:
Create a tKEYS.py file in the project root with the following:
python
APIKEY = "your_twitter_api_key"
APIKEYSECRET = "your_twitter_api_secret"
ACCESSTOKEN = "your_access_token"
ACCESSTOKENSECRET = "your_access_token_secret"
id = "your_twitter_handle"
oaien = "your_openai_api_key"
Prepare Daily Images:
Place the following image files in the project root for calendar posts:
tsat.png, tsun.png, tmon.png, ttue.png, twed.png, tthur.png, tfri.png
Run the Bot:
bash
python blue_eye_x_bot.py
Usage
The bot runs continuously with the following schedule:
Every 30 minutes: Fetches new Digiato articles, selects the most relevant one, summarizes it, and posts it to Twitter with generated hashtags.
Daily: Posts a Persian calendar update with three historical tech events for the current date, including a day-specific image.
Console logs provide debugging and monitoring information.
Previously posted links are stored in t_digiato_sent_links.txt to avoid duplicates.
File Structure
blue-eye-x-bot/
├── blue_eye_x_bot.py        # Main bot script
├── tKEYS.py                 # API keys (not included in repo)
├── t_digiato_sent_links.txt # Tracks posted article links
├── tsat.png                 # Image for Saturday
├── tsun.png                 # Image for Sunday
├── ...                      # Other daily images
├── requirements.txt         # Python dependencies
└── README.md                # This file
Dependencies
tweepy: Twitter API interaction
requests: Web content fetching
beautifulsoup4: Web scraping
openai: Article summarization and hashtag generation
jdatetime: Persian (Jalali) calendar support
schedule: Task scheduling
pytz: Timezone handling
Install dependencies:
bash
pip install tweepy requests beautifulsoup4 openai jdatetime schedule pytz
Configuration
Twitter API Keys: Obtain from Twitter Developer Portal.
OpenAI API Key: Obtain from OpenAI.
Daily Images: Ensure day-specific images (tsat.png, etc.) are in the project root.
Link Storage: The bot creates t_digiato_sent_links.txt to track posted articles.
Contributing
Contributions are welcome! To contribute:
Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a Pull Request.
Please ensure your contributions align with the GPL-3.0 License (LICENSE).
License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for details.
Contact
For questions or support, reach out via Telegram: @callsys_asm.
```
