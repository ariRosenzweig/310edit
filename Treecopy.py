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
              dicte = {} 
              json_data = self.response.json()  
              for n in range(len(json_data['Entries'])):  
                  Ur2 = json_data['Entries'][n]['obitlink'] 
                  Ur3 = json_data['Entries'][n]['name']  
                  c.append(Ur2)  
                  dicte.update({str(Ur2): Ur3}) 
              for uri in c:        
                     
                if uri.split(".aspx")[1].split("=")[0] == '?n':  
                   ur = uri.split("?n=")[1].replace("&pid", "-obituary?pid") 
                   ur3 = "https://www.legacy.com/obituaries/name/"  
                   uri = ur3 + ur 
                   self.b.append(uri) 
                elif uri.split('/')[3].split('=')[0] == 'link.asp?i': 
                    name = dicte[str(uri)]  
                    id = uri.split('/')[3].split('000')[1] 
                    uri="https://www.legacy.com/obituaries/name/" + name + "-obituary?pid=" + id 
                     
                    self.b.append(uri)  
                else:  
                    if uri.split('/')[4] == 'name': 
                        self.b.append(uri)                                                                                                                   
              def match(i):  
                     j = i  
                     for el in i:  
                        for le in j:  
                            if  (el.split("=")[1][0:3] in le or el.split("name/")[1].split("?")[0] in le ) and i.index(el) != j.index(le) :  
                                j.remove(le)  
                     i = j           
              match(self.b)                  
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