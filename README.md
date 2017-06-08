# jira_search_replace
Search &amp; Replace via Rest API for JIRA

This script performs search and replace across a set of issues in JIRA via JIRA's REST API.
The jira_search_replace.ini file contains the URL of the JIRA instance, the JQL to specify the set of issues, 
issue fields to modify, and the search and replace strings.

There is a second .ini file, auth/auth.ini, which contains the username and password which will be used to execute the REST calls.
