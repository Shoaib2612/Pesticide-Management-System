from audioop import add
# from crypt import methods
# from crypt import /
# from crypt import methods

from dataclasses import dataclass
import email
from pickletools import read_long1
from random import seed
import re
from flask import *  
from flask import flash
from numpy import result_type
from cassandra_connect import connect
import os
import time
# from wtfloginform import loginform
from flask_session import Session

app = Flask(__name__, static_folder="static")  
app.secret_key = "shoaib2612"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
@app.route("/")
def homepage():
    
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html  ")

@app.route("/userlogin",methods = ['GET','POST'])
def userlogin():
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        user_name=request.cookies.get('user_name')
        # return redirect("/userlogin/userdashboard/{user_name}")
        resp=make_response(redirect(f"/userlogin/userdashboard/{user_name}"))
        return resp
    
        # return render_template('userdashboard.html')

    if request.method=="POST":
        user_name=request.form['user_name']  
        user_password=request.form['user_password'] 
        database = connect()
        database.execute('use "Emp" ')
        data = database.execute("select user_name,user_password from user_login")
        for i in data:
            if user_name==i.user_name and user_password==i.user_password:
                session['user']=user_name
                resp=make_response(redirect(f"/userlogin/userdashboard/{user_name}"))
                resp.set_cookie('user_name',user_name)
                return resp
 
    else:
        return render_template("userlogin.html")
@app.route("/userlogin/userdashboard/<string:name>")
def userdashboard(name):
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        pest = []
        name = request.cookies.get('user_name')
        database = connect()
        database.execute('use "Emp"')
        data = database.execute("select pest_pic,pest_name,pest_details,pest_price,pest_id from pest")
        for i in data:
            pest.append([i.pest_pic,i.pest_name,i.pest_details,i.pest_price,i.pest_id])
        pest=tuple(pest)
        for i in pest:
            print(i)
        
        r  = make_response(render_template("userdashboard.html",pest=pest,name = name))
        return r
    else:
        return redirect("/userlogin")

@app.route("/userregister",methods=['GET','POST'])
def userregister():
    if request.method=='POST':
        user_name = request.form['user_name']
        user_password = request.form['user_password']
        user_confirm_password = request.form['user_confirm_password']
        city = request.form['user_city']
        state = request.form['user_state']
        address = str(request.form['user_address'])
        zipcode = int(request.form['user_zipcode'])
        email= request.form['user_email']

        database = connect()
        database.execute('use "Emp" ')
        data = database.execute("select user_name,email from user_login")
        for i in data:
            if (user_name != i.user_name and email != i.email):
                if user_password==user_confirm_password:
                    database.execute(
                        """
                        INSERT INTO user_login(user_name,address,city,email,state,user_password,zipcode)
                        VALUES(%(user_name)s, %(address)s, %(city)s, %(email)s, %(state)s, %(user_password)s, %(zipcode)s)
                        
                        """,
                        {'user_name':user_name,'address':address,'city':city,'email':email,'state':state,'user_password':user_password,'zipcode':zipcode}
                    )
                    return render_template("user_success_register.html")
                    
                else:
                    return render_template("userregister.html")
            elif (user_name == i.user_name and email == i.email):
                return render_template("userregistererror.html")
            
    else:
        return render_template("userregister.html")

@app.route("/userlogin/userdashboard/<string:name>/<string:pest_id>")
def buynow(name,pest_id):
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        user_name = request.cookies.get('user_name')
        database = connect()
        pest_id=int(pest_id)
        database.execute('use "Emp"')
        pest_details = database.execute("""
        select pest_pic,pest_name,pest_details,pest_price from pest where pest_id=%(pest_id)s
        
        """,
        {'pest_id':pest_id}
        )
        pest=[]
        for i in pest_details:
            pest.append([i.pest_pic,i.pest_name,i.pest_details,i.pest_price])
        pest=tuple(pest)

        user_details = database.execute("""
        select email,address,city,zipcode from user_login where user_name = %(user_name)s
        
        """,
        {'user_name':user_name}
        )
        user=[]
        for j in user_details:
            user.append([j.email,j.address,j.city])
        user=tuple(user)
        return render_template("user_confirm_order.html",user=user,pest=pest,name=user_name,pest_id=pest_id)
    else:
        return redirect("/userlogin")
