import json

data = {}
data['hostname'] = []
data['uri'] = []
data['connections'] = []
data['hostname'].append({
    'name': 'Scott',
    'website': 'stackabuse.com',
    'from': 'Nebraska'
})
data['uri'].append({
    'name': 'Larry',
    'website': 'google.com',
    'from': 'Michigan'
})
data['connections'].append({
    'name': 'Tim',
    'website': 'apple.com',
    'from': 'Alabama'
})

with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)