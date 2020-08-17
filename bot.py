# FsBot v0.4
# Made by Jan Imhof

import requests
import json
import discord
import datetime
import urllib3
import geopy.distance
from discord.ext import commands

# Opening the config.json file that stores the Discord Token and avwx Auth code
with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['token']  # Psst keep secret
client = commands.Bot(command_prefix='!')  # Meaning that all commands must start with a ! so for instance !metar
client.remove_command('help')  # removes the custom help command

# Global variable
version = 'FsBot v0.4'


def get_metar(loc):
    url = 'https://avwx.rest/api/metar/' + loc + '?options=&airport=true&reporting=true&format=json&onfail=cache'
    headers = {'Authorization': config['authHeader']}
    r = requests.request("GET", url, headers=headers)
    data = r.json()
    return data


def get_taf(loc):
    url = 'https://avwx.rest/api/taf/' + loc + '?options=summary&airport=true&reporting=true&format=json&onfail=cache'
    headers = {'Authorization': config['authHeader']}
    r = requests.request("GET", url, headers=headers)
    data = r.json()
    return data['raw']


def get_station(loc):
    url = 'https://avwx.rest/api/station/' + loc + '?format=json'
    headers = {'Authorization': config['authHeader']}
    r = requests.request("GET", url, headers=headers)
    data = r.json()
    return data


@client.command()
async def help(ctx):
    help_embed = discord.Embed(
        title=version,
        description='See the commands list below',
        color=discord.Colour.orange()
    )
    # Setting all the Values
    help_embed.set_footer(text='Simulation use only')
    help_embed.add_field(name='Get a decoded METAR', value='!metar ICAO', inline=False)
    help_embed.add_field(name='Get the current ZULU time', value='!zulu', inline=False)
    help_embed.add_field(name='Get the number of users on Vatsim', value='!vatsim', inline=False)
    help_embed.add_field(name='Get airport information', value='!station ICAO', inline=False)
    help_embed.add_field(name='Get distance between airports', value='!distance ICAO ICAO', inline=False)
    help_embed.add_field(name='Convert between units', value='!convert amount unit_from unit_to e.g:\n '
                                                             '!convert 1000 gal lbs \n'
                                                             'Supported units: \n'
                                                             '- gal, gallons \n'
                                                             '- lbs, pounds \n'
                                                             '- kg, kilograms\n'
                                                             '- liters', inline=False)
    await ctx.send(embed=help_embed)


@client.command()
async def metar(ctx, arg):
    data = get_metar(arg)
    my_embed = discord.Embed(
        title=version,
        description='',
        color=discord.Colour.orange()
    )

    # Getting the station
    station_name = data['station']

    # Formatting Time issued correctly
    temp_data = data['time']['dt'][11:]
    temp_list = temp_data.split('+')
    time_issued = temp_list[0] + 'Z'  # So we get the time like 17:30:00Z

    # Getting the wind
    if data['wind_speed']['repr'] == 'null':
        wind_speed = 'null'
    else:
        wind_speed = data['wind_speed']['repr']
    wind = data['wind_direction']['repr'] + ' @ ' + wind_speed + 'kts'

    # Getting the visibility
    if data['units']['visibility'] == 'sm':
        if data['visibility']['repr'] is not None:
            if data['visibility']['repr'] != 'CAVOK':
                visibility = str(data['visibility']['repr'] + 'SM')
            else:
                visibility = str(data['visibility']['repr'])
        else:
            visibility = 'null'
    else:
        if data['visibility']['repr'] is not None:
            if data['visibility']['repr'] != 'CAVOK':
                visibility = str(data['visibility']['repr'] + 'M')
            else:
                visibility = str(data['visibility']['repr'])
        else:
            visibility = 'null'

    # Getting the Cloud layers into a nice List
    cloud_layers = ''
    if data['clouds']:
        for item in data['clouds']:
            cloud_layers = cloud_layers + item['type'] + ' @ ' + str(item['altitude']) + '00 feet, '
        cloud_layers = cloud_layers[
                       :-2]  # We have the [:-2] there to remove the final , and the whitespace that is not needed
    else:
        cloud_layers = 'No information provided'

    # Getting the temperature
    if data['temperature']['repr'] != 'null':
        temperature = data['temperature']['repr'].replace('M', '-') + ' °C'
    else:
        temperature = 'null'

    # Getting the dewpoint
    if data['dewpoint']['repr'] != 'null':
        dewpoint = data['dewpoint']['repr'].replace('M', '-') + ' °C'
    else:
        dewpoint = 'null'

    # Getting the correct altimeteres (This is because some stations return mb and some inHg)
    if data['units']['altimeter'] == 'inHg':
        altimeter_inHg = str(data['altimeter']['value'])
        altimeter_mb = str(round(data['altimeter']['value'] * 33.864))
    else:
        altimeter_mb = str(data['altimeter']['value'])
        altimeter_inHg = str(round(float(data['altimeter']['value'] / 33.864), 2))
    altimeter = altimeter_inHg + ' inHg / ' + altimeter_mb + ' mb'

    # Getting the raw metar
    metar_raw = data['raw']

    # Setting all the Values
    my_embed.set_footer(text='Simulation use only')
    my_embed.add_field(name='Station Name:', value=station_name, inline=False)
    my_embed.add_field(name='Time issued:', value=time_issued, inline=False)
    my_embed.add_field(name='Wind:', value=wind, inline=False)
    my_embed.add_field(name='Visibility:', value=visibility, inline=False)
    my_embed.add_field(name='Clouds:', value=cloud_layers, inline=False)
    my_embed.add_field(name='Temperature:', value=temperature, inline=False)
    my_embed.add_field(name='Dewpoint:', value=dewpoint, inline=False)
    my_embed.add_field(name='Altimeter:', value=altimeter, inline=False)
    my_embed.add_field(name='Raw METAR:', value=metar_raw, inline=False)
    await ctx.send(embed=my_embed)


