#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2016, Ben Fellows <kiwifellows@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: mysql_query
short_description: Query MySQL Database and return results
description:
   - Can run any SELECT, INSERT, UPDATE or DELETE query
   - returns results based on query
   - And returns affected_rows
   
   See: https://github.com/ansible/ansible-modules-extras/issues/980
version_added: "1.9"
options:
TODO
'''
    
import os
import pipes
import stat
import subprocess
import collections

try:
    import MySQLdb
except ImportError:
    mysqldb_found = False
else:
    mysqldb_found = True

# ===========================================
# MySQL module specific support methods.
#

def db_exists(cursor, db):
    res = cursor.execute("SHOW DATABASES LIKE %s", (db.replace("_","\_"),))
    return bool(res)

def query_insert(cursor, query):
    res=cursor.execute(query)
    return res

def query_delete(cursor, query):
    res=cursor.execute(query)
    return res

def query_update(cursor, query):
    res=cursor.execute(query)
    return res

def query_select(cursor, query):
    res=cursor.execute(query)
    rdef = collections.namedtuple('dataset', ' '.join([x[0] for x in cursor.description])) 
    num_fields = len(cursor.description)
    field_names = [i[0] for i in cursor.description]
    columns = cursor.description 
    row_results = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    return row_results, cursor.rowcount, field_names

# ===========================================
# Module execution.
#

def main():
    module = AnsibleModule(
        argument_spec = dict(
            login_user=dict(default=None),
            login_password=dict(default=None),
            login_host=dict(default="localhost"),
            login_port=dict(default=3306, type='int'),
            name=dict(required=True, aliases=['db']),
            query=dict(default=""),
        )
    )
    changed=0
    if not mysqldb_found:
        module.fail_json(msg="the python mysqldb module is required")
        
    db = module.params["name"]
    query= module.params["query"]
    login_port = module.params["login_port"]
    if login_port < 0 or login_port > 65535:
        module.fail_json(msg="login_port must be a valid unix port number (0-65535)")
    login_password = module.params["login_password"]
    login_user = module.params["login_user"]
    login_host = module.params["login_host"]

    connect_to_db = db
    
    try:
        db_connection = MySQLdb.connect(host=login_host, user=login_user, passwd=login_password, db=connect_to_db, port=login_port)
        cursor = db_connection.cursor()
    except Exception as e:
        if "Unknown database" in str(e):
                errno, errstr = e.args
                module.fail_json(msg="ERROR: %s %s" % (errno, errstr))
        else:
            module.fail_json(msg="unable to connect to database, check login_user and login_password are correct or has the credentials. Exception message: %s" % (e))
    
    try:
        
        if(query.upper()[:6]=="SELECT"):
            query_output, rows_affected, rows_def=query_select(cursor, query)
             #This is used to commit any inserts, deletes, updates
            db_connection.commit();
            changed=1
            module.exit_json(changed=changed, result=query_output, rows_affected=rows_affected, allrows=rows_def)
            
        if(query.upper()[:6]=="INSERT"):
                
            insert_result=query_insert(cursor, query)
            db_connection.commit();
            changed=1
            module.exit_json(changed=changed, result=insert_result)
            
        
        if(query.upper()[:6]=="UPDATE"):
            update_result=query_update(cursor, query)
            db_connection.commit();
            changed=1
            module.exit_json(changed=changed, result=update_result)
            
        if(query.upper()[:6]=="DELETE"):
            delete_result=query_delete(cursor, query)
            db_connection.commit();
            changed=1
            module.exit_json(changed=changed, result=delete_result)
        
        
        
    except Exception as e:
        module.fail_json(msg="Unable to run query against database. Exception message is %s" % (e))

    
# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.database import *
if __name__ == '__main__':
    main()
