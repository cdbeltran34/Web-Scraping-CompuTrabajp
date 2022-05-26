
from cgitb import text
from http.client import SWITCHING_PROTOCOLS
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from pandas import ExcelWriter


criteria = pd.read_excel('Categorías Busqueda Webscraping FCCEA.xlsx')
example_word="turismo"
offers_list=[]     #lista para guardar las cabeceras de las ofertas



#metodo para depurar caracteres de las palabras
#params: s(string a depurar)  return: s (string depurado)
def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
        
    return s


def write_excel(d,name):

    writer = pd.ExcelWriter(name+'.xlsx', engine='xlsxwriter')
    d.to_excel(writer, sheet_name='Sheet1')
    #print(profile["name"])

    writer.save()
    print("Guardo el Archivo con informacion de Profesores")



"""metodo para obtener cabecera de cada oferta
@paramas: soup_reference:page content(pagina obtenida),campo:string
 (campo detallado), search_word:string(palabra a buscar)"""

def offers_head(soup_reference,field,search_word):
    offers = soup_reference.find_all('div', class_="w100")
    #print(len(offers))
    for offer in offers:
        
        url_title=offer.find('a',href=True)
        
        try:
            company=offer.find('a',{'class':'fc_base hover it-blank'}).text
        except:
            company=""
        region=''.join(offer.find('p',{'class':'fs16 fc_base mt5 mb10'}).find_all(text=True, recursive=False)).strip()
        offer_info=[field,
            search_word,
            url_title.text,
            'https://www.computrabajo.com.co'+url_title['href'].strip(),
            company.strip(),
            region
        ]
        
        #print("titulo: ",url_title.text,"compañia:",company.text,"Region: ",
        #region)
        
        offers_list.append(offer_info)





            #lista para guardar encabezados de ofertas

# para recorrer las páginas y obtener por cada una los encabezados de las ofertas

for index, row in criteria.iterrows():
    debugged_criteria = normalize(row['PALABRA DE BUSQUEDA WEBSCRAPING'].lower())
    page_number=1
    page = requests.get('https://www.computrabajo.com.co/trabajo-de-'
                        + debugged_criteria.replace(' ', '-').replace(',', '-') +'?p='+str(page_number))
    while page:
        
        try:
            print("número de página:",page_number)
            page = requests.get('https://www.computrabajo.com.co/trabajo-de-'
                        + debugged_criteria.replace(' ', '-').replace(',', '-') +'?p='+str(page_number))
            print(debugged_criteria)
            soup = BeautifulSoup(page.content, 'html.parser')
            #llama al metodo anterior para buscar el encabezado de ofertas por cada criterio página por página
            offers_head(soup, row['CAMPO'], row['PALABRA DE BUSQUEDA WEBSCRAPING'])
        except:
            print("no hay mas páginas")
            break
    
        page_number=page_number+1                 
    
    #print(len(offers))

#print(offers_list)

#------------------------------------------------
"""metodo para obtener detalle de la oferta
paramas: url:string (url de página de oferta)"""
def offer_detail(url):
    salary=''
    contract_type=''
    journal=''
    description=''
    education=''
    travel_disp=''
    resident_disp=''
    disc_persons=''
    experience=''
    languagues=''
    knowledge=''
    Age=''
    try:
        offer_page=requests.get(url)
        soup_offer = BeautifulSoup(offer_page.content, 'html.parser')
        
        des=soup_offer.find_all('span',class_="tag base mb10")
        try:
            salary=des[0].text
            contract_type=des[1].text
            journal=des[2].text
        except:
            salary="Sin especificar"
            contract_type=des[0].text
            journal=des[1].text
        
        description=soup_offer.find('p',class_="mbB").text
        requirements=soup_offer.find('ul',class_="disc mbB")
        #requirements=soup_offer.find_all('li',class_="mb10")
        for r in requirements.find_all('li',class_="mb10"):
            #print(r.text)
            if "Educación mínima:" in r.text:
                education=r.text
            if "Disponibilidad de viajar" in r.text:
                travel_disp=r.text
            if "Personas con discapacidad" in r.text:
                disc_persons=r.text
            if "Disponibilidad de cambio de residencia" in r.text:
                resident_disp=r.text 
            if "años de experiencia" in r.text:
                experience=r.text
            if "Idiomas" in r.text:
                languagues=r.text
            if "Conocimientos" in r.text:
                knowledge=r.text
            if "Age" in r.text:
                Age=r.text
        
        #print(salary,contract_type,journal,"requisitos: ",education,travel_disp,disc_persons,resident_disp,
        #experience,languagues,knowledge,Age,salary,description,languagues,education,experience,Age,knowledge,travel_disp,
        #resident_disp,disc_persons)
        data_details=[contract_type,journal,salary,description,languagues,education,experience,Age,knowledge,travel_disp,
        resident_disp,disc_persons]
        return data_details
    except:
        data_details=[contract_type,journal,salary,description,languagues,education,experience,Age,knowledge,travel_disp,
        resident_disp,disc_persons]
        print("No existe la oferta ")
        return data_details
        


#ciclo para llamar offer details por cada oferta y crear data frame con los datos
"""data_computrabajo=['Página','Campo''Criterio de búsqueda', 'Oferta', 'URL',
                                        'Empresa','Región', 
                                         'Tipo de contrato', 'Jornada', 'Salario',
                                        'Descripción', 'Idiomas',
                                        'Educación mínima', 'Años de experiencia', 'Edad',
                                        'Conocimientos', 'Disponibilidad de viajar',
                                        'Disponibilidad de cambio de residencia',
                                        'Personas con discapacidad']"""

dict_offers={"offers":[]}
for offer in offers_list:
    print(offer[3],"Palabra: ",offer[1])
    
    details=offer_detail(offer[3])
    dict_offers["offers"].append({"Página":"Computrabajo",
    "Campo":offer[0],
    "Palabra de busqueda":offer[1],
    "Titulo de oferta":offer[2],
    "Link de oferta":offer[3],
    "Empresa":offer[4],
    "Región":offer[5],
    "Empresa":offer[4],
    "Tipo de contrato":details[0],
    "Jornada":details[1],
    "Salario":details[2],
    "Descripción":details[3],
    "Idiomas":details[4],
    "Educación mínima":details[5],
    "Experiencia":details[6],
    "Edad":details[7],
    "Concocimiento":details[8],
    "Disponibilidad para viajar":details[9],
    "Disponibilidad para cambiar de residencia":details[10],
    "Personas con discapacidad":details[11],
    })

#Description: Metodo para escribir el resultado y exportar arhcivo excel con datos
#params: dict(diccionario con datos de detaller de las ofertas)
def write_results_offers(dict):
    df=pd.DataFrame.from_dict(dict["offers"])
    writer = pd.ExcelWriter('OfertasComputrabajoDetaller.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    #print(profile["name"])

    writer.save()
    print("Guardo el Archivo con ofertas de computrabajo")

write_results_offers(dict_offers)

""""
page = requests.get('https://www.computrabajo.com.co/trabajo-de-'
                        + example_word.replace(' ', '-').replace(',', '-') + '?q='
                        + example_word.replace(',', ''))
soup = BeautifulSoup(page.content, 'html.parser')
offers_head(soup, example_word, example_word) 

"""


"""""


#cabecera de busqueda por palabra a buscar (cantidad de ofertas)
search_data=[]
for index, row in criteria.iterrows():
    debugged_criteria = normalize(row['PALABRA DE BUSQUEDA WEBSCRAPING'].lower())
    debugged_criteria=row['PALABRA DE BUSQUEDA WEBSCRAPING']
    page = requests.get('https://www.computrabajo.com.co/trabajo-de-'
                        + debugged_criteria.replace(' ', '-').replace(',', '-') + '?q='
                        + debugged_criteria.replace(',', ''))
    soup = BeautifulSoup(page.content, 'html.parser')

    offers = soup.find('div', class_="w100")
    count_offers = offers.find('span')
    note_offers = offers.find('h1').text
    if count_offers:
        offer_data=count_offers.text
    else:
        offer_data=note_offers.text.strip()
    print(row,offer_data)
    data=[row["CAMPO"],row["PALABRA DE BUSQUEDA WEBSCRAPING"],offer_data]
    search_data.append(data)


count_df = pd.DataFrame(search_data)
write_excel(count_df,"cantidad de ofertas")
print(count_df)

"""