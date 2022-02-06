<div align="center" id = "top">
  <img src="ravager.png"  alt="ravager logo"/>
  <h3>A telegram bot that sails the high seas and brings treasures from the land unknown</h3> 
</div>

## Contents
- [Introduction](#Introduction)
- [Features](#Features)
- [Environment Variables](#Environment-Variables)
- [Installation](#Installation)
  - [Heroku](#Heroku)
  - [Docker](#Docker)
- [Contributing](#Contributing)
- [Authors](#Authors)
- [License](#License)

## Introduction

This is a telegram bot which supports torrent file,magnet uri as well as direct download links,it uses aria2 as a backend 
for downloading the content and uploads it to google drive. It can be deployed to heroku free dyno or on a server.

## Features

- Easy-to-use heroku one click deploy
- Support for multiple google accounts and telegram chats (group and private)
- Preserves the directory structure of uploaded content and doesn't require any archiving.
- Support for Personal and Shared Drive and changing them on the fly
- Flexible in terms deploying and installing options
- Single multi-arch docker image
- Recover from failed upload
- Download once upload multiple times
- Multiple optimisations for running on heroku free dyno


## Environment Variables
To run this project, you will need to set the following environment variables :
<details>
    <summary>Core Environment Variables</summary>
    <ul>
        <details>
            <summary>APP_URL</summary>
            <p></p>
        </details>
        <details> 
            <summary>CLIENT_CONFIG</summary>
            <p></p>
        </details>
        <details>
            <summary>REDIS_URL</summary>
            <p></p>
        </details> 
        <details>
            <summary>BOT_TOKEN</summary>
            <p></p>
        </details>
        <details>
            <summary>STATE_SECRET_KEY</summary>
            <p></p>
        </details>
        <details>
            <summary>BOT_URL</summary>
            <p></p>
        </details>
        <details>
            <summary>ALLOWLIST</summary>
            <p></p>
        </details>
        <details>
            <summary>GROUP_PASSWORD</summary>
            <p></p>
        </details>
        <details>
            <summary>USER_PASSWORD</summary>
            <p></p>
        </details> 
    </ul>
</details>
<details>
    <summary>Environment Variables for Heroku only</summary>
    <ul>
    <details>
        <summary>KEEP_HEROKU_ALIVE</summary>
        <p></p>
    </details>
    <details>
        <summary>HEROKU_API_TOKEN</summary>
        <p></p>
    </details>
    </ul>
</details>
<details>
    <summary>Optional Environment Variables</summary>
    <ul>
        <details>
        <summary>OAUTH_URL</summary>
        <p></p>
        </details>
        <details>
        <summary>DATABASE_URL</summary>
        <p></p>
        </details>
        <details>
        <summary>REDIS_URL</summary>
        <p></p>
        </details>
        <details>
        <summary>LOG_LEVEL</summary>
        <p></p>
        </details>
        <details>
        <summary>PORT</summary>
        <p></p>
        </details>
    </ul>
</details>

<p align="right">(<a href="#top">back to top</a>)</p>

## Installation
- Ravager can be deployed and used in the following ways

## Heroku
- Click [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/coolfool/ravager) and fill the environment variables accordingly. 
<p align="right">(<a href="#top">back to top</a>)</p>

## Docker

- ### Docker Compose
    1) Download [docker-compose.yml]() for running on a server or [docker-compose-local.yml]() for running locally with ngrok or other tunneling service for oauth authentication
    2) Open the file in a text editor and fill the environment variables
    3) - If `docker-compose-local.yml` is used you have to create a docker network called `ravager_net`
       - Forward the connection for `ravager_net` with port `8443` using ngrok or some other tunneling service.
       - Get the ip for `ravager_net` using the command `docker inspect ravager_net`
       - For ngrok the command should be as follows: `./ngrok https <ravager_net_ip>:8443`
       - The url from ngrok will be used as telegram bot webhook and oauth endpoint
       - Add the ngrok url and the oauth endpoint `ngrok_url/oauth_handler` to google's oauth api authorized domain.
    4) Execute the following command in the same directory
        ```
        docker-compose up -d
        ```
    5) The bot should be up and running
    6) For checking the logs you can use `docker logs -f ravager`
<p align="right">(<a href="#top">back to top</a>)</p>

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