order_id=0
import random
@app.route("/userlogin/userdashboard/<string:name>/<string:pest_id>/confirm_order")
def confirm_order(name,pest_id):
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        global order_id
        order_id = random.randint(1,10000)
        # order_id=int(order_id)
        database = connect()
        pest_id=int(pest_id)
        database.execute('use "Emp"')
        user_name = request.cookies.get('user_name')
        pest_details = database.execute("""

        select pest_details,pest_name,pest_pic,pest_price from pest where pest_id=%(pest_id)s

        """,
        {'pest_id':pest_id}
        
        )
        pest=[]
        for i in pest_details:
            pest.append([i.pest_details,i.pest_name,i.pest_pic,i.pest_price])
        pest=tuple(pest)
        for i in pest:
            pest_details=i[0]
            pest_name =i[1]
            pest_pic = i[2]
            pest_price = int(i[3])
        user_details = database.execute("""

        select email,address,city,zipcode from user_login where user_name = %(user_name)s

        """,
        {'user_name':user_name}
        )
        user=[]
        for j in user_details:
            user.append([j.email,j.address,j.city,j.zipcode])
        user=tuple(user)
        for j in user:
            email=j[0]
            address=j[1]
            city=j[2]
            zipcode=j[3]
        database.execute("""

        INSERT INTO order_details(order_id,pest_id,pest_details,pest_name,pest_pic,pest_price,user_address,user_email,user_name,zipcode,city)
        VALUES(%(order_id)s,%(pest_id)s,%(pest_details)s,%(pest_name)s,%(pest_pic)s,%(pest_price)s,%(address)s,%(email)s,%(user_name)s,%(zipcode)s,%(city)s)
        
        """,
        {'order_id':order_id,'pest_id':pest_id,'pest_details':pest_details,'pest_name':pest_name,'pest_pic':pest_pic,'pest_price':pest_price,'address':address,'email':email,'user_name':user_name,'zipcode':zipcode,'city':city}
        
        )
        name = request.cookies.get('user_name')
        return render_template("orderconfirm.html",name=name)   
    else:
        return redirect("/userlogin")

@app.route("/userlogin/userdashboard/<string:name>/myorders")
def myorders(name):
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        user_name = request.cookies.get('user_name')
        database = connect()
        database.execute('use "Emp"')
        myorders = database.execute("""

        select pest_pic,pest_name,pest_details,pest_price,pest_id from order_details where
        user_name=%(user_name)s
        
        """,
        {'user_name':user_name}
        
        )
        orders=[]
        for i in myorders:
            orders.append([i.pest_pic,i.pest_name,i.pest_details,i.pest_price,i.pest_id])
        orders=tuple(orders)
        return render_template("myorders.html",orders=orders,name=user_name)
    else:
        return redirect("/userlogin")
@app.route("/userlogin/userdashboard/<string:name>/viewprofile")
def viewprofile(name):
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        user_name=request.cookies.get('user_name')
        database=connect()
        database.execute('use "Emp"')
        user_details = database.execute("""
        select email,address,city,state,zipcode from user_login where user_name = %(user_name)s
        
        """,
        {'user_name': user_name}
        )
        user=[]
        for i in user_details:
            user.append([i.email,i.address,i.city,i.state,i.zipcode])
        user=tuple(user)
        return render_template("user_viewprofile.html",user=user,name=user_name)
    else:
        return redirect("/userlogin")

