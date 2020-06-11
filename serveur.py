# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 09:45:54 2020

@author: iliès
"""


import http.server
import socketserver
import sqlite3

from urllib.parse import urlparse, parse_qs, unquote


#
# Définition du nouveau handler
#
class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-répertoire racine des documents statiques
  static_dir = '/client'

  #
  # On surcharge la méthode qui traite les requêtes GET
  #
  def do_GET(self):
    # on récupère les paramètres
    self.init_params()

    # le chemin d'accès commence par /time
    if self.path.startswith('/time'):
      self.send_time()
   
    # le chemin d'accès commence par /countries
    elif self.path.startswith('/countries'):
      self.send_countries()

    # le chemin d'accès commence par /country et se poursuit par un nom de pays
    elif self.path_info[0] == 'country' and len(self.path_info) > 1:
      self.send_country(self.path_info[1])
      
    # ou pas...
    else:
      self.send_static()

  #
  # On surcharge la méthode qui traite les requêtes HEAD
  #
  def do_HEAD(self):
    self.send_static()

  #
  # On envoie le document statique demandé
  #
  def send_static(self):

    # on modifie le chemin d'accès en insérant un répertoire préfixe
    self.path = self.static_dir + self.path

    # on appelle la méthode parent (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    if (self.command=='HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)
        

  #     
  # on analyse la requête pour initialiser nos paramètres
  #
  def init_params(self):
    # analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]  # info.path.split('/')[1:]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)),'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
    else:
      self.body = ''
   
    # traces
    print('path_info =',self.path_info)
    print('body =',length,ctype,self.body)
    print('params =', self.params)


  #
  # On envoie un document avec l'heure
  #
  def send_time(self):
    
    # on récupère l'heure
    time = self.date_time_string()

    # on génère un document au format html
    body = '<!doctype html>' + \
           '<meta charset="utf-8">' + \
           '<title>l\'heure</title>' + \
           '<div>Voici l\'heure du serveur :</div>' + \
           '<pre>{}</pre>'.format(time)

    # pour prévenir qu'il s'agit d'une ressource au format html
    headers = [('Content-Type','text/html;charset=utf-8')]

    # on envoie
    self.send(body,headers)

  #
  # On renvoie la liste des pays
  #
  def send_countries(self):

    # création d'un curseur (conn est globale)
    c = conn.cursor()
    
    # récupération de la liste des pays dans la base
    c.execute("SELECT name FROM countries")
    r = c.fetchall()

    # construction de la réponse
    txt = 'List of all {} countries :\n'.format(len(r))
    n = 0
    for a in r:
       n += 1
       txt = txt + '[{}] - {}\n'.format(n,a[0])
    
    # envoi de la réponse
    headers = [('Content-Type','text/plain;charset=utf-8')]
    self.send(txt,headers)

  #
  # On renvoie les informations d'un pays
  #
  def send_country(self,country):

    # préparation de la requête SQL
    c = conn.cursor()
    sql = 'SELECT * from countries WHERE wp=?'

    # récupération de l'information (ou pas)
    c.execute(sql,(country,))
    r = c.fetchone()

    # on n'a pas trouvé le pays demandé
    if r == None:
      self.send_error(404,'Country not found')

    # on génère un document au format html
    else:
      body = '<!DOCTYPE html>\n<meta charset="utf-8">\n'
      body += '<title>{}</title>'.format(country)
      body += '<link rel="stylesheet" href="/ProjetWeb.css">'
      body += '<main>'
      body += '<h1>{}</h1>'.format(r['name'])
      body += '<ul>'
      body += '<li>{}: {}</li>'.format('Leader',r['leader'])
      body += '<li>{}: {} km2</li>'.format('Superficie',r['area_km2'])
      body += '<li>{}: {}</li>'.format('Capital',r['capital'])
      body += '<li>{}: {:.3f}</li>'.format('Latitude',r['latitude'])
      body += '<li>{}: {:.3f}</li>'.format('Longitude',r['longitude'])
      body += '<li>{}: {:.3f}</li>'.format('Coefficient de Gini',r['gini'])
      body += '<li>{}: {:.3f}</li>'.format('Indice de developpement humain (IDH)',r['hdi'])
      body += '</ul>'
      body += '</main>'

      # on envoie la réponse
      headers = [('Content-Type','text/html;charset=utf-8')]
      self.send(body,headers)

  #
  # On envoie les entêtes et le corps fourni
  #
  def send(self,body,headers=[]):

    # on encode la chaine de caractères à envoyer
    encoded = bytes(body, 'UTF-8')

    # on envoie la ligne de statut
    self.send_response(200)

    # on envoie les lignes d'entête et la ligne vide
    [self.send_header(*t) for t in headers]
    self.send_header('Content-Length',int(len(encoded)))
    self.end_headers()

    # on envoie le corps de la réponse
    self.wfile.write(encoded)

 
#
# Ouverture d'une connexion avec la base de données
#
conn = sqlite3.connect('africa_complet.sqlite')

# Pour accéder au résultat des requêtes sous forme d'un dictionnaire
conn.row_factory = sqlite3.Row

#
# Instanciation et lancement du serveur
#
httpd = socketserver.TCPServer(("", 8080), RequestHandler)
httpd.serve_forever()