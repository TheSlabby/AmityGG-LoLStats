from django.shortcuts import HttpResponseRedirect, render
from utils import get_db_handle as GetDB
from datetime import datetime
import math

client = GetDB()

LIMIT = 20
HOME_MATCH_LIMIT = 1000

def home(request):
    # get all matches
    coll = client.get_database('leagueoflegends').get_collection('matches')
    matches = coll.find().sort('info.gameCreation', -1).limit(HOME_MATCH_LIMIT)
    #get the number of matches
    numMatches = coll.count_documents({})
    
    # this might be a bad idea (TODO i need to create a match object for each match)
    userData = {}
    champData = {}
    for match in matches:
        for participant in match['info']['participants']:
            #user data
            if participant['summonerName'] not in userData:
                userData[participant['summonerName']] = {
                    'kills': 0,
                    'wins': 0,
                }
            userData[participant['summonerName']]['kills'] += participant['kills']
            if participant['win']:
                userData[participant['summonerName']]['wins'] += 1
            
            #champion data
            if participant['championName'] not in champData:
                champData[participant['championName']] = {
                    'kills': 0,
                    'wins': 0,
                }
            champData[participant['championName']]['kills'] += participant['kills']
            if participant['win']:
                champData[participant['championName']]['wins'] += 1
    
    #sort into a list of tuples
    data = []
    for user, value in userData.items(): data.append((user, value['kills'], value['wins']))
    data.sort(key=lambda x: x[1], reverse=True)
    cData = []
    for champ, value in champData.items(): cData.append((champ, value['kills'], value['wins']))
    cData.sort(key=lambda x: x[1], reverse=True)


    return render(request, 'index.html', {'data': data[:15], 'cData': cData[:30], 'matches': numMatches, 'match_limit': HOME_MATCH_LIMIT})

def userHome(request):
    if request.method == 'POST':
        username = request.POST['username']
        return HttpResponseRedirect('/user/' + username)
    else:
        return HttpResponseRedirect('/')

def user(request, username):
    if request.method == 'POST':
        username = request.POST['username']
        return user(request, username)

    coll = client.get_database('leagueoflegends').get_collection('matches')
    matches = coll.find(
        {"info.participants" : {"$elemMatch": {"summonerName": {"$regex": username, "$options": 'i' }}}}
    )

    totalKills = 0
    totalDeaths = 0
    totalAssists = 0
    totalCs = 0
    totalWins = 0
    totalTime = 0
    actualName = ''

    specificMatches = []
    for match in matches:
        for participant in match['info']['participants']:
            if participant['summonerName'].lower() == username.lower():
                specificMatches.append(participant)
                #format seconds to mm:ss
                specificMatches[-1]['length'] = str(datetime.utcfromtimestamp(match['info']['gameDuration']).strftime('%M:%S'))
                
                cs = participant['totalMinionsKilled'] + participant['neutralMinionsKilled']
                specificMatches[-1]['cs'] = cs
                specificMatches[-1]['participants'] = match['info']['participants']
                totalCs += cs
                actualName = participant['summonerName']

                totalTime += match['info']['gameDuration']
                totalKills += participant['kills']
                totalDeaths += participant['deaths']
                totalAssists += participant['assists']
                if participant['win']:
                    totalWins += 1

                end = match['info']['gameEndTimestamp']
                end = datetime.utcfromtimestamp(end/1000)
                delta = (datetime.utcnow() - end).days
                if delta == 0:
                    specificMatches[-1]['delta'] = 'Today'
                elif delta == 1:
                    specificMatches[-1]['delta'] = str(delta) + ' day ago'
                else:
                    specificMatches[-1]['delta'] = str(delta) + ' days ago'
                break

    if len(specificMatches) == 0:
        return render(request, 'userNotFound.html', {'username': username})
    winRate = math.floor(totalWins / len(specificMatches) * 100)
    winRate = str(winRate)

    # convert total time from minutes to hours
    hours = math.floor(totalTime / 3600)
    totalTime -= hours * 3600
    totalTime = math.floor(totalTime / 60)
    totalTime = str(hours) + ' hours, ' + str(totalTime) + ' minutes'

    return render(request, 'user.html', {'username': username, 'matches': specificMatches[len(specificMatches)-LIMIT:], 'fullMatches': specificMatches, 'actualName': actualName,
                    'winRate': winRate, 'totalKills': totalKills, 'totalDeaths': totalDeaths, 'totalAssists': totalAssists, 'totalCs': totalCs, 'timePlayed': totalTime})
