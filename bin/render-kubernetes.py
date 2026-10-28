"""Print the isolated CarConnect Kubernetes manifests as a JSON list."""
import json
import sys

prefix, tag = sys.argv[1:]
items = []
for name, port, image, extra, memory in [
    ('mongo', 27017, 'mongo:7', {}, '512Mi'),
    ('api', 3030, f'{prefix}-api:{tag}', {'env':[{'name':'MONGO_URL','value':'mongodb://carconnect-mongo:27017/carconnect'}]}, '192Mi'),
    ('sentiment', 5050, f'{prefix}-sentiment:{tag}', {}, '192Mi'),
    ('web', 8000, f'{prefix}-web:{tag}', {'envFrom':[{'secretRef':{'name':'carconnect-settings'}}],
        'env':[{'name':'DJANGO_ALLOWED_HOSTS','value':'*'}, {'name':'BACKEND_URL','value':'http://carconnect-api:3030'},
               {'name':'SENTIMENT_URL','value':'http://carconnect-sentiment:5050'},
               {'name':'DJANGO_DB_PATH','value':'/data/db.sqlite3'},
               {'name':'DJANGO_CSRF_TRUSTED_ORIGINS','value':'https://*.proxy.cognitiveclass.ai,https://*.labs.skills.network'}]}, '256Mi'),
]:
    labels={'app':f'carconnect-{name}','app.kubernetes.io/part-of':'carconnect'}
    container={'name':name,'image':image,'ports':[{'containerPort':port}],
        'resources':{'requests':{'cpu':'50m','memory':'64Mi'},'limits':{'cpu':'500m','memory':memory}}, **extra}
    pod={'containers':[container]}
    if name in ('mongo','web'):
        directory='/data/db' if name=='mongo' else '/data'
        container['volumeMounts']=[{'name':'data','mountPath':directory}]
        pod['volumes']=[{'name':'data','emptyDir':{}}]
    if name!='mongo':
        probe={'httpGet':{'path':'/health/' if name=='web' else '/','port':port},'initialDelaySeconds':15,'periodSeconds':10,'timeoutSeconds':5}
        container['readinessProbe']=probe
    items += [{'apiVersion':'apps/v1','kind':'Deployment','metadata':{'name':f'carconnect-{name}','labels':labels},
        'spec':{'replicas':1,'selector':{'matchLabels':{'app':f'carconnect-{name}'}},'template':{'metadata':{'labels':labels},'spec':pod}}},
        {'apiVersion':'v1','kind':'Service','metadata':{'name':f'carconnect-{name}','labels':labels},
        'spec':{'selector':{'app':f'carconnect-{name}'},'ports':[{'port':port,'targetPort':port}]}}]
print(json.dumps({'apiVersion':'v1','kind':'List','items':items}))
