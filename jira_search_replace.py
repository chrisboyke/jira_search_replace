# jira_search_replace.py
# Search and replace text in a set of jira issues via Jira rest API
import re, util, configparser

update_count=0

def main():
  config=configparser.ConfigParser()
  config.read('jira_search_replace.ini')
  config.read('auth/auth.ini')
  
  issues=get_issues(config)
  for issue in issues:
    issue=util.get_issue(config['instance'],issue['key'])
    do_search_replace(issue,config) 

  print('UPDATE COUNT:',update_count)
  #DONE

##################################################################################
# Fetch a list of issues according to the JQL in the INI file
def get_issues(config):  
  post_data={'jql':config['replace']['query'],'maxResults':9999,'fields':['key']}
  data=util.do_post(config['instance'],'search',post_data)
  if data:
    print('COUNT:',len(data['issues']))
    return data['issues']
  else:
    return []

   

def do_search_replace(issue,config):
  fields=config['replace']['fields']
  search=config['replace']['search']
  repl=config['replace']['replace']
  
  new_issue={'fields': {}}
  for field in re.split('\s*,\s*',fields): 
    if field in issue['fields']:
      if field == 'comment':
        handle_comment(issue,config)
      else:
        if type(issue['fields'][field]) == str:
          print('Replacing',search,'in',field,'with',repl)   
          orig_data=issue['fields'][field]
          new_data=orig_data.replace(search,repl)
          if new_data != orig_data:
            new_issue['fields'][field] = new_data
        else:
          print(field,'is of unhandled type',type(issue['fields'][field]),'skipping')
  
  if(len(new_issue['fields'].keys()) == 0):
    print('No changes in issue',issue['key'])
  else:
    result = util.do_put(config['instance'],'issue/'+issue['key'],new_issue)
    handle_result(result,issue,config)
    
        

########################################################
# Handle each comment body update via its own put
def handle_comment(issue,config):
  search=config['replace']['search']
  repl=config['replace']['replace']
  
  for comment in issue['fields']['comment']['comments']:
    orig_body=comment['body']
    new_body=orig_body.replace(search,repl)
    if new_body != orig_body:
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