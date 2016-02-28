# ansible-modules
Ansible modules being developed (R&amp;D) that aren't yet ready for prime time use in Ansible Extra's modules or Core.

Current modules:
*mysql_query*
Pre-requisites:
You need the Python MySQL module installed on your OS.

This currently supports the following basic SQl queries:
-SELECT
-INSERT
-UPDATE
-DELETE

Used as follows
'''yaml
- mysql_query:
    login_host: "localhost"
    login_user: "some_user"
    login_password: "password"
    db: "my_db"
    query: "select current_timestamp() as CurrentTime "
  register: query_output
'''
Returning and displaying information.
Once you have the query working you can use "register" to return the output.
*SELECT queries*
The module returns the following values:
- result: returns results as a list
- rows_affected: returns number of rows
- allrows: returns field names (needs to be renamed)

*Other queries*
The module returns the following values:
- result: This will typically be a 1 or 0 depending on number of rows affected.

Example in Ansible task to retrieve the result from a variable called 'query_output'

'''yaml
#Displays  value of a field named 'CurrentTime' in first row
- debug: var=query_output.result[0].CurrentTime
# or set a variable
- set_fact: my_var={{query_output.result[0].CurrentTime}}
# let's say we had a select query that queried a user table and returned lot's of rows...
# This example outputs the value of email addresses for all rows to a text file for example
- shell: "echo '{{ item[0].email }}' >> /myusers.txt"
  with_nested:
    - query_output.result
    - ['email']

'''