# jira_search_replace.py
# Search and replace text in a set of jira issues via Jira rest API
import re, util, configparser
from getpass import getpass

update_count=0
found_count=0

def main():
  config=configparser.ConfigParser()
  config.read('jira_search_replace.ini')
  config.read('auth.ini')
  ## atlassian don't like passwords any more
  # if not config['instance'].get('pw'):
  #   config['instance']['pw'] = getpass("JIRA account password: ")
  
  issues=get_issues(config)
  for issue in issues:
    issue=util.get_issue(config['instance'],issue['key'])
    do_search_replace(issue,config) 

  print('UPDATE COUNT:',update_count)
  print('FOUND COUNT: ', found_count)
  #DONE

##################################################################################
# Fetch a list of issues according to the JQL in the INI file
def get_issues(config):  
  ## this just fetches the list of issues and only grabs the "key" from each issue?
  ## I think you can do a simpler request...
  post_data={'jql':config['replace']['query'],'maxResults':9999,'fields':['key']}
  data=util.do_post(config['instance'],'search',post_data)
  if data:
    print('COUNT:',len(data['issues']))
    print (data['issues'])
    return data['issues']
  else:
    return []

   

def do_search_replace(issue,config):
  fields=config['replace']['fields']
  search=config['replace']['search']
  repl=config['replace']['replace']
  global found_count

  new_issue={'fields': {}}
  for field in re.split('\s*,\s*',fields): 
    #print("looking for field named "+field)
    if field in issue['fields']:
      #print ("found field named "+field)
      if field == 'comment':
        handle_comment(issue,config)
      else:
        if type(issue['fields'][field]) == str:
          orig_data=issue['fields'][field]
          #new_data=orig_data.replace(search,repl)
          found_match = re.search(search,orig_data)
          if found_match:
            print ('found ',found_match.group()) # add where you found it!
            print ('in issue : ',issue['key'])
            new_data = re.sub(search, repl, orig_data)          
            new_issue['fields'][field] = new_data
            ## uncomment these 2 lines to enable actually saving new value to issues
            result = util.do_put(config['instance'],'issue/'+issue['key'],new_issue)
            handle_result(result,issue,config)
            found_count += 1 
        else:
          #print ('problem handling issue ',issue['key'])
          print(issue['key'],' ',field,'is of unhandled type',type(issue['fields'][field]),'skipping')
   
        

########################################################
# Handle each comment body update via its own put
def handle_comment(issue,config):
  search=config['replace']['search']
  repl=config['replace']['replace']
  
  for comment in issue['fields']['comment']['comments']:
    orig_body=comment['body']
    #new_body=orig_body.replace(search,repl)
    found_match = re.search(search,orig_body)
    if found_match:
      new_body=re.sub(search, repl, orig_body)
      print('found ',found_match.group(),' in a comment on issue ',issue['key'])
      ## uncomment these to save new values
      id=comment['id']
      result=util.do_put(config['instance'],'issue/'+issue['key']+'/comment/'+id,{'body':new_body})
      handle_result(result,issue,config)

def handle_result(result,issue,config):
  global update_count
  if result:
    update_count += 1
    print('OK')
    util.uncache(config['instance'],issue['key'])
  else:
    print('ERROR')

main()