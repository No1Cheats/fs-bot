# FS-Bot

A simple Python Discord bot using the discord.py library. This bot provides information to Simulator Pilots, it provides weather, station information and can calculate distances and convert between different fuel units

## Getting Started

This project works on Heroku or your own VPS

### Prerequisites

All of the prerequisites are listed below and are also mentioned in the requirements.txt.

```
discord.py
geopy
urllib3
datetime
requests
```

Further, a config.json file is needed, this should be located in the root folder. This includes the Discord Token as well as the AVWX authorization Header. 
The latter can be obtained on [AVWX](https://avwx.rest/). The format needs to be as follows

```
{
	"token": "Discord Token",
	"authHeader": "Authorization Header"
}
```

## Built With

* [discord.py](https://github.com/Rapptz/discord.py) - The main framework used
* [requests](https://github.com/psf/requests) - HTTP library
* [urllib3](https://github.com/urllib3/urllib3) - Thread Safe HTTP library
* [geopy](https://github.com/geopy/geopy) - used for distance calculations
* [AVWX](https://github.com/avwx-rest/avwx-api) - used for current weather and station information

## Authors

* **Jan Imhof** - [No1Cheats](https://github.com/No1Cheats)

## License

This project is licensed under the MIT License - see the [LICENSE.md](license) file for details