@app.route("/userlogin/userdashboard/<string:name>/viewprofile/editprofile",methods=['GET','POST'])
def editprofile(name):
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        if request.method=='POST':
            # user_name = request.form['user_name']
            # user_password = request.form['user_password']
            # user_confirm_password = request.form['user_confirm_password']
            name = request.cookies.get('user_name')
            city = request.form['user_city']
            state = request.form['user_state']
            address = str(request.form['user_address'])
            zipcode = int(request.form['user_zipcode'])
            email= request.form['user_email']

            # if user_password==user_confirm_password:
            database = connect()
            database.execute('use "Emp" ')
            database.execute("""
            update user_login set address=%(address)s,city=%(city)s,state=%(state)s,email=%(email)s,zipcode=%(zipcode)s where user_name =%(name)s
            
            """,
            {'address':address,'city':city,'state':state,'email':email,'name':name,'zipcode':zipcode}
            )
            return redirect(f"/userlogin/userdashboard/{name}/viewprofile/editprofile/success")
            

        else:
            name = request.cookies.get('user_name')
            return render_template("user_editprofile.html",name=name)

    else:
        return redirect("/userlogin")

@app.route("/userlogin/userdashboard/<string:name>/viewprofile/editprofile/success")
def user_edit_success(name):
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        name = request.cookies.get('user_name')
        return render_template("user_editsuccess.html",name=name)
    else:
        return redirect("/userlogin")
         
@app.route("/userlogin/userdashboard/<string:name>/viewprofile/editprofile/password",methods=['GET','POST'])
def edit_username_password(name):
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        if request.method=='POST':
            # user_name=request.form['user_name']
            name=request.cookies.get('user_name')
            user_password = request.form['user_password']
            user_confirmpassword = request.form['user_confirmpassword']
            if user_password==user_confirmpassword:
                database = connect()
                database.execute('use "Emp"')
                database.execute("""

                update user_login set user_password=%(user_password)s where user_name=%(name)s

                """,
                {'user_password':user_password,'name':name}


                )
                
                
                return redirect(f"/userlogin/userdashboard/{name}/viewprofile/editprofile/password/success")
            else:
                name = request.cookies.get('user_name')
                return render_template("invalid1.html",name=name)
        else:
            name=request.cookies.get('user_name')
            return render_template("user_usernamepaswordedit.html",name=name)
    else:
        return redirect("/userlogin")

@app.route("/userlogin/userdashboard/<string:name>/viewprofile/editprofile/password/success")
def user_edit_username_success(name):
    if 'user' in session and session['user']==request.cookies.get('user_name'):
        session.pop('user')
        
        return render_template("user_edit_username_success.html")
        
    else:
        return redirect("/userlogin")


                
       


@app.route("/userlogout")
def userlogout():
    session.pop('user')
    return redirect("/")

# --------------------------------------------ADMIN-----------------------------------------------------------------------------------------------

@app.route("/admin",methods=['GET','POST'])
def admin():
    if 'admin' in session and session['admin']==os.environ.get('admin_username'):
        return render_template("admindashboard.html")
    if request.method=="POST":
        admin_name = request.form['name']
        admin_password = request.form['password']
        if admin_name==os.environ.get('admin_username') and admin_password==os.environ.get('admin_password'):
            session['admin']=admin_name
            return redirect("/admin/admindashboard")
    else:
        return render_template('admin.html')
@app.route("/admin/admindashboard")
def admindashboard():
    if 'admin' in session and session['admin']==os.environ.get('admin_username'):
        return render_template("admindashboard.html")
    else:
        return redirect("/admin")
    
@app.route("/admin/admindashboard/adminuserregister")
def adminuserregister():
    if 'admin' in session and session['admin']==os.environ.get('admin_username'):
        database = connect()
        database.execute(' use "Emp" ')
        data = database.execute("select * from user_login")
        data1=[]
        for i in data:
            data1.append([i.user_name,i.address,i.city,i.email,i.state,i.user_password,i.zipcode])
            r = tuple(data1)
        return render_template("adminuserregister.html",r=r)
    else:
        return redirect("/admin")

@app.route("/admin/admindashboard/adminpestadd",methods=['GET','POST'])
def admin_add_pesticide():
    if 'admin' in session and session['admin']==os.environ.get('admin_username'):
        if request.method=='POST':
            pest_id = int(request.form['pest_id'])
            pest_name = request.form['pest_name']
            pest_details = request.form['pest_details']
            pest_price = int(request.form['pest_price'])
            pest_pic = request.form['pest_pic']
            database = connect()
            database.execute('use "Emp"')
            database.execute("""
            INSERT into pest(pest_id,pest_details,pest_name,pest_pic,pest_price) 
            values(%(pest_id)s, %(pest_details)s, %(pest_name)s, %(pest_pic)s , %(pest_price)s) 

            """,
            {'pest_id':pest_id,'pest_details':pest_details,'pest_name':pest_name,'pest_pic':pest_pic,'pest_price':pest_price}
            )
            return render_template("admin_pestadd_success.html")
        else:
            
            return render_template("adminpestadd.html")
    else:
        return redirect("/admin")
