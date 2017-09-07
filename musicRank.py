# !usr/bin/env python
# encoding:utf-8
import sys
import csv
import requests
import json
import os
import base64
from Crypto.Cipher import AES
reload(sys)
sys.setdefaultencoding('utf8')

def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(text.encode('hex'), 16)**int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)


def createSecretKey(size):
    return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

def getTotalCommentById(musicId):
    url = 'http://music.163.com/weapi/v1/resource/comments/' + str(musicId) + '/?csrf_token='
    headers = {
        'Cookie': 'appver=1.5.0.75771;',
        'Referer': 'http://music.163.com/'
    }
    text = {
        'username': 'email',
        'password': 'password',
        'rememberLogin': 'true'
    }
    modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    nonce = '0CoJUm6Qyw8W8jud'
    pubKey = '010001'
    text = json.dumps(text)
    secKey = createSecretKey(16)
    encText = aesEncrypt(aesEncrypt(text, nonce), secKey)
    encSecKey = rsaEncrypt(secKey, pubKey, modulus)
    data = {
        'params': encText,
        'encSecKey': encSecKey
    }
    try:
        req = requests.post(url, headers=headers, data=data)
        return req.json()['total']
    #pprint(req.json())
    # for content in req.json()['comments']:
    #     print content['content'].encode('utf-8')
    #     print
    except requests.exceptions.ConnectionError:
        return 0
    except Exception:
        return 0

# 歌单id list的生成器
def getPlaylistId_list(keyword):
    url = 'http://music.163.com/api/search/get'
    postData = {'s': keyword,
            'type': 1000,#1000是搜索歌单
            'offset': 0,
            'sub': 'false',
            'limit': 100
                }
   # postData = urllib.urlencode(data)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
               'Cookie': 'appver=2.0.2', 'Referer': 'http://music.163.com'}
    response = requests.post(url, data = postData, headers = headers)

    for playlist in iter(list(response.json()['result']['playlists'])):
        yield playlist['id']


# 歌曲 id list 生成器
def getMusicIdListByPlaylistId(keyword):
    for playlistId in getPlaylistId_list(keyword):
        url = 'http://music.163.com/api/playlist/detail?id=%s' % playlistId
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
            'Cookie': 'appver=2.0.2', 'Referer': 'http://music.163.com'}
        response = requests.get(url, headers=headers)
        musicInfoList = list(response.json()['result']['tracks'])
        for musicInfo in iter(musicInfoList):
            commentIdlist = {}
            commentIdlist[musicInfo['name']] = musicInfo['commentThreadId']
            #commentIdlist.append(musicInfo['commentThreadId'])
            print commentIdlist
            yield  commentIdlist



if __name__ == "__main__":
    keyword = raw_input("input keyword:")
    # playlistId_list = getPlaylistId_list(keyword)
    commentIdlist = getMusicIdListByPlaylistId(keyword)
    commetToalDict = {}
    for musicNameAndCommentId in commentIdlist:
        totalComment = getTotalCommentById(musicNameAndCommentId.values()[0])
        commetToalDict[musicNameAndCommentId.keys()[0].encode('utf-8')] = totalComment
    print commetToalDict
    commetToalDict = sorted(commetToalDict.iteritems(), key=lambda e:e[1], reverse=True)
    with open(r'c:\musicRank.csv', 'wb') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(commetToalDict)