@client.command()
async def station(ctx, arg):
    data = get_station(arg)
    my_embed = discord.Embed(
        title=version,
        description='',
        color=discord.Colour.orange()
    )

    runways = ''
    for item in data['runways']:
        if item['length_ft'] != 0:  # To prevent "fake" runways with length 0 example: LAX 09L/09R with 0 feet
            runways = runways + item['ident1'] + ' / ' + item['ident2'] + '  ' + str(item['length_ft']) + ' feet\n'
    my_embed.set_footer(text='Simulation use only')
    my_embed.add_field(name='Station Name:', value=data['name'], inline=False)
    my_embed.add_field(name='Country:', value=data['country'], inline=False)
    my_embed.add_field(name='Runways:', value=runways, inline=False)
    my_embed.add_field(name='Elevation:',
                       value=str(data['elevation_ft']) + ' feet / ' + str(data['elevation_m']) + ' m', inline=False)
    my_embed.add_field(name='Coordinates:', value=str(data['latitude']) + ' / ' + str(data['longitude']), inline=False)
    await ctx.send(embed=my_embed)


@client.command()
async def convert(ctx, arg1, arg2, arg3):
    # arg1 = amount e.g 1000
    # arg2 = current unit e.g lbs
    # arg3 = unit to convert to e.g gal
    convert_embed = discord.Embed(
        title=version,
        description='',
        color=discord.Colour.orange()
    )
    arg1f = float(arg1)
    result = 0.0
    if arg2 == 'lbs':
        if arg3 == 'gal':
            result = arg1f * 0.14925
        if arg3 == 'kg':
            result = arg1f * 0.45359
        if arg3 == 'liters':
            result = arg1f * 0.56499
    if arg2 == 'gal':
        if arg3 == 'lbs':
            result = arg1f * 6.7
        if arg3 == 'kg':
            result = arg1f * 3.03907
        if arg3 == 'liters':
            result = arg1f * 3.78541
    if arg2 == 'kg':
        if arg3 == 'lbs':
            result = arg1f * 2.20462
        if arg3 == 'gal':
            result = arg1f * 0.32905
        if arg3 == 'liters':
            result = arg1f * 1.24558
    if arg2 == 'liters':
        if arg3 == 'lbs':
            result = arg1f * 1.76995
        if arg3 == 'gal':
            result = arg1f * 0.26417
        if arg3 == 'kg':
            result = arg1f * 0.80284

    convert_embed.add_field(name=arg1 + ' ' + arg2 + ' are:', value=str(round(result, 2)) + ' ' + arg3, inline=False)
    convert_embed.set_footer(text='Simulation use only, based on Jet A Fuel')
    await ctx.send(embed=convert_embed)


@client.command()
async def zulu(ctx):
    zulu_embed = discord.Embed(
        title=version,
        description='',
        color=discord.Colour.orange()
    )
    now = datetime.datetime.utcnow().strftime("%H:%M")
    zulu_embed.add_field(name='Current ZULU time:', value=now, inline=False)
    await ctx.send(embed=zulu_embed)


@client.command()
async def distance(ctx, arg1, arg2):
    distance_embed = discord.Embed(
        title=version,
        description='',
        color=discord.Colour.orange()
    )
    station1 = get_station(arg1)
    station2 = get_station(arg2)
    coords_1 = (station1['latitude'], station1['longitude'])
    coords_2 = (station2['latitude'], station2['longitude'])
    my_distance = geopy.distance.geodesic(coords_1, coords_2).nm
    distance_embed.add_field(name='Distance:', value="The distance between " + station1['icao'] + " and " +
                                                     station2['icao'] + " is: " + str(round(my_distance, 2)) + ' nm',
                             inline=False)
    distance_embed.set_footer(text='Simulation use only')
    await ctx.send(embed=distance_embed)


@client.command()
async def vatsim(ctx):
    vatsim_embed = discord.Embed(
        title=version,
        description='',
        color=discord.Colour.orange()
    )
    http = urllib3.PoolManager()
    response = http.request('GET', 'http://cluster.data.vatsim.net/vatsim-data.txt')
    data = response.data.decode('utf-8')
    total_clients_index = data.find('CONNECTED CLIENTS')
    unique_clients_index = data.find('UNIQUE USERS')
    total_clients = data[total_clients_index + 19: total_clients_index + 25]
    unique_clients = data[unique_clients_index + 14: unique_clients_index + 20]
    vatsim_embed.add_field(name='Currently connected Clients:', value=total_clients, inline=False)
    vatsim_embed.add_field(name='Currently connected Unique Users:', value=unique_clients, inline=False)
    await ctx.send(embed=vatsim_embed)


client.run(TOKEN)
