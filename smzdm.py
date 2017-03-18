#
#coding=utf-8 
# -*- coding: utf-8 -*-

import sys
try:
	reload(sys)
	sys.setdefaultencoding('utf8')
except:
	pass

import time
import datetime
import os.path
import json
import requests
try:
	import ConfigParser as iniParser
except:
	import configparser as iniParser

log_file='log.log'

page='''<html><head> <meta charset="UTF-8"></head>
<h1>{title}</h1>
<div><table><tbody>
{itemhtmllist}
</tbody></table></div>
<div></div>
<div><code>======== LOG ========<br>{dumplog}</code></div></html>
'''

itemhtml='''<tr>
<td><a href="{link}"><img src="{picurl}" alt="" width="170" height="170" /></a></td>
<td><p>|{channel}| {time} |</p>
<h2>{name}</h2> <p>{price}</p> <p>{worth} / {unworth}, #{comment}</p></td>
</tr>
'''



def ERROR(text):
	with open(log_file,'a') as f:
		f.writeline(str(time.ctime())+':[ERRR]'+text+'\n')
	exit()

def INFO(text):
	with open(log_file,'a') as f:
		f.write(str(time.ctime())+':[INFO]'+text+'\n')

def tm2str(smzdm_timestamp):
	return datetime.datetime.fromtimestamp(smzdm_timestamp/100).strftime('%m-%d %H:%M')

def get_config():
	config_file='config.ini'
	
	# Read config.ini
	if not os.path.isfile(config_file):
		raise Exception(config_file+' not exist!')
	ini=iniParser.RawConfigParser()
	ini.read(config_file)
	if not ini.has_option('email','mode'):
		raise Exception('Need [email]mode in '+config_file)
	if not ini.get('email','mode') in ('mailgun'):
		raise Exception('Not supported [email]mode')
	config={}
	config['email']=dict(ini.items('email'))
	# Integrity Check
	if config['email']['mode']=='mailgun':
		if not ('mailgun_domain' in config['email'].keys()) or not  ('mailgun_apikey' in config['email'].keys()):
			raise Exception('missing mailgun_domain or mailgun_apikey.')

	config['filter']=[]
	for tupl in ini.items('filter'):
		config['filter']=config['filter']+tupl[1].split('|')
	config['filter']=filter(None, config['filter']) # remove empty elements
	config['max_num_item']=ini.getint('advance','max_num_item')
	config['max_num_item']=max(5,config['max_num_item'])
	config['append_log']=ini.getboolean('advance','append_log')

	# Read history.log
	ini=iniParser.ConfigParser()
	ini.read('history.log')
	if ini.has_section('history'):
		config['last_timesort']=ini.getint('history','last_timesort')
	else:
		config['last_timesort']=0
	
	#print config
	INFO(str(len(config['filter']))+' items:' + '|'.join(config['filter']))
	return config


def get_data(max_item=100,before_timesort=0,after_timesort=0):
	before_timesort=max(before_timesort,after_timesort)
	before_timesort=before_timesort if before_timesort!=0 else int(time.time()*100) 
	max_timesort=after_timesort
	min_timesort=before_timesort
	headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Host': 'www.smzdm.com',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
	}

	url = 'http://www.smzdm.com/json_more?timesort=' + str(before_timesort)
	r = requests.get(url=url, headers=headers)

	if r.status_code !=200:
		INFO('[WARN] GET respond='+str(r.status_code))
		return {
			'itemlist': [],
			'num_get' : 0,
			'num_ignore' : 0,
			'max_timesort' : max_timesort,
			'min_timesort' : min_timesort
		}


	data = json.loads(r.text)
	#with open('data.json','w') as f:
	#	json.dump(data,f)

	itemlist = []
	num_get=0
	num_ignore=0

	for item in data:
		max_timesort=max(max_timesort,item['timesort'])
		min_timesort=min(min_timesort,item['timesort'])
		if num_get>=max_item:
			break;
		timeout=0 if (not u'article_is_timeout' in item.keys()) else item['article_is_timeout']
		soldout=0 if (not u'article_is_sold_out' in item.keys()) else item['article_is_sold_out']
		if timeout or soldout:
			num_ignore=num_ignore+1
			continue;
		if item['timesort']<=after_timesort:
			continue;

		#title = item['article_title']
		#smzdm_url = item['article_url']
		#timesort = item['timesort']
		picurl= '' if (not u'article_pic' in item.keys()) else item['article_pic']
		price = '' if (not u'article_price' in item.keys()) else item['article_price']
		channel='' if (not u'article_channel' in item.keys()) else item['article_channel']
		worth  = 0 if (not u'article_worthy' in item.keys()) else item['article_worthy']
		unworth= 0 if (not u'article_unworthy' in item.keys()) else item['article_unworthy']
		comment= 0 if (not u'article_comment' in item.keys()) else item['article_comment']


		oneitem = {
			'title': item['article_title'],
			'smzdm_url': item['article_url'],
			'timesort': item['timesort'],
			'picurl': picurl,
			'price': price,
			'channel': channel,
			'worth':worth,
			'unworth':unworth,
			'comment':comment
		}
		#print item['article_title'].encode('utf-8')+' | '+str(oneitem['timesort'])
		itemlist.append(oneitem)
		num_get=num_get+1

	INFO("GET ?sorttime={} : Fetch {} items between {} and {}".format(
		before_timesort, num_get, max_timesort, min_timesort
	))

	recursion={
		'itemlist': [],
		'num_get' : 0,
		'num_ignore' : 0,
		'max_timesort' : after_timesort,
		'min_timesort' : before_timesort
	}

	if min_timesort>after_timesort and num_get<max_item:
		time.sleep(2)
		recursion=get_data(max_item-num_get, min_timesort-1 ,after_timesort)

	return {
		'itemlist': itemlist+recursion['itemlist'],
		'num_get' : num_get+recursion['num_get'],
		'num_ignore' : num_ignore+recursion['num_ignore'],
		'max_timesort' : max_timesort,
		'min_timesort' : min(min_timesort,recursion['min_timesort'])
	}

def filterkeyword(data,wordlist):
	data['filteredtitle']=[ item['title']
		for item in data['itemlist']
		if any(word in item['title'].encode('utf-8') for word in wordlist)
	]
	if data['filteredtitle']:
		INFO('Filted title:' + '|'.join(data['filteredtitle']))
	data['itemlist']=[ item 
		for item in data['itemlist']
		if not any(word in item['title'].encode('utf-8') for word in wordlist)
	]
	data['num_item']=len(data['itemlist'])
	return data


def gen_html(data,log_file,if_log):
	itemlisthtml=''
	for item in data['itemlist']:
		itemlisthtml=itemlisthtml+itemhtml.format(
			link=item['smzdm_url'],
			picurl=item['picurl'],
			channel=item['channel'],
			time=tm2str(item['timesort']),
			name=item['title'],
			price=item['price'],
			worth=item['worth'],
			unworth=item['unworth'],
			comment=item['comment']
		)

	dumplog=''
	if if_log:
		with open(log_file,'r') as f:
			for line in f.readlines():
				dumplog=dumplog+line+'<br>\n'

	htmlpage=page.format(
		title="SMZDM",
		itemhtmllist=itemlisthtml,
		dumplog=dumplog
	)

	return htmlpage

def send_email(config,html_content):
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
			return;
		retry_left=retry_left-1

		if st_code!=200:
			INFO('Send Email:'+ str(respond))
			time.sleep(5)
	return (st_code==200)

def set_history(smzdm_timesort):
	hist=iniParser.RawConfigParser()
	hist.add_section('history')
	hist.set('history','last_timesort',str(smzdm_timesort))
	with open('history.log','wb') as h:
		hist.write(h)


if __name__ == "__main__":
	INFO("Launch Task.")
	config=get_config()
	res=get_data(config['max_num_item'],int(time.time()*100),config['last_timesort'])
	#with open('temp.json','w') as f:
	#	json.dump(res,f)
	#res={}
	#with open('temp.json','r') as f:
	#	res=json.load(f)
	res=filterkeyword(res,config['filter'])
	INFO("item={!s}, get={!s}, ignore={!s}".format(
		res['num_item'], res['num_get'], res['num_ignore'])
	)
	if res['num_item']>0:

		htmlpage=gen_html(res,log_file,config['append_log'])
		suc=send_email(config,htmlpage)
		if suc==1:
			try:
				os.remove(log_file)
				set_history(res['max_timesort'])
			except:
				pass
	else:
		INFO("No matching item, quit.")

	INFO("Task finished.")