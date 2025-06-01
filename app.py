from flask import Flask,request,jsonify
from google import genai
import requests
import sqlite3
import http.client
import psycopg2
import json
from flask_cors import CORS 
app = Flask(__name__)
CORS(app)
conn =psycopg2.connect(
        user='postgres.vkeghbowcwxjvwtqfrta',
        password='QwertyPass#1',
        host="aws-0-us-east-2.pooler.supabase.com",
        port='6543',
        dbname='postgres'
    )
cur = conn.cursor()
@app.route("/getbookmarksviasearch",methods=['GET','POST'])
def hello_world():
    a=request.get_json()
    print(a)
    if a['Lot']=="":
        query = "select * from bookmarks"
    else:
        query = "select distinct a.* from bookmarks as a join urllot as b on a.url = b.url join Lots as c on b.lotid = c.id and c.name = '"+a['Lot']+"'"
    cur.execute(query)
    res = cur.fetchall()
    print(res)
    web=[]
    if a["description"]!="":
        for i in res:
            prompt = "Can you tell me if the following url:"+i[1]+"Fits the following description?. Here goes the description:"+a["description"]+".just give me the answer in the following format:yes/no,no need of any other explanations.Also dont include any markup elements,just a yes/no."
            client = genai.Client(api_key="AIzaSyAtI4yLa-bZtGu5XRm6Tyxy9Jtphl8uNOE")
            response = client.models.generate_content(
            model="gemini-1.5-flash", contents=prompt
            )
            flag=response.text
            print(flag)
            if 'yes' in flag:
                a1={"url":i[1],"icon":i[2],"Thumbnail":i[3]}
                web.append(a1)
        a2={"result":"returned"}
        print(web)
    else:
        for i in res:
            #if i[4]==a['Lot'] or a['Lot']=='':
            a1={"url":i[1],"icon":i[2],"Thumbnail":i[3]}
            web.append(a1)
    print('Hello',web)
    return jsonify(web)
@app.route('/generatebookmark',methods=["GET","POST"])
def fetchurltags():
    a=request.get_json()
    # conn = http.client.HTTPSConnection("ai-image-generator14.p.rapidapi.com")
    prompt="Provide me with appropriate description for this website.Here is the url:"+a["url"]+"Just provide me with just the description,no need of any other explanation."
    client = genai.Client(api_key="AIzaSyAtI4yLa-bZtGu5XRm6Tyxy9Jtphl8uNOE")
    response = client.models.generate_content(
    model="gemini-1.5-flash", contents=prompt
    )
    
    g=requests.get("https://favicone.com/"+a["url"]+"?json")._content
    # h1=jsonify(g)
    # print("Hello",g[2],b'ILO')

# Execute a query
    query = "select max(id) from bookmarks"
    cur.execute(query)
    id = cur.fetchone()
    print(id)
    try:
        id=int(id[0])
    except:
        id=0
    id+=1
    screenshot = requests.get('https://api.screenshotmachine.com?key=a76adc&url='+a["url"]+'&dimension=1024x768')
    #print(screenshot.text)
    query = "insert into bookmarks values("+str(id)+",'"+a["url"]+"','"+a["icon"]+"','"+screenshot.text+"')" 
    cur.execute(query)
    cur.execute("COMMIT")
    if True:
        id=0
        query = "select max(id) from tags"
        cur.execute(query)
        id = cur.fetchone()
        #print(id)
        try:
            id = int(id[0])
        except:
            id=0
        id+=1
        tags = a["tags"]
        #print(tags)
        for i in tags:
            query = "insert into Tags values("+str(id)+",'"+i+"','"+a["url"]+"')"
            cur.execute(query)
            cur.execute("COMMIT")
            id+=1
    if True:
        id=0
        query = "select max(id) from urllot"
        cur.execute(query)
        id = cur.fetchone()
        #print(id)
        try:
            id = int(id[0])
        except:
            id=0
        id+=1
        lots = a["Lot"]
        
        #print(tags)
        for i in lots:
            query = "select id from Lots where name = '"+i+"'"
            cur.execute(query)
            lotid = cur.fetchone()
            try:
                query = "insert into urlLot values("+str(id)+",'"+a["url"]+"','"+str(lotid[0])+"')"
                cur.execute(query)
                cur.execute("COMMIT")
            except:
                print("No Lot available with given name")
            id+=1
    a2={"result":response.text,"icon":"abc"}
    return jsonify(a2)
@app.route('/addtags',methods=["GET","POST"])
def addtag():
    id=0
    query = "select max(id) from tags"
    cur.execute(query)
    id = cur.fetchone()
    print(id)
    try:
        id = int(id[0])
    except:
        id=0
    id+=1
    tags = a["tags"]
    print(tags)
    for i in tags:
        query = "insert into Tags values("+str(id)+",'"+i+"','"+a["url"]+"')"
        cur.execute(query)
        cur.execute("COMMIT")
        id+=1
@app.route('/createlot',methods=['GET','POST'])
def createLot():
    a=request.get_json()
    id=0
    query = "select max(id) from Lots"
    cur.execute(query)
    id = cur.fetchone()
    print(id)
    try:
        id = int(id[0])
    except:
        id=0
    id+=1
    query = "insert into Lots values("+str(id)+",'"+a["Lot"]+"')"
    cur.execute(query)
    cur.execute("COMMIT")
    a1={'result':'success'}
    return jsonify(a1)

@app.route('/fetchlots',methods=['GET','POST'])
def fetchlots():
    query = "select * from Lots"
    cur.execute(query)
    res1 = cur.fetchall()
    a=[]
    for i in res1:
        a.append({'id':i[0],'name':i[1]})
    return jsonify(a)
@app.route('/editlot',methods=['GET','POST'])
def editlot():
    req = request.get_json()
    query = "update lots set name = '"+req['name']+"' where id = "+str(req['id'])+""
    cur.execute(query)
    cur.execute('COMMIT')
    return jsonify({'Result':"Success"})