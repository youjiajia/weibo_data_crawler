#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   jiajia you
#   E-mail  :   hi_youjiajia@163.com
#   Date    :   16/04/18 14:54:57
#   Desc    :
#

import pymongo,time, re, os, sys, datetime,json,logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from pymongo import MongoClient
from gevent import monkey; monkey.patch_socket()
import gevent
from multiprocessing import Pool
# client=MongoClient('localhost',27017)
# db=client.weibo
# collection=db.weibo
# _id=collection.find().sort("_id",pymongo.DESCENDING).limit(1)[0]['_id']

logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)s %(filename)s[line:%(lineno)d]%(levelname)s%(message)s',
    filename='./log/getuser.log',
    filemode='a'
)
def LoginWeibo(username, password,driver):
    """
    该函数用来登陆微博，输入用户名密码和浏览器，会进行登陆并验证，成功返回１
    """
    try:
        print "准备登陆weibo网站..."
        # 先调用无界面浏览器PhantonJS或者Firefox
        driver.get("http://www.weibo.com")
        # print 'ready'
        time.sleep(10)
        try:
            elem_changelogin = driver.find_element_by_xpath("//div[@class='tab clearfix']/a[@action-data='type=normal']")
        except:
            driver.get("http://www.weibo.com")
            time.sleep(10)
            elem_changelogin = driver.find_element_by_xpath("//div[@class='tab clearfix']/a[@action-data='type=normal']")
        elem_changelogin.click()
        elem_user = driver.find_element_by_name("username")
        elem_user.click()
        elem_user.send_keys(username)
        elem_pwd = driver.find_element_by_name("password")
        elem_pwd.click()
        elem_pwd.send_keys(password)
        elem_sub = driver.find_element_by_xpath("//a[@class='W_btn_a btn_40px']/span")
        elem_sub.click()
        time.sleep(10)
        try:
            driver.get("http://www.weibo.com/u/3936897693?is_all=1")
            elem_fensi = driver.find_element_by_xpath('//span[text()="粉丝"]')
        except:
            driver.get("http://www.weibo.com/u/3936897693?is_all=1")
            elem_fensi = driver.find_element_by_xpath('//span[text()="粉丝"]')
        elem_fensi.click()
        try:
            elem_changelogin = driver.find_element_by_xpath("//div[@class='tab clearfix']/a[@action-data='type=normal']")
        except Exception,e:
            print '登陆成功'
            return 1
        # print '登陆失败'
        return None
    except NoSuchElementException,e:
        print 'nosuchelement'
        return None
    except Exception,e:
        logging.error('登陆失败，错误原因为{0}'.format(e))
        print 'error:{0}'.format(e)
        return None
def geturl(userid,driver):
    """
    根据用户ｕｒｌ获取到粉丝和关注的ｕｒｌ
    """
    try:
        url = 'http://weibo.com/{0}?is_all=1'.format(userid)
        driver.implicitly_wait(10)
        driver.get(url)
        time.sleep(2)
        driver.get(url)
        try:
            elem_fensi = driver.find_element_by_xpath('//div[@class="WB_innerwrap"]//a[contains(@href,"weibo.com")]').get_attribute('href')
        except:
            driver.get(url)
            elem_fensi = driver.find_element_by_xpath('//div[@class="WB_innerwrap"]//a[contains(@href,"weibo.com")]').get_attribute('href')
        elem_guanzhu = elem_fensi.split('#')[0]
        elem_fensi = elem_guanzhu
        elem_guanzhu += '&relate=fans'
        return elem_fensi,elem_guanzhu
    except Exception,e:
        logging.error('获取用户{0}的关注和粉丝url，错误原因为{1}'.format(userid,e))
        print '页面{0}获取粉丝url'.format(url)
        print e
        return None,None
def getpage(url,driver):
    """
    获取该粉丝或关注一共多少页
    """
    try:
        driver.implicitly_wait(10)
        driver.get(url)
        try:
            nextpage = driver.find_elements_by_xpath('//a[@class="page S_txt1"]')
        except:
            driver.get(url)
            nextpage = driver.find_elements_by_xpath('//a[@class="page S_txt1"]')
        nexturl = nextpage[-1].text
        pageurl = nextpage[-1].get_attribute('href')
        return int(nexturl),pageurl
    except Exception, e:
        logging.error('获取{0}该url一共多少关注和粉丝失败，错误原因为{1}'.format(url,e))
        return 1,url
def getuser(fauser,fakey,url,driver):
    """
    获取该粉丝或关注页面所有用户，并判断该用户是否已经存入关注或粉丝列表中
    如果不存在则加入，然后判读用户是否存在于数据库中，如果不存在，则添加进去。
    """
    client=MongoClient('localhost',27017)
    db=client.weibo
    collection=db.weibo
    _id=collection.find().sort("_id",pymongo.DESCENDING).limit(1)[0]['_id']
    if 'u/' in fauser:
        fauserinfo=collection.find_one({"userid":fauser[2:]})[fakey]
        useridinfolist=[]
        domaininfolist=[]
        for oneinfo in fauserinfo:
            useridinfolist.append(oneinfo['userid'])
            domaininfolist.append(oneinfo['domain'])
    else:
        fauserinfo=collection.find_one({"domain":fauser})[fakey]
        useridinfolist=[]
        domaininfolist=[]
        for oneinfo in fauserinfo:
            useridinfolist.append(oneinfo['userid'])
            domaininfolist.append(oneinfo['domain'])
    try:
        driver.implicitly_wait(10)
        try:
            driver.get(url)
            users = driver.find_elements_by_xpath('//div[contains(@class,"info_name")]/a[contains(@href,"refer_flag")]')
            foucusbys = driver.find_elements_by_xpath('//a[@class="from"]')
        except:
            driver.get(url)
            users = driver.find_elements_by_xpath('//div[contains(@class,"info_name")]/a[contains(@href,"refer_flag")]')
            foucusbys = driver.find_elements_by_xpath('//a[@class="from"]')
        foucusnum=0
        insertuserlist=[]
        for user in users:
            try:
                url=user.get_attribute('href')
                if 'refer_flag' in url:
                    focusby=foucusbys[foucusnum].text
                    foucusnum += 1
                    user=url.split('?refer_flag')[0].split('weibo.com/')[1]
                    if 'u/' in user:
                        if user[2:] not in useridinfolist:
                            fauserinfo.append({"userid":user[2:],"domain":"","focusby":focusby})
                        if collection.find_one({"userid":user[2:]})==None:
                            _id += 1
                            insertuserlist.append({"_id":_id,"userid":user[2:],"name":"","sex":"","level":"","certification":"","area":"","school":"","birthday":"","introduction":"","domain":"","focusnum":"","focus":[],"fansnum":"","fans":[],"blogsnum":"","blogs":[]})
                    else:
                        if user not in domaininfolist:
                            fauserinfo.append({"userid":"","domain":user,"focusby":focusby})
                        if collection.find_one({"domain":user})==None:
                            _id += 1
                            insertuserlist.append({"_id":_id,"userid":"","name":"","sex":"","level":"","certification":"","area":"","school":"","birthday":"","introduction":"","domain":user,"focusnum":"","focus":[],"fansnum":"","fans":[],"blogsnum":"","blogs":[]})
            except:
                continue
        if len(insertuserlist) != 0:
            collection.insert(insertuserlist)
        if 'u/' in fauser:
            collection.update({"userid":fauser[2:]},{"$set":{fakey:fauserinfo}})
        else:
            collection.update({"domain":fauser},{"$set":{fakey:fauserinfo}})
    except Exception, e:
        logging.error('获取该用户所有粉丝和关注列表错误，url为{0}用户为{1}'.format(url,fauser))
        print '获取用户失败'
        print '错误为{0}'.format(e)
def getrelation(userid,driver):
    """
    获取该用户所有页面的粉丝和关注，并将其加入到数据库中
    """
    client=MongoClient('localhost',27017)
    db=client.weibo
    collection=db.weibo
    _id=collection.find().sort("_id",pymongo.DESCENDING).limit(1)[0]['_id']
    if 'u/' in userid:
        if collection.find_one({"userid":userid[2:]})==None:
            _id += 1
            collection.insert({"_id":_id,"userid":userid[2:],"domain":"","userinfo":{},"focusnum":"","focus":[],"fansnum":"","fans":[],"blogsnum":"","blogs":[]})
    else:
        if collection.find_one({"domain":userid})==None:
            _id += 1
            collection.insert({"_id":_id,"userid":"","domain":userid,"userinfo":{},"focusnum":"","focus":[],"fansnum":"","fans":[],"blogsnum":"","blogs":[]})
    fans,guanzhu=geturl(userid,driver)
    if guanzhu:
        userkey="focus"
        fanspage,fanspageurl=getpage(fans,driver)
        if fanspage == 1:
            getuser(userid,userkey,fanspageurl,driver)
        else:
            for fanpage in xrange(1,(fanspage if fanspage<5 else 5)+1):
                time.sleep(2)
                fanurl=fanspageurl.replace("page={0}".format(fanspage),"page={0}".format(fanpage))
                getuser(userid,userkey,fanurl,driver)
        guanzhupage,guanzhuurl=getpage(guanzhu,driver)
        userkey="fans"
        if guanzhupage == 1:
            getuser(userid,userkey,guanzhuurl,driver)
        else:
            for onepage in xrange(1,(guanzhupage if guanzhupage<5 else 5)+1):
                time.sleep(2)
                onepageurl = guanzhuurl.replace("page={0}".format(guanzhupage),"page={0}".format(onepage))
                getuser(userid,userkey,onepageurl,driver)

def getuserinfo(userid,driver):
    """
    获取该用户微博信息，并获取到该用户微博总页数
    """
    try:
        url = 'http://weibo.com/{0}?is_all=1'.format(userid)
        driver.get(url)
        userinfo={}
        userotherinfo={}
        try:
            userinfo['certification']=driver.find_element_by_xpath("//p[@class='info']").text.encode('utf-8')
            userinfo['certification']="未认证" if userinfo['certification']=='' else userinfo['certification']
        except:
            userinfo['certification']="未认证"
        usernuminfo=driver.find_elements_by_xpath("//strong[contains(@class,'W_f')]")
        userotherinfo['focusnum']=usernuminfo[0].text.encode('utf-8')
        userotherinfo['fansnum']=usernuminfo[1].text.encode('utf-8')
        userotherinfo['weibonum']=usernuminfo[2].text.encode('utf-8')
        userotherinfo['weibopages']='1'
        i=0
        js="var q=document.documentElement.scrollTop=10000000000"
        while i<3:
            driver.execute_script(js)
            try:
                tryagainbut=driver.find_element_by_link_text("点击重新载入")
                tryagainbut.click()
                time.sleep(3)
            except:
                driver.execute_script(js)
                time.sleep(3)
            finally:
                pages=driver.find_elements_by_xpath("//div[@class='layer_menu_list W_scroll']/ul/li")
                if len(pages)>0:
                    userotherinfo['weibopages']=len(pages)
                    break
                i+=1
        userinfoclick=driver.find_element_by_xpath("//a[@class='WB_cardmore S_txt1 S_line1 clearfix']")
        userinfoclick.click()
        time.sleep(2)
        userinfo['等级']=driver.find_element_by_xpath("//p[@class='level_info']/span[@class='info'][1]/span[@class='S_txt1']").text.encode('utf-8')
        userbaseinfos=driver.find_elements_by_xpath("//li[@class='li_1 clearfix']")
        userotherinfo['domain']=''
        for userbaseinfo in userbaseinfos:
            userbaseinfo=userbaseinfo.text.encode('utf-8').split("：\n")
            userbaseinfoname=userbaseinfo[0]
            userbaseinfodata=userbaseinfo[1]
            if userbaseinfoname != '个性域名':
                userinfo[userbaseinfoname]=userbaseinfodata
            else:
                userotherinfo['domain']=userbaseinfodata.split('weibo.com/')[1]
        userotherinfo['userinfo']=userinfo
        return userotherinfo
    except Exception,e:
        logging.error('用户{0}获取基本信息失败错误原因为{1}'.format(userid,e))
        print "获取用户{0}的基本信息出错".format(userid)
        print e
        return None
def getweibo(userid,page,driver):
    """
    该函数接收浏览器，用户id，用户微博总页数来获取该用户所有的微博
    """
    try:
        page=1
        URL='http://weibo.com/{0}?is_all=1&page='.format(userid)
        js="var q=document.documentElement.scrollTop=10000000000"
        for onepage in xrange(1,int(page)+1):
            url = URL + str(onepage)
            driver.get(url)
            i=0
            while i<3:
                i+=1
                driver.execute_script(js)
                try:
                    tryagainbut=driver.find_element_by_link_text("点击重新载入")
                    tryagainbut.click()
                except:
                    driver.execute_script(js)
                finally:
                    pages=driver.find_elements_by_xpath("//div[@class='layer_menu_list W_scroll']/ul/li")
                    if len(pages)>0:
                        break
                    driver.get(url)
        allweibolen=len(driver.find_elements_by_xpath('//div[contains(@class,"WB_feed_detail")]'))
        otherpattern=re.compile(r'\n|\s',re.S)
        numpattern=re.compile(r'\d+',re.S)
        weibolist=[]
        for i in xrange(1,allweibolen+1):
            try:
                oneweibo={}
                oneweibo["context"]=driver.find_element_by_xpath('//div[contains(@class,"WB_cardwrap WB_feed_type S_bg2")][{0}]/div[contains(@class,"WB_feed_detail")]/div[contains(@class,"WB_detail")]/div[contains(@class,"WB_text")]'.format(i)).text
                try:
                    oneweibo["forward"]=driver.find_element_by_xpath('//div[contains(@class,"WB_cardwrap WB_feed_type S_bg2")][{0}]/div[contains(@class,"WB_feed_detail")]/div[contains(@class,"WB_detail")]/div[contains(@class,"WB_feed_expand")]'.format(i)).text
                except:
                    oneweibo["forward"]=''
                oneweibo["weibotime"]=driver.find_element_by_xpath('//div[contains(@class,"WB_cardwrap WB_feed_type S_bg2")][{0}]/div[contains(@class,"WB_feed_detail")]/div[contains(@class,"WB_detail")]/div[contains(@class,"WB_from")]/a[1]'.format(i)).get_attribute("title")
                try:
                    oneweibo["weibofrom"]=driver.find_element_by_xpath('//div[contains(@class,"WB_cardwrap WB_feed_type S_bg2")][{0}]/div[contains(@class,"WB_feed_detail")]/div[contains(@class,"WB_detail")]/div[contains(@class,"WB_from")]/a[2]'.format(i)).text
                except:
                    oneweibo["weibofrom"]=''
                comments=driver.find_elements_by_xpath('//div[contains(@class,"WB_cardwrap WB_feed_type S_bg2")][{0}]/div[contains(@class,"WB_feed_handle")]//li/a/span[1]'.format(i))
                forwardnumlist=re.findall(numpattern,comments[1].text)
                oneweibo["forwardnum"]=0
                if len(forwardnumlist)>0:
                    oneweibo["forwardnum"]=forwardnumlist[0]
                commentnumlist=re.findall(numpattern,comments[2].text)
                oneweibo["commentnum"]=0
                if len(commentnumlist)>0:
                    oneweibo["commentnum"]=commentnumlist[0]
                zannumlist=re.findall(numpattern,comments[3].text)
                oneweibo["zannum"]=0
                if len(zannumlist)>0:
                    oneweibo["zannum"]=zannumlist[0]
                weibolist.append(oneweibo)
            except:
                continue
        return weibolist
    except Exception,e:
        logging.error('用户{0}微博第{1}页面错误原因为{2}'.format(userid,page,e))
        return None

def getoneaccount(userid,driver):
    getrelation(userid,driver)
    userinfo=getuserinfo(userid,driver)
    if userinfo!=None:
        # print json.dumps(userinfo,ensure_ascii=False)
        pagenums=int(userinfo['weibopages'])
        allweibo=[]
        for onepage in xrange(1,pagenums+1):
            onepageweibo=getweibo(userid,str(onepage),driver)
            if onepageweibo != None:
                for var in onepageweibo:
                    allweibo.append(onepageweibo)
        if 'u/' in userid:
            user=collection.update({"userid":userid[2:]},{"$set":{"domain":userinfo['domain']
                                                                ,"focusnum":userinfo['focusnum']
                                                                ,"fansnum":userinfo['fansnum']
                                                                ,"blogsnum":userinfo['weibonum']
                                                                ,"userinfo":userinfo['userinfo']
                                                                ,"blogs":allweibo}})
        else:
            user=collection.update({"domain":userid},{"$set":{"domain":userinfo['domain']
                                                                ,"focusnum":userinfo['focusnum']
                                                                ,"fansnum":userinfo['fansnum']
                                                                ,"blogsnum":userinfo['weibonum']
                                                                ,"userinfo":userinfo['userinfo']
                                                                ,"blogs":allweibo}})
def main(username,password,userid,start,end):
    """
     主函数，输入微博用户，用户名密码，开始获取用户的域名或者id
     首先检查输入的用户是否存在，如果不存在，则创建一个
     由于微博用户主页可以为weibo.com/域名 或者为 weibo.com/u/用户id
     所以mongodb中存储的用户有id 和　domain俩个字段，二者存在其一即可
    """
    starttime=datetime.datetime.now()
    result = None
    while result == None:
        # 先调用无界面浏览器PhantonJS或者Firefox
        # driver = webdriver.Firefox()
        # driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", webdriver.DesiredCapabilities.HTMLUNITWITHJS)
        driver = webdriver.PhantomJS('./phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
        driver.set_window_size(1920,1080)
        # 设定页面加载限制时间
        driver.set_page_load_timeout(20)
        #设置页面等待时间
        driver.implicitly_wait(10)
        result=LoginWeibo(username,password,driver)
        if result !=1:
            driver.quit()
            time.sleep(2)
    client=MongoClient('localhost',27017)
    db=client.weibo
    weibocollection=db.weibo
    for onepeople in weibocollection.find({"_id":{'$gte':start,'$lte':end}},no_cursor_timeout=True):
        time.sleep(2)
        userid=onepeople['userid']
        if  userid== '':
            userid=onepeople['domain']
        getoneaccount(userid,driver)
    driver.quit()

def process(username,password,userid,start,end):
    geventlist=[]
    everyline=(end-start)/5+1
    a=None
    for jc in xrange(0,5):
        onestart=jc*everyline+start
        oneend=(jc+1)*everyline+start
        geventlist.append(gevent.spawn(main,username,password,userid,onestart,oneend))
    gevent.joinall(geventlist)
if __name__=='__main__':
    # 设置微博用户用户名密码
    starttime=datetime.datetime.now()
    # username = str(input('请输入微博账户用户名,输入时情加上双引号，例如"你的用户名"'))
    # password = str(input('请输入微博账户密码,输入时情加上双引号，例如"你的密码"'))
    username=''#输入微博账号
    password=''#输入密码
    userid='FWECK'
    while True:
        client=MongoClient('localhost',27017)
        db=client.weibo
        collection=db.weibo
        _id=collection.find().sort("_id",pymongo.DESCENDING).limit(1)[0]['_id']
        main(username,password,userid,0,_id)
        # p = Pool(processes=1)
        # for num in xrange(0,1):
            # p.apply_async(process,args=(username,password,userid,num*_id/1,(num+1)*_id/1,))
        # p.close()
        # p.join()
        print('抓取完毕，请进入data文件夹查看数据， 进入log文件夹查看日志')
    endtime=datetime.datetime.now()
    print '开始时间为{0}结束时间为{1}'.format(starttime,endtime)