@app.route("/admin/admindashboard/adminpestcheck")
def adminpest_check():
    if 'admin' in session and session['admin']==os.environ.get('admin_username'):
        database = connect()
        database.execute('use "Emp"')
        data = database.execute("select pest_id,pest_pic,pest_name,pest_details,pest_price from pest")
        pest=[]
        for i in data:
            pest.append([i.pest_id,i.pest_pic,i.pest_name,i.pest_details,i.pest_price])
        return render_template("adminpestcheck.html",pest=pest)
    else:
        return redirect("/admin")

@app.route("/admin/admindashboard/adminpestcheck/delete/<string:no>")
def pestdelete(no):
    if 'admin' in session and session['admin']==os.environ.get('admin_username'):
        pest_id = int(no)
        database = connect()
        database.execute('use "Emp"')
        database.execute("""

        delete from pest where pest_id=%(pest_id)s
        
        """,
        {'pest_id':pest_id}
        )
        return render_template("admin_pest_delete_success.html")
    else:
        return redirect("/admin")

@app.route("/admin/admindashboard/adminpestcheck/edit/<string:no>",methods=['GET','POST'])
def pestedit(no):
    
    if 'admin' in session and session['admin']==os.environ.get('admin_username'):
        if request.method=='POST':
            pest_id=int(no)
            pest_name = request.form['pest_name']
            pest_details = request.form['pest_details']
            pest_price = int(request.form['pest_price'])
            pest_pic = request.form['pest_pic']
            database = connect()
            database.execute('use "Emp"')
            database.execute("""
            update pest set pest_name=%(pest_name)s,pest_details=%(pest_details)s,pest_price=%(pest_price)s,pest_pic=%(pest_pic)s
            where pest_id=%(pest_id)s

            """,
            {'pest_details':pest_details,'pest_name':pest_name,'pest_pic':pest_pic,'pest_price':pest_price,'pest_id':pest_id}
            )
            resp = make_response(redirect(f"/admin/admindashboard/adminpestcheck/edit/{pest_id}/success"))
            return resp
        else:
            pest_id=int(no)
            return render_template("admin_pest_edit.html",pest_id=pest_id)
    else:
        return redirect("/admin")
@app.route("/admin/admindashboard/adminpestcheck/edit/<string:no>/success")
def edit_success(no):
    if 'admin' in session and session['admin']==os.environ.get('admin_username'):
        pest_id=int(no)
        return render_template("admin_pest_edit_success.html",pest_id=pest_id)
    else:
        return redirect("/admin")


@app.route("/admin/admindashboard/ordercheck")
def ordercheck():
    name = request.cookies.get('user_name')
    database = connect()
    database.execute('use "Emp"')
    order = database.execute("""

    select order_id,pest_id,pest_name,pest_price,user_name,user_address,city,zipcode from  order_details
    
    """
    
    )
    order_details=[]
    for i in order:
        order_details.append([i.order_id,i.pest_id,i.pest_name,i.pest_price,i.user_name,i.user_address,i.city,i.zipcode])
    order_details=tuple(order_details)
    return render_template("admin_orderdetails.html",order_details=order_details)


@app.route("/adminlogout")
def adminlogout():
    session.pop('admin')
    return redirect("/admin")
# @app.route('/login', methods = ['GET', 'POST'])  
# def login():
#     form = loginform()
#     if form.validate_on_submit():
#         if form.name.data == 'admin' and form.password.data == 'admin':
#             flash('login successful')
#             return redirect('index')
#     else:
#         return render_template('login.html', form=form)

if __name__=="__main__":
    app.run(debug=True)