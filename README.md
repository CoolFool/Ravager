<div align="center" id = "top">
  <img src="ravager.png"  alt="ravager logo"/>
  <h3>A telegram bot that downloads content in the form of torrent and direct download links and mirrors them 1:1 to google drive</h3> 
</div>

## Contents
- [Introduction](#Introduction)
- [Features](#Features)
- [Environment Variables](#Environment-Variables)
- [Installation](#Installation)
  - [Heroku](#Heroku)
  - [Docker](#Docker)
- [Bot Commands](#Telegram-Bot-Commands)
- [Contributing](#Contributing)
- [Authors](#Authors)
- [License](#License)

## Introduction

This is a telegram bot which supports torrent file,magnet uri as well as direct download links,it uses aria2 as a backend 
for downloading the content and uploads it to google drive. It can be deployed to heroku free dyno or on a server.

## Features

- Easy-to-use heroku one click deploy
- Support for multiple telegram chats (group and private) and Google accounts with built-in oauth support
- Preserves the directory structure of uploaded content and doesn't require any archiving.
- Support for Personal and Shared Drive and changing them on the fly
- Flexible in terms deploying and installing options
- Single multi-arch docker image
- Recover from failed upload
- Download once upload multiple times
- Admin interface for getting logs and other system info
- Multiple optimisations for running on heroku free dyno


## Environment Variables
To run this project, you will need to set the following environment variables :
<details open>
    <summary>Core Environment Variables</summary>
    <ul>
        <details>
            <summary>APP_URL</summary>
            <p>The url where the app will be hosted i.e for heroku it will be 
            https://{appname}.herokuapp.com or for self-hosted server it will be
            https://{hostname_or_ip}:{port} where port is usally 8443</p>
        </details>
        <details> 
            <summary>CLIENT_CONFIG</summary>
                <ol>
                    <h4>To create a Google Cloud project:</h4>
                    <ol>
                        <li>Open the <a href="https://console.cloud.google.com/">Google Cloud Console.</a></li>
                        <li>At the top-left, click Menu > <b>IAM & Admin</b> > <b>Create a Project.</b></li>
                        <li>In the <b>Project Name</b> field, enter a descriptive name for your project.<br>
                            Optional: To edit the <b>Project ID</b>, click <b>Edit</b>. The project ID can't be changed after the project is created, so choose an ID that meets your needs for the lifetime of the project.<br>
                            In the <b>Location</b> field, click <b>Browse</b> to display potential locations for your project. Then, click <b>Select</b></li>
                        <li>Click <b>Create.</b> The console navigates to the Dashboard page and your project is created within a few minutes.
                    </ol>
                    <h4>Configure the Project:</h4>
                    <ol>
                        <li>Open the <a href="https://console.cloud.google.com/home/dashboard">Google Cloud Console Dashboard</a> and select your project</li>
                        <li>At the top-left, click Menu > <b>APIs & Services</b> </li>
                        <li>On the left side menu,Select <b>Library/</b></li>
                        <li>Search for <b>Google Drive</b> in the search bar the API library and Select and <b>Enable Google Drive API</b></li>
                        <li>Again at the top-left, click Menu > <b>APIs & Services</b> </li>
                        <li>On the left side menu,Select <b>Credentials</b>, select <b>Create credentials</b>, then <b>OAuth client ID</b>.</li>
                        <li>You may be prompted to set a product name on the <b>Consent screen</b>; if so, click <b>Configure consent screen</b>, supply the requested information following the notes below, and click Save to return to the Credentials screen</li>
                        <h4>OAuth consent screen Configuration: </h4>
                            <ol>
                                <li>Select user type as <b>external</b></li>
                                <li>Fill the required details</li>
                                <li>In the scopes page,Click on <b>Add or Remove Scopes</b></li>
                                <li>Search and Add <b>/auth/drive</b> and <b>/auth/drive.metadata</b> scopes and click on update</li>
                                <li>You should see the scopes added in <b>Your Sensitive Scopes</b> Section</li>
                                <li>Click on <b>Save and Continue</b> for rest of the sections</li>
                                <li>On the OAuth consent screen Click on <b>Publish App</b> and <b>Confirm</b></li>
                                <li>Ignore Needs verification warning for the time being,the users will only see the warning while authorizing but please note there's a limit to number of users for unverified apps</li>
                            </ol>
                        <li>Again On the left side menu,select <b>Credentials</b> and then select <b>Create credentials</b>, then <b>OAuth client ID</b></li>
                        <li>Select Web Application for the Application Type. Follow the instructions to enter JavaScript origins, redirect URIs, or both.
                            <ol>
                                <li>In <b>Javascript Origins</b> add your domain name which should be <b>APP_URL</b></li>
                                <li>In <b>Authorized redirect URIs</b> Add your redirect uri which should be <b>APP_URL/oauth_handler</b></li>
                            </ol>
                        </li>
                        <li>Click <b>Create.</b></li>
                        <li>Download your client_secret.json from the popup modal or from under OAuth 2.0 Client IDs</li>
                        <li><b>Open</b> client_secret.json and <b>copy</b> the whole config as CLIENT_CONFIG</li>
                    </ol>
                </ol>
        </details>
        <details>
            <summary>BOT_TOKEN</summary>
            <p>The bot token for telegram bot, for more info on how to create a bot and get
            a token visit <a href="https://core.telegram.org/bots#3-how-do-i-create-a-bot">How to create a telegram bot</a></p>
        </details>
        <details>
            <summary>STATE_SECRET_KEY</summary>
            <p>A random alphanumeric text used as a salt in generating state for oauth authorization. <br>
           Not required in heroku caused generator is used while deploying</p>
        </details>
        <details>
            <summary>BOT_URL</summary>
            <p>The telegram bot url,this is usually in the form https://t.me/{bot_username}</p>
        </details>
        <details>
            <summary>ALLOWLIST</summary>
            <p>Should there be a filter where password is required for access to the bot <br>
                Set as "True" or "False"</p>
        </details>
        <details>
            <summary>GROUP_PASSWORD</summary>
            <p>Password used for allowing a group chat access to the bot,should be set if "ALLOWLIST" is enabled</p>
        </details>
        <details>
            <summary>USER_PASSWORD</summary>
            <p>Password used for allowing a user access to the bot,should be set if "ALLOWLIST" is enabled</p>
        </details> 
    </ul>
</details>
<details open>
    <summary>Environment Variables for Heroku only</summary>
    <ul>
    <details>
        <summary>KEEP_HEROKU_ALIVE</summary>
        <p> The application hosted in heroku free dyno sleeps after 20 minutes of no activity,to conteract this the application
        can ping itself every 5 minutes and keep itself alive.<br>Should be set to either "True" or "False"
        </p>
    </details>
    <details>
        <summary>HEROKU_API_TOKEN</summary>
        <p>Heroku dynos are restarted every 24 hours + random(0-216)minutes,but if there is a restart before that the restart time is reset.
        The bot can give you the approx restart time and restart itself when no activity occurs for 4 hours if it has the Platform API Token<br>
        The token can be found <a href="https://dashboard.heroku.com/account">here</a></p>
    </details>
    </ul>
</details>
<details open>
    <summary>Optional Environment Variables</summary>
    <ul>
        <details>
        <summary>DATABASE_URL</summary>
        <p>The DATABASE URI for custom SQL Database</p>
        </details>
        <details>
        <summary>REDIS_URL</summary>
        <p>The URL for connecting to custom redis instance</p>
        </details>
        <details>
        <summary>LOG_LEVEL</summary>
        <p>The log level to be displayed in console,all the log levels can be found <a href="https://docs.python.org/3/library/logging.html#logging-levels">here</a><br>
        Only numeric value is supported</p>
        </details>
        <details>
        <summary>PORT</summary>
        <p>Custom port for hosting the application,but only Ports supported by telegram should be used when the application is not hosted behind a reverse proxy</p>
        </details>
    </ul>
</details>

<p align="right">(<a href="#top">back to top</a>)</p>

## Installation
- Ravager can be deployed and used in the following ways

## Heroku
- Click [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/coolfool/ravager) and fill the environment variables accordingly. 
- If the addons section is empty in the app dashboard on heroku add the following addons:
   - Heroku Postgres with plan Hobby-Dev:Free
   - Heroku Redis with plan Hobby-Dev:Free
- Restart the app
<p align="right">(<a href="#top">back to top</a>)</p>

## Docker

- ### Docker Compose
    1) Download [docker-compose.yml](https://github.com/CoolFool/Ravager/blob/main/docker-compose.yml) for running on a server or [docker-compose-local.yml](https://github.com/CoolFool/Ravager/blob/main/docker-compose-local.yml) for running locally with ngrok or other tunneling service for oauth authentication
    2) Open the file in a text editor and fill the environment variables
    3) - If `docker-compose-local.yml` is used you have to create a docker network called `ravager_net`
       - Forward the connection for `ravager_net` with port `8443` using ngrok or some other tunneling service.
       - Get the ip for `ravager_net` using the command `docker inspect ravager_net`
       - For ngrok the command should be as follows: `./ngrok http <ravager_net_ip>:8443`
       - The url from ngrok will be used as telegram bot webhook and oauth endpoint
       - Add the ngrok url and the oauth endpoint `ngrok_url/oauth_handler` to google's oauth api authorized domain.
    4) Execute the following command in the same directory
        ```
        docker-compose up -d
        ```
    5) The bot should be up and running
    6) For checking the logs you can use `docker logs -f ravager`
<p align="right">(<a href="#top">back to top</a>)</p>
    
## Telegram Bot Commands
- `/start` : Start the authorization flow for google drive access
- `/add_drive` : Set default drive either personal or shared drive through the menu
- `/download` : Add download task
- `/upload` : Upload content if a download fails you can reply to the source message or upload multiple times
- `/abort` : Abort an ongoing task
- `/admin_interface` : Admin interface access (only available in private chat and for admins)
- `/revoke` : Revoke and delete your Google account on the bot
- `/help` : See all the commands

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>


## Authors

- [@coolfool](https://www.github.com/coolfool)

<p align="right">(<a href="#top">back to top</a>)</p>

## License

[MIT](https://choosealicense.com/licenses/mit/)

<p align="right">(<a href="#top">back to top</a>)</p>

