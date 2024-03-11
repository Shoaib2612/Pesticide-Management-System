database.execute('use "Emp" ')
            database.execute("""
            update user_login set address=%(address)s,city=%(city)s,state=%(state)s,email=%(email)s,zipcode=%(zipcode)s where user_name =%(name)s
            
            """,
            {'address':address,'city':city,'state':state,'email':email,'name':name,'zipcode':zipcode}
            )