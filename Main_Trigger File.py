from flask import Flask,render_template,request
import boto3
# import sqlite3
import pymysql as py
from werkzeug.utils import secure_filename
import json

# ACCESS_KEY="IAM ACCESS"
# SECRET_KEY="IAM SECRETKEY"
# AWS_REGION="us-east-1"

dbhost='db1.ckggf7ifzj7k.us-east-1.rds.amazonaws.com'

snsclient=boto3.client('sns',
                            aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY,
                            region_name=AWS_REGION)



lambdaclient=boto3.client('lambda',
                            aws_access_key_id=ACCESS_KEY,
                            aws_secret_access_key=SECRET_KEY,
                            region_name=AWS_REGION)


logname=[]
app=Flask(__name__)

# @app.route('/')
# def index():
#     # form1= request.form
    
#         return render_template('file.html')


@app.route('/')
def index():
    return render_template('log.html')




@app.route('/SIGNIN', methods=['POST','GET'])
def signin():
    form1= request.form
    name =form1['logname']
    slot = form1['logpwd']
    logname.append(name)
    try: 
        conn=py.connect(host=dbhost,user='admin',password='12345678')
        cursor = conn.cursor()
        cursor.execute("USE  GIRI")
        print("first chk")
        cursor.execute('SELECT PASSWORD FROM LOGIN WHERE USERNAME=%s', name) 
        pwd  = cursor.fetchone()
        dbpwd=pwd[0]
        view_table='''select * from LOGIN '''
        cursor.execute(view_table)
        print(cursor.fetchall())

        conn.close()

        if slot==dbpwd:
            return render_template("file.html")
        else:
            return "Failure Check Details" 
    except Exception as e:

              return  ("Exeception occured:{}".format(e))
                
      
    # finally:
    #         return "Finall"
    #         con.close()




@app.route('/SIGNUP', methods=['POST','GET'])
def signup():
    form2= request.form
    name1 =form2['regname']
    slot1 = form2['regpwd']


    print(name1 + slot1)

    try:
        conn=py.connect(host=dbhost,user='admin',password='12345678')
        cursor = conn.cursor()
        print(cursor)

        # data=cursor.execute("select version()")
        # print(data)
        # d1=cursor.fetchAll()
        # print(d1)
        cursor.execute("CREATE DATABASE IF NOT EXISTS GIRI")
        cursor.connection.commit()
        cursor.execute("USE  GIRI")
      
        create_table='''CREATE TABLE IF NOT EXISTS LOGIN (
                  ID INT not null auto_increment,
                  USERNAME  TEXT,
                  PASSWORD TEXT,
                  primary key(id)
                )'''

        cursor.execute(create_table)
        conn.commit()
        print('Create done !!')
        # insert_table='''INSERT INTO LOGIN (USERNAME,PASSWORD) values (name1,slot1)'''
        # insert_table='''INSERT INTO LOGIN (USERNAME,PASSWORD) VALUES (?, ?), (name1,slot1))'''

        # cursor.execute(insert_table)
        cursor.execute('INSERT INTO LOGIN(USERNAME,PASSWORD) VALUES (%s,%s)',(name1,slot1) )
        conn.commit()
        view_table='''select * from LOGIN '''
        cursor.execute(view_table)
        print(cursor.fetchall())
        return "Success"
        conn.close()  

    except Exception as e:
        return  ("Exeception occured:{}".format(e))
        conn.close()  



@app.route('/Results', methods=['POST','GET'])
def Results():
        form1= request.form
        name =request.files['myfile']
        # mail1 = form1['comment']
        mail = form1['email1']
        mail2 = form1['email2']
        mail3 = form1['email3']
        mail4 = form1['email4']
        mail5 = form1['email5']
        mails=[]
        if(len(mail)>0):
            mails.append(mail)

        if(len(mail2)>0):
            mails.append(mail2)

        if(len(mail3)>0):
            mails.append(mail3)

        if(len(mail4)>0):
            mails.append(mail4) 

        if(len(mail5)>0):
            mails.append(mail5)       
        print(mails)    
        fname=secure_filename(name.filename)
        sigusr=logname[-1]
        dbentry=''.join(mails)
        print(sigusr,dbentry)
        ACCESS_ID='AWS ROOT KEY'
        ACCESS_KEY='AWS ACCESS KEY'
        # try:
        if request.method=='POST':
                bucket=boto3.client('s3',aws_access_key_id=ACCESS_ID,
                                         aws_secret_access_key= ACCESS_KEY)
                
                bucket.upload_fileobj(name,'mallena',fname)
                # bucket.upload_file(mail1,'mallena',mail1)
                # bucket.download_file('mallena','SampleUpload.txt','Download_S3.txt')
                print("Inside Boto")
                msg1='* File Uploaded in S3 Bucket \n'
                conn=py.connect(host=dbhost,user='admin',password='12345678')
                cursor = conn.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS GIRI")
                cursor.connection.commit()
                cursor.execute("USE  GIRI")
                # del_table='''DROP TABLE IF EXISTS USER'''

                # cursor.execute(del_table)
                # conn.commit()

                create_table='''CREATE TABLE IF NOT EXISTS USER (
                        ID INT not null auto_increment,
                        USERNAME  TEXT,
                        FILENAME TEXT,
                        MAIL TEXT,
                        primary key(id)
                        )'''

                cursor.execute(create_table)
                conn.commit()
                print('Create done !!')
                cursor.execute('INSERT INTO USER(USERNAME,FILENAME,MAIL) VALUES (%s,%s,%s)',(sigusr,fname,dbentry))
                conn.commit()
                view_table='''select * from USER '''
                cursor.execute(view_table)
                print(cursor.fetchall())

                topic=snsclient.create_topic(Name="VsCode_test")
                print(topic)
                arn=topic['TopicArn']
                proto='email'
                for i in mails:
                    print(i)
                    End=i
                    subscribe=snsclient.subscribe(
                                    TopicArn=arn,
                                    Protocol=proto,
                                    Endpoint=End,
                                    ReturnSubscriptionArn=True)['SubscriptionArn']
                    msg2='* Subscribed to Sns \n' 
                    url = bucket.generate_presigned_url('get_object', 
                                    Params={'Bucket': 'mallena', 'Key': fname},
                                    ExpiresIn=3600)               

                    payload={"email":i,"arn":"arn:aws:sns:us-east-1:361226060154:VsCode_test","URL":url,"LOGGER":sigusr}
                    lambdaclient.invoke(
                                    FunctionName='Sample',
                                    InvocationType='Event',
                                    Payload=json.dumps(payload)
                                    )  
                    msg3='* Mail sent please verify'                                      

                return render_template('file.html',msg=msg1+msg2+msg3)

        # except:
        #     return render_template('file.html',msg='Fail')

if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)        