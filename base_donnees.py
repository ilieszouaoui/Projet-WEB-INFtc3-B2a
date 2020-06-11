# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 10:49:41 2020

@author: rodrigo
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

#####

def get_leader(info):
    try:
        lead=info['leader_name1']
        new_lead = ''
        flag = False #indique si on a déjà commencé a ecrire le nom du leader
        for c in (lead): #on enleve la formatation [[]]
            if c == '[' : flag = True;
            if flag and (c ==']' or c == '|'): break
            elif flag and c != '[': new_lead += c
        return new_lead
    
    except:
        print(' Could not parse leader de {}'.format(info['conventional_long_name']))
        return None
             
def get_hdi(info):
    try:
        return info['HDI']
    except:
        print(' Could not parse HDI de {}'.format(info['conventional_long_name']))
        return None

def get_gini(info):
    try:
        return info['Gini']
    except:
        print(' Could not parse gini de {}'.format(info['conventional_long_name']))
        return None

def get_area(info):
    try:
        if ',' not in info['area_km2']: #s'il n'y a aucune virgule
            return info['area_km2']
        else: #il faut enlever les virguler du numbre
            new_area = ''
            for c in info['area_km2']:
                if c.isalnum(): new_area += c
            return new_area
    except:
        print(' Could not parse area de {}'.format(info['conventional_long_name']))
        return None

#####

def save_country(conn,country,info):    
    # préparation de la commande SQL
    c = conn.cursor()
    sql = 'INSERT INTO countries VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'

    # les infos à enregistrer
    name = get_name(info)
    capital = get_capital(info)
    coords = get_coords(info)
    leader = get_leader(info)
    hdi = get_hdi(info)
    gini = get_gini(info)
    area = get_area(info)
    
    new_country = '' #on enleve le .json et le _
    for char in country:
        if char.isalnum(): new_country += char
        elif char =='_': new_country += ' '
        elif char =='.':
            break
    country = new_country
        
    # soumission de la commande (noter que le second argument est un tuple)
    if coords != None:
        c.execute(sql,(country, name, capital, round(float(coords['lat']), 2), round(float(coords['lon']), 2), leader, hdi, gini, area))  #on enleve le .json du nom du pays
        conn.commit()
    else:
        c.execute(sql,(country, name, capital, None, None, leader, hdi, gini, area)) #on enleve le .json du nom du pays
        conn.commit() 
        
# création de la base de donnees
with ZipFile('africa.zip','r') as z:
    # liste des documents contenus dans le fichier zip
    conn = sqlite3.connect('africa_complet.sqlite')
    # infobox de l'un des pays
    for country in z.namelist():
        info = json.loads(z.read(country))
        save_country(conn, country, info)
        print(country, 'saved successfully')
