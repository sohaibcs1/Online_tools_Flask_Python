from decimal import MAX_PREC
from flask import Flask,redirect,flash,request, render_template,url_for,abort,json,send_from_directory
from pytube import YouTube
from YoutubeTags import videotags
from pytube import YouTube
import urllib.request
from flask_mysqldb import MySQL
import yaml
import re
from flask_recaptcha import ReCaptcha
import whois
from flask_sitemap import Sitemap
from datetime import datetime   
import os,requests
from bs4 import BeautifulSoup

app = Flask(__name__)
recaptcha = ReCaptcha(app=app)
ext = Sitemap(app=app)
currentDate = datetime.now().strftime('%Y-%m-%d')


#config Captcha Start
app.config.update(dict(
    RECAPTCHA_ENABLED = True,
    RECAPTCHA_SITE_KEY = "6LfSdXoeAAAAABaPxOpQYUgEa65slIsw9R8cW20R",
    RECAPTCHA_SECRET_KEY = "6LfSdXoeAAAAAP0F4s5Nf6amsQAj-fcEDYMgdVQW",
))

recaptcha = ReCaptcha()
recaptcha.init_app(app)
app.config['SECRET_KEY'] = 'cscandasdrocoders-edxzalan'

#config Captcha End

# Configure db
db = yaml.load(open('db.yaml'),Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


# from transformers import AutoModel, AutoTokenizer 
# model_name = "facebook/bart-large-cnn" 
# model = AutoModel.from_pretrained(model_name)
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model.save_pretrained("./sumerization")
# tokenizer.save_pretrained("./sumerization")


def ip_details(iip):
        ipcheck=0
        try:
            url="https://ipinfo.io/" + iip
            req=urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data=response.read()
                data=json.loads(data)
        except:
            ipcheck=1
            return ("Network-Problem/Not-Valid-Ip")
        if(ipcheck==0):
            try:
                my_dict = {"IP Address": data['ip'], "City:": data['city']
                , "State:": data['region']
                , "Country:": data['country']
                , "GPS:": data['loc']
                , "ZIP:": data['postal']
                , "ISP:": data['org']
                    }
                return (my_dict)
            except:
                my_dict2 = {"IP Address": "N/A", "City:": "N/A"
                , "State:": "N/A"
                , "Country:": "N/A"
                , "GPS:": "N/A"
                , "ZIP:": "N/A"
                , "ISP:": "N/A"
                    }
                return (my_dict2)

def taghash(keyword):
    params = {'keyword': str(keyword), 'filter': 'random'}
    response=requests.post("https://www.all-hashtag.com//library/contents/ajax_generator.php",params)
    # print(response.status_code)
    res=response.text
    soup = BeautifulSoup(res, "lxml")
    Hashtag=soup.find("div", {"id": "copy-hashtags"})
    moreHashtag = soup.find("div", {"class": "box-content"})
    similarHashtag=soup.find("div", {"id": "copy-hashtags-similar"})
    hash=Hashtag.text
    morehash=moreHashtag.text
    similarhash=similarHashtag.text
    return(hash,morehash,similarhash)

@ext.register_generator
def index():
    # Not needed if you set SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS=True
    yield 'index', {}, currentDate,'daily', 1.0
    yield 'hashtag', {}, currentDate,'daily', 0.7
    yield 'domainLookup', {}, currentDate,'daily', 0.7
    yield 'ipAddressTrackerFree', {}, currentDate,'daily', 0.7
    yield 'youTubeTag', {}, currentDate,'daily', 0.7
    yield 'youtubeDes', {}, currentDate,'daily', 0.7
    yield 'thumbnailDownloader', {}, currentDate,'daily', 0.7
    yield 'contactUs', {}, currentDate,'daily', 0.7

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/hashtag')
def hashtag():
    return render_template('hashtag.html')

@app.route('/contactUs')
def contactUs():
    return render_template('contactUs.html')

@app.route('/domainLookup')
def domainLookup():
    return render_template('domainLookup.html')

@app.route('/ipAddressTrackerFree')
def ipAddressTrackerFree():
    return render_template('ipAddressTrackerFree.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacyPolicy')
def privacyPolicy():
    return render_template('privacyPolicy.html')

@app.route('/thumbnailDownloader')
def thumbnailDownloader():
    return render_template('thumbnailDownloader.html')

@app.route('/youTubeTag')
def youTubeTag():
	return render_template('youTubeTag.html')


@app.route('/youtubeDes')
def youtubeDes():
	return render_template('youtubeDes.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html')

def replace(para):
    row = para.replace(',', '\n')
    return row

def checkIP(Ip):
    regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
    if(re.search(regex, Ip)):
        return 'accept'
    else:
        return 'reject'

@app.route('/ipAddressTrackerFree',methods=['GET','POST'])
def ip():
    if request.method == 'POST':
        ipAddress = request.form['ipAddress']
        if ipAddress == '' or ipAddress==None or checkIP(ipAddress)=='reject':
            return render_template('ipAddressTrackerFree.html')
        else:
            ipDetails = ip_details(ipAddress)
            ip=ipAddress
            state=ipDetails['State:']
            city=ipDetails['City:']
            country= ipDetails['Country:']
            gps= ipDetails['GPS:']
            zip=ipDetails['ZIP:']
            isp=ipDetails['ISP:']
            #Db
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO ip_details(ip,state,city,country,gps,zip,isp) VALUES(%s, %s,%s, %s, %s,%s, %s)",(ip, state,city,country,gps,zip,isp))
            mysql.connection.commit()
            cur.close()
            return render_template('ipAddressTrackerFree.html',ip=ip,state=state,city=city,country=country,gps=gps,zip=zip,isp=isp)

@app.route('/youTubeTag',methods=['GET','POST'])
def sumerizer():
    if request.method == 'POST':
        videoTitle = request.form['videoTitle']
        if videoTitle == '' or videoTitle==None:
            return render_template('youTubeTag.html')
        else:
            findtags = videotags(videoTitle)
            taginList=replace(findtags)
            return render_template('youTubeTag.html',findtags=findtags,taginList=taginList)

@app.route('/domainLookup',methods=['GET','POST'])
def lookUp():
    if request.method == 'POST':
        url = request.form['url']
        if(url =='' or url==None):
            return render_template('domainLookup.html')
        else:
            try:
                res=whois.whois(url)
                domainName=res.domain_name
                registrar=res.registrar
                whois_server=res.whois_server
                referral_url=res.referral_url   
                updated_date=res.updated_date
                expiration_date=res.expiration_date
                creation_date=res.creation_date
                name_servers=res.name_servers
                status=res.status
                emails=res.emails
                dnssec=res.dnssec
                name=res.name
                org=res.org
                address=res.address
                city=res.city
                state=res.state
                zipcode=res.zipcode
                country=res.country
                #Db START
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO domain_lookup(domainName,registrar,whois_server,referral_url,updated_date,expiration_date,creation_date,name_servers,status,emails,dnssec,name,org,address,city,state,zipcode,country) VALUES(%s, %s,%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s, %s,%s,%s, %s,%s)",(str(domainName),str(registrar),str(whois_server),str(referral_url),str(updated_date),str(expiration_date),str(creation_date),str(name_servers),str(status),str(emails),str(dnssec),str(name),str(org),str(address),str(city),str(state),str(zipcode),str(country)))
                mysql.connection.commit()
                cur.close()
                #Db END    
                return render_template('domainLookup.html',domainName=domainName,registrar=registrar,whois_server=whois_server,referral_url=referral_url,updated_date=updated_date,creation_date=creation_date,expiration_date=expiration_date,name_servers=name_servers,status=status,emails=emails,dnssec=dnssec,name=name,org=org,address=address,city=city,state=state,zipcode=zipcode,country=country)
            except:
                flash('Enter Correct Formate!')
                return render_template('domainLookup.html')

@app.route('/youtubeDes',methods=['GET','POST'])
def titleDes(): 
    if request.method == 'POST':
        urrawTxt = request.form['rawtext']
        if urrawTxt == '' or urrawTxt ==None:
            return render_template('youtubeDes.html')
        else:     
            video = YouTube(urrawTxt)
            title=video.title
            Description=video.description
            thumbNail=video.thumbnail_url
            Captions=video.captions      
            return render_template('youtubeDes.html',title=title,Description=Description)

@app.route('/contactUs',methods=['GET','POST'])
def contact(): 
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message=request.form['message']
        if recaptcha.verify():
            flash('Verified successfully')  
            #Db START
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO user_feedback(name,email,message) VALUES(%s, %s,%s)",(name, email,message))
            mysql.connection.commit()
            cur.close()
            #Db END     
            return render_template('contactUs.html',name=name)  
        else:
            flash('Error ReCaptcha')
            return render_template('contactUs.html')

@app.route('/thumbnailDownloader',methods=['GET','POST'])
def thumbtitles(): 
    if request.method == 'POST':
        stext = request.form['stext']
        if stext == '' or stext==None :
            return render_template('thumbnailDownloader.html')
        else:     
            video = YouTube(stext)
            thumbNail=video.thumbnail_url
            return render_template('thumbnailDownloader.html',thumbNail=thumbNail)

@app.route('/hashtag',methods=['GET','POST'])
def tags(): 
    if request.method == 'POST':
        word = request.form['enterword']
        if word == '' or word==None:
            return render_template('hashtag.html')
        else:
            try:
                hashtag1,morehashtag,similarhashtag=taghash(word)
                #Db Start
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO hashtag_details(word,top_hashtag,similar_hashtag,more_hashtag) VALUES(%s, %s,%s, %s)",(word,hashtag1, morehashtag,similarhashtag))
                mysql.connection.commit()
                cur.close()
                #Db End
                return render_template('hashtag.html',hashtag1=hashtag1,morehashtag=morehashtag,similarhashtag=similarhashtag)    
            except:
                flash('Enter Correct Formate!')
                return render_template('hashtag.html')
if __name__ =='__main__':
    app.run()
    # app.run(host='127.0.0.1')
