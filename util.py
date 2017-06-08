import requests, json, os, datetime as dt, sys


json_hdr = {'Content-Type':"application/json"}
  
rest_api='/rest/api/2/'
  
# minutes  
cache_time=120

def log_error(*args):
  with open('error.log','a') as f:
    for arg in args:
      f.write(arg+'\n')

def uncache(instance,issue_key):  
  fname=instance['cache_dir']+'/'+issue_key+'.json'
  print('Deleting',fname,'from cache')
  if os.path.isfile(fname):
    os.remove(fname)
  
def get_issue(instance,issue_key):
  
  fname=instance['cache_dir']+'/'+issue_key+'.json'
  url=instance['url']+rest_api+'issue/'+issue_key
  return get_with_cache(instance,url,fname)

  
def get_with_cache(instance,url,fname):
  if instance['read_from_cache'] == 'yes' and os.path.isfile(fname):
    now=dt.datetime.now()
    ago=now-dt.timedelta(minutes=cache_time)    
    st=os.stat(fname)
    mtime = dt.datetime.fromtimestamp(st.st_mtime)
    if mtime > ago:
      print('Reading',fname,'from cache')
      with open(fname,'r') as f:
        data=json.load(f)
        return data
        
  # re-fetch
  print('Fetching',url,'to',fname)
  r=requests.get(url,auth=(instance['user'],instance['pw']))
  if r.status_code==200:
    data=json.loads(r.text)
    os.makedirs(instance['cache_dir'],exist_ok=True)     
    with open(fname,'w') as f:
      json.dump(data,f,indent=2)
      return data
  else:
    print('Error',fname,r.status_code)
    return None
    

  
def do_post(instance,noun,data):
  url=instance['url']+rest_api+noun
  print('POST',url,'with',json.dumps(data,indent=2))
  r = requests.post(url,auth=(instance['user'],instance['pw']),headers=json_hdr,data=json.dumps(data))
  return handle_status(url,data,r)

def do_put(instance,noun,data):
  url=instance['url']+rest_api+noun
  print('PUT',url,'with',json.dumps(data,indent=2))
  r = requests.put(url,auth=(instance['user'],instance['pw']),headers=json_hdr,data=json.dumps(data))
  return handle_status(url,data,r) 
    
def handle_status(url,data,r):
  if r.status_code == 200 or r.status_code==201 or r.status_code==204:
    print(r.status_code)
    if(r.status_code==200):
      respdata=json.loads(r.text)
      return respdata
    return r.status_code
   
  if r.status_code == 401:
    print('AUTH ERROR')
    print('Your REST request failed with a 401-unauthorized.')
    print('Make sure you have updated the auth.ini file')
    print('with a username and password that are valid')
    print('for the JIRA instance at',url)
    sys.exit(1)
    
  print(r.status_code, r.reason,r.text)
  log_error(url,r.status_code,r.reason,r.text,json.dumps(data,indent=2))
  return False
  
