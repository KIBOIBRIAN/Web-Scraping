import scrap as src

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlsplit

import pandas as pd
import numpy as np

import os, sys, httplib2, json, fire, re, string, requests
from collections import OrderedDict, deque
import re, requests, requests.exceptions


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    agent = {
        "User-Agent":'Mozilla/5.0 (X11; Linux x86_64; rv:97.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
        }
    # page = requests.get(url, headers=agent)
    try:
        with closing(get(url, stream=True, headers=agent)) as resp:
            if is_good_response(resp):
                return resp.content  #.encode(BeautifulSoup.original_encoding)
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)
    
def get_elements(url, tag='',search={}, fname=None):
    """
    Downloads a page specified by the url parameter
    and returns a list of strings, one per tag element
    """

    if isinstance(url,str):
        response = simple_get(url)
    else:
        #if already it is a loaded html page
        response = url

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        
        res = []
        if tag:    
            for li in html.select(tag):
                for name in li.text.split('\n'):
                    if len(name) > 0:
                        res.append(name.strip())
                       
                
        if search:
            soup = html            
            
            
            r = ''
            if 'find' in search.keys():
                print('findaing',search['find'])
                soup = soup.find(**search['find'])
                r = soup

                
            if 'find_all' in search.keys():
                print('findaing all of',search['find_all'])
                r = soup.find_all(**search['find_all'])
   
            if r:
                for x in list(r):
                    if len(x) > 0:
                        res.extend(x)
            
        return res
    
def get_tag_elements(url, tag='h2'):
    """
    Downloads a page specified by the url parameter
    and returns a list of strings, one per tag element
    """
    
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        names = set()
        for li in html.select(tag):
            for name in li.text.split('\n'):
                if len(name) > 0:
                    names.add(name.strip())
        return list(names)

    # Raise an exception if we failed to get any data from the url
    raise Exception('Error retrieving contents at {}'.format(url)) 
    
    
def contactCanada(urls, naics_code):

    # names
    names = []
    for site in urls:
        stuff = get_elements(site, tag='ul',search={}, fname=None)
        names.append(stuff[2:-2])


    names_ = [item for sublist in names for item in sublist]
    print(len(names_))

    links = []

    for site in urls:
        linkss = get_links(site)
        linkss = [link for link in linkss if "freesearch" in link][1:]
        links.append(linkss)

    links_ = [item for sublist in links for item in sublist]

    links_ = [url.split('"')[1] for url in links_]
    print(len(links_))

    # name df
    df_ = pd.DataFrame(columns=["name", "url"])
    df_["name"] = names_
    df_["url"] = links_

    df_["url"] = "https://www.contactcanada.com/database/" + df_.url
    df_.url = df_.url.str.replace("amp;", "")
    df_.head()

    # further details
    infos = []
    for url in df_.url.values:
        infos.append(get_elements(url, tag='div',search={"class": "profileWrapper layoutSixth"}, fname=None))

    updated =[]
    for info in infos:
        updated.append(list(OrderedDict.fromkeys(info))[2:])

    print(len(updated))

    all_ = []
    for info in updated:
        all_.append(get_info(info))

    len(all_)

    df_ = pd.DataFrame.from_dict(all_)
    df_.naics_code = naics_code
    display(df_.sample(3))
    
    return df_

if get_ipython().__class__.__name__ == '__main__':
    fire(get_tag_elements)