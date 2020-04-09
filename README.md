# jira_search_replace
Search &amp; Replace via Rest API for JIRA

This script performs search and replace across a set of issues in JIRA via JIRA's REST API.
The jira_search_replace.ini file contains the URL of the JIRA instance, the JQL to specify the set of issues,
issue fields to modify, and the search and replace strings.

If your JIRA instance uses custom fields, the internal field name will differ from the displayed field name. Check the cached JSON file to find the internal field name.

There is a second .ini file, auth.ini, which you will need to edit to supply the username and password which will be used to execute the REST calls. You can also generate an API token from your Atlassian profile Security page and use it in place of the password. Some organizations don't allow basic password authentication, but will allow API tokens. To use a token either set pw in auth.ini with the token or paste it in on the command line when you are prompted for your password.

To install the dependencies, use pip with the requirements.txt file.

$ pip install -r requirements
