#
# -*- coding: utf-8 -*-
#coding=utf-8

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass

import time
import datetime
import os.path
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
try:
    import ConfigParser as iniParser
except:
    import configparser as iniParser

config_file='config.ini'
LOG_file='log.log'
history_file='history.log'

page='''<html><head> <meta charset="UTF-8"></head>
<h1>{title}</h1>
{interesthtml}
<div><table><tbody>
{itemhtmllist}
</tbody></table></div>
<div></div>
<div><code>======== LOG ========<br>{dumplog}</code></div></html>
'''

interesthtml='''<div><p>======== Find Your Interests !!! ========</p></div><div><table><tbody>
{interestlist}
</tbody></table></div><div></div>
<div><p>========== End of Interests ==========</p></div>
'''

itemhtml='''<tr>
<td><a href="{link}"><img src="{picurl}" alt="" width="165" height="165" /></a></td>
<td><p>|{channel}|{mall}|{time}|<small>{tags}</small></p> <h2>{name}</h2>
    <p>{price}</p> <p>{worth} / {unworth}, #{comment}</p></td>
</tr>
'''



def ERROR(text):
    with open(LOG_file,'a') as f:
        f.write(str(time.ctime())+':[ERRR]'+text+'\n')
    exit(1)

def INFO(text):
    with open(LOG_file,'a') as f:
        f.write(str(time.ctime())+':[INFO]'+text+'\n')

def tm2str(smzdm_timestamp):
    #return datetime.datetime.fromtimestamp(smzdm_timestamp/100).strftime('%m-%d %H:%M')
    return datetime.datetime.fromtimestamp(smzdm_timestamp).strftime('%m-%d %H:%M')

def get_config():
    config_file='config.ini'

    # Read config.ini
    if not os.path.isfile(config_file):
        raise Exception(config_file+' not exist!')
    INFO("Reading {fullpathconfig!s}".format(fullpathconfig=os.path.abspath(config_file)))
    ini=iniParser.RawConfigParser()
    ini.read(config_file)
    if not ini.has_option('email','mode'):
        raise Exception('Need [email]mode in ' + config_file)
    if not ini.get('email','mode') in ('mailgun'):
        raise Exception('Not supported [email]mode')
    config={}
    config['email']=dict(ini.items('email'))
    # Integrity Check
    if config['email']['mode']=='mailgun':
        if not ('mailgun_domain' in config['email'].keys()) or not  ('mailgun_apikey' in config['email'].keys()):
            raise Exception('missing mailgun_domain or mailgun_apikey.')

    config['interests']=[]
    for tupl in ini.items('interests'):
        config['interests']=config['interests']+tupl[1].split('|')
    config['interests']=filter(None, config['interests']) # remove empty elements
    config['filter']=[]
    for tupl in ini.items('filter'):
        config['filter']=config['filter']+tupl[1].split('|')
    config['filter']=filter(None, config['filter']) # remove empty elements
    config['mallfilter']=[]
    for tupl in ini.items('mallfilter'):
        config['mallfilter']=config['mallfilter']+tupl[1].split('|')
    config['mallfilter']=filter(None, config['mallfilter']) # remove empty elements
    config['max_num_get']=ini.getint('advance','max_num_get') if ini.has_option('advance','max_num_get') else 100
    config['max_num_get']=max(5,config['max_num_get'])
    config['append_log']= ini.getboolean('advance','append_log') if ini.has_option('advance','append_log') else False
    config['verbose']   = ini.getint('advance','verbose') if ini.has_option('advance','verbose') else 3    #TODO: maybe move to logging.

    # Read history.log
    if os.path.isfile(history_file):
        ini = iniParser.ConfigParser()
        ini.read(history_file)
        config['last_timesort'] = ini.getint('history', 'last_timesort') if ini.has_section('history') else 0
    else:
        config['last_timesort'] = 0

    #print config
    INFO("LOG level={LogLv}; last_timesort={tm!s}; Num(Interests)={numI!s}; Num(filter)={numF!s}".format(
            LogLv = config['verbose'], tm = config['last_timesort'], numI=len(config['interests']), numF = len(config['filter'])))

    if sys.version_info[0]<3:
        config['mallfilter'] = [unicode(x, 'utf-8') for x in config['mallfilter']]
        config['filter']=[unicode(x,'utf-8') for x in config['filter']]
        config['interests']=[unicode(x,'utf-8') for x in config['interests']]

    return config

def requests_retry_session(
    retries=4,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries, read=retries, connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_data(max_item=100,before_timesort=0,after_timesort=0,verbose=0,req_session=None):
    before_timesort=max(before_timesort,after_timesort)
    before_timesort=before_timesort if before_timesort!=0 else int(time.time()*100)
    max_timesort=after_timesort
    min_timesort=before_timesort
    headers = {
        #'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language':'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'www.smzdm.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
        'Referer': 'http://www.smzdm.com/jingxuan/',
        'Cache-Control' : 'no-cache',
        'X-Requested-With': 'XMLHttpRequest'
    }

    url = 'http://www.smzdm.com/jingxuan/json_more?timesort={TS}?filter=s0f0t0b0d0r0p0'.format(TS=before_timesort)

    req_session=requests_retry_session(session=req_session)
    try:
        r = req_session.get(url=url, headers=headers)
    except Exception as e:
        ERROR(str(e))

    data=r.json()
    #data = json.loads(r.text)
    #with open('data.json','w') as f:
    #	json.dump(data,f)

    itemlist = []
    num_get=0
    num_ignore=0

    for item in data['article_list']:
        if num_get>=max_item:
            break

        timesort=item['article_timesort']
        picurl= '' if (not u'article_pic_url' in item.keys()) else item['article_pic_url']
        price = '' if (not u'article_price' in item.keys()) else item['article_price']
        channel='' if (not u'article_channel' in item.keys()) else item['article_channel']
        mall = '' if (not u'article_mall' in item.keys()) else item['article_mall']
        worth  = 0 if (not u'article_worthy' in item.keys()) else item['article_worthy']
        unworth= 0 if (not u'article_unworthy' in item.keys()) else item['article_unworthy']
        comment= 0 if (not u'article_comment' in item.keys()) else item['article_comment']
        timeout=0 if (not u'article_is_timeout' in item.keys()) else item['article_is_timeout']
        soldout=0 if (not u'article_is_sold_out' in item.keys()) else item['article_is_sold_out']

        tags=set()
        if u'article_tags' in item.keys():
            for t in item['article_tags']:
                tags.add(t[u'name'])
        if u'article_tese_tags' in item.keys():
            for t in item['article_tese_tags']:
                tags.add(t[u'name'])
        tags=",".join(tags)

        max_timesort=max(max_timesort,timesort)
        min_timesort=min(min_timesort,timesort)

        if timeout or soldout:
            num_ignore=num_ignore+1
            continue
        if item['article_timesort']<=after_timesort:
            continue

        oneitem = {
            'title': item['article_title'],
            'smzdm_url': item['article_url'],
            'timesort': timesort,
            'picurl': picurl,
            'price': price,
            'channel': channel,
            'tags': tags,
            'mall': mall,
            'worth':worth,
            'unworth':unworth,
            'comment':comment
        }

        itemlist.append(oneitem)
        num_get=num_get+1

    if verbose>=3 :
        INFO("GET sorttime={} : Fetch {} items between {} and {}".format(
            before_timesort, num_get, max_timesort, min_timesort
        ))

    recursion={
        'itemlist': [],
        'num_get' : 0,
        'num_ignore' : 0,
        'max_timesort' : after_timesort,
        'min_timesort' : before_timesort
    }

    if min_timesort>after_timesort and num_get<max_item and num_get != 0:
        time.sleep(0.1)
        recursion=get_data(max_item-num_get, min_timesort-1 ,after_timesort,verbose,req_session=req_session)

    return {
        'itemlist': itemlist+recursion['itemlist'],
        'num_get' : num_get+recursion['num_get'],
        'num_ignore' : num_ignore+recursion['num_ignore'],
        'max_timesort' : max_timesort,
        'min_timesort' : min(min_timesort,recursion['min_timesort'])
    }

def filter_item(data,field,keywords):
    # TODO: change to regex
    data['filteredBy'+field]=[ item['title']
        for item in data['itemlist']
        if any(word in item[field] for word in keywords)
    ]
    if data['filteredBy'+field]:
        INFO('Filtered items by {}:'.format(field) + '|'.join(data['filteredBy'+field]))
    data['itemlist']=[ item
        for item in data['itemlist']
        if not any(word in item[field] for word in keywords)
    ]
    data['num_item']=len(data['itemlist'])
    return data

def find_interested(data,wordlist):
    if( len(wordlist) == 0 ) :
        data['interestlist']=[]
        data['num_interest']=0
        return data
    data['interestlist']=[ item
        for item in data['itemlist']
        if any(word in item['title'] for word in wordlist)
    ]
    if data['interestlist']:
        data['itemlist']=[ item
            for item in data['itemlist']
            if not any(word in item['title'] for word in wordlist)
        ]
    data['num_interest']=len(data['interestlist'])
    return data


def gen_html(data,log_file,if_log):
    def format_one_item(item):
        return itemhtml.format(
            link=item['smzdm_url'],
            picurl=item['picurl'],
            channel=item['channel'],
            mall=item['mall'],
            time=tm2str(item['timesort']),
            tags=item['tags'],
            name=item['title'],
            price=item['price'],
            worth=item['worth'],
            unworth=item['unworth'],
            comment=item['comment']
        )

    interestlisthtml=''
    for item in data['interestlist']:
        interestlisthtml=interestlisthtml+format_one_item(item)

    if interestlisthtml:
        interestlisthtml=interesthtml.format(interestlist=interestlisthtml)

    itemlisthtml=''
    for item in data['itemlist']:
        itemlisthtml=itemlisthtml+format_one_item(item)

    dumplog=''
    if if_log:
        with open(log_file,'r') as f:
            for line in f.readlines():
                dumplog=dumplog+line+'<br>\n'

    htmlpage=page.format(
        title="SMZDM",
        interesthtml=interestlisthtml,
        itemhtmllist=itemlisthtml,
        dumplog=dumplog
    )

    return htmlpage

def send_email(config,html_content):
    # TODO: Support direct email
    st_code=404
    retry_left=2
    while(retry_left>0 and st_code!=200):
        if config['email']['mode']=='mailgun':
            # respond=mailgun_send_html(
            # 	config['email'],
            # 	config['email']['subject'],
            # 	html_content
            # )
            url="https://api.mailgun.net/v3/%s/messages" % config['email']['mailgun_domain']
            r=requests.post(
                url,
                auth=("api", config['email']['mailgun_apikey']),
                data={
                    "from": config['email']['mail_from'],
                    "to": config['email']['mailto'],
                    "subject": config['email']['subject'],
                    "text": config['email']['subject'],
                    "html": html_content
             })
            st_code=r.status_code
        else:
            return
        retry_left=retry_left-1

        if st_code!=200:
            INFO('Send Email:'+ str(r))
            time.sleep(5)
    return (st_code==200)

def set_history(smzdm_timesort):
    hist=iniParser.RawConfigParser()
    hist.add_section('history')
    hist.set('history','last_timesort',str(smzdm_timesort))
    with open('history.log','wb') as h:
        hist.write(h)


if __name__ == "__main__":
    print("Launch Task.")
    config=get_config()
    res = get_data(config['max_num_get'],int(time.time()),config['last_timesort'],config['verbose'])
    res = find_interested(res,config['interests'])
    res = filter_item(res,field='title',keywords=config['filter'])
    res = filter_item(res,field='tags', keywords=config['filter'])
    res = filter_item(res,field='mall', keywords=config['mallfilter'])

    INFO("interest={!s}, item={!s}, get={!s}, ignore={!s}".format(
        res['num_interest'], res['num_item'], res['num_get'], res['num_ignore'])
    )
    if (res['num_interest']+res['num_item'])>0:

        htmlpage=gen_html(res,LOG_file,config['append_log'])
        suc=send_email(config,htmlpage)
        if suc==1:
            try:
                os.remove(LOG_file)
                set_history(res['max_timesort'])
            except:
                pass
    else:
        INFO("No matching item, quit.")

    print("Task finished.")