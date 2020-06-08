# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 10:49:41 2020

@author: rodri
"""


# importations

import re
import sqlite3 
from zipfile import ZipFile
import json

# fonctions auxiliaires pour recuperer les infos des pays : 

def get_coords(info): # format : {'lat': '139', 'lon': '35'}
    
    try:
        coords=info['coordinates']
        m = re.match('\{\{Coord\|(\w+)\|(\w+)\|(\w+)\|(\w+)\|(\w+)\|(\w+)\|type:city}}', coords)
        lon = int(m.group(1))+int(m.group(2))/60
        if m.group(3)=='S': lon=lon*-1
        lat = int(m.group(4))+int(m.group(5))/60
        if m.group(6)=='W': lon=lon*-1
        return {'lat':str(lat),'lon':str(lon)}
    except:
        print(' Could not parse coordinates de {}'.format(info['conventional_long_name']))
        return None

def get_capital(info):
    cap=info['capital']
    m = re.match("\[\[(\w+)\]\]", cap)
    if m == None :
        print(' Could not parse capital de {}'.format(info['conventional_long_name']))
        return None
    cap = m.group(1)
    return cap

def get_name(info):
    return info['conventional_long_name']

def save_country(conn,country,info):    
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT INTO countries VALUES (?, ?, ?, ?, ?)'

    # les infos à enregistrer
    name = get_name(info)
    capital = get_capital(info)
    coords = get_coords(info)

    # soumission de la commande (noter que le second argument est un tuple)
    if coords != None:
        c.execute(sql,(country, name, capital, coords['lat'], coords['lon']))
        conn.commit()
    else:
        c.execute(sql,(country, name, capital, None, None))
        conn.commit() 
    
# création de la base de donnees
with ZipFile('africa.zip','r') as z:
    # liste des documents contenus dans le fichier zip
    conn = sqlite3.connect('africa.sqlite')
    # infobox de l'un des pays
    for country in z.namelist():
        info = json.loads(z.read(country))
        save_country(conn, country, info)
        print(country, 'saved successfully')
    
