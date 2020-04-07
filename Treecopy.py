import requests, lxml, bs4, json, spacy 
from bs4 import BeautifulSoup     
import en_core_web_sm
nlp = en_core_web_sm.load()
class Proj: 
          def __init__(self):   
              self.url = None   
              self.response = None   
              self.html_doc = None   
              self.soup = None   
              self.apiurl = None  
              self.numentry = None  
              self.total = None  
              self.resultspp = None  
              self.entrysize = None  
              self.pagesleft = None  
              self.b = None  

          def fn1 (self, state):  
              with open('stateid3copy.json') as f:   
                           statesdict = json.load(f)  
                           for elem in statesdict:  
                               if elem['State'] == state.capitalize():  
                                   state = elem['Id']  
                                   return state  
                                   break  
                             
          def getSearch (self, fname, lname, state=None):   
           if not state:  
              self.url=f"https://www.legacy.com/obituaries/legacy/obituary-search.aspx?daterange=99999&lastname={lname}&keyword={fname}&countryid=1&stateid=all&affiliateid=all"   
           else:  
            std = self.fn1(state)  
            self.url=f"https://www.legacy.com/obituaries/legacy/obituary-search.aspx?daterange=99999&lastname={lname}&keyword={fname}&countryid=1&stateid={std}&affiliateid=all"  
           self.response = requests.get(self.url)   
           self.html_doc = self.response.content.decode('utf-8')   
           self.soup = BeautifulSoup(self.html_doc, 'lxml')    
           for line in self.html_doc.splitlines():   
               if 'wsUrl' in line:   
                   self.apiurl=line.partition("'")[2].partition("'")[0]  
                   break                                                                                                                                     
          def getNew (self):   
              print(self.url)   
             #print(self.response)   
              print(self.apiurl)   
           
          def getApi (self):   
              self.response = requests.get(self.apiurl)   
              self.pagedata = self.response.content.decode('utf-8')   
          def getApistats (self):  
              self.getApi()  
              json_data = self.response.json()   
              self.pagesleft = json_data['NumPageRemaining']  
              self.resultspp = json_data['EntriesPerPage']   
              self.total = json_data['Total']  
              self.numentry  = json_data['NumEntryRemaining']   
              self.entrysize = self.total - self.numentry  
              #print(self.pagesleft, self.resultspp, self.total, self.entrysize) 
 
          def extractLinks (self):  
              self.b = []                                                             
              c = []  
              json_data = self.response.json()
              c = json_data   
              for n in range(int(str(c).count("'id':"))): 
                  Id = c['Entries'][n]['id']  
                  name = c['Entries'][n]['name'].replace(' ', '-').replace('.', '') + '-obituary?pid='
                  string="https://www.legacy.com/obituaries/name/"
                  if c['Entries'][n]['name'] != '':
                      self.b.append(f'{string}{name}{Id}')    
              
          def getLinks (self):  
              m=1  
              d = []  
              page = self.apiurl  
              if self.pagesleft == 0:  
                 self.getApistats()  
                 self.extractLinks()   
                 d = d + self.b  
              else:  
               while self.pagesleft != 0:  
                     self.apiurl = "{}&Page={}".format(page, m)  
                     self.getApistats()  
                     self.extractLinks()  
                     d = d + self.b  
                     m += 1  
              self.b = d                                                                                                                                     
             #print(print(self.b))
          def getPage(self, pageno=None):
                g = []
                page = self.apiurl
                self.apiurl = "{}&Page={}".format(page, pageno)
                self.getApi() 
                self.extractLinks()
                g = g + self.b
                self.b = g
               #print(self.b)
                                                                                                                                                        






          def extractText (self):  
              e = []  
              for uri  in self.b:  
                  response = requests.get(uri)  
                  html_doc = response.content.decode('utf-8')  
                  soup = BeautifulSoup(html_doc, 'lxml')  
                  for line in html_doc.splitlines():  
                      if 'window.__INITIAL_STATE__' in line:  
                          txt = line  
                          break                                                                                                                                                
                  txt2 = txt[:-1].partition(" = ")[2]  
                  mytxt = json.loads(txt2)  
                   
                  a = mytxt['personStore']['obituaries']  
                  tname = mytxt['personStore']['name'] 
                  tloc = mytxt['personStore']['location'] 
                  condol = mytxt['personStore']['guestBook']['condolences']['edges'] 
                  dict1 = {} 
                  dict2 = {} 
                  dict3 ={} 
                  for elem in range(len(a)):   
                            c = mytxt['personStore']['obituaries'][elem]['obituaryText']  
                            b = BeautifulSoup(c, 'lxml')  
                            tbody = b.text  
                            dict1.update({"Text" + str(elem): tbody})                     
                  for text in dict1:  
                       tbody = dict1[text]  
                       tentities = dict([(str(x), x.label_) for x in nlp(tbody).ents if x.label_ == 'PERSON'])  
                       dict3.update({str(text): tentities})  
                   
                   
                  dict2.update({"Texts": dict1, "Name": tname, "Location": tloc, "Condols": condol, "Ents": dict3}) 
                  e.append(dict2) 
              return e  