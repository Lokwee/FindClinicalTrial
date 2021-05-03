# Everything with selenium becuse dynamic websites
import pandas as pd 
from bs4 import BeautifulSoup
from selenium import webdriver
import time 
from selenium.common.exceptions import NoSuchElementException 
import math 
import numpy as np 
import mysql.connector
from sqlalchemy import create_engine

# Initialize
host = "localhost"
user = "root"
passwd = "Nakuru9665*"
database = "ClinicalTrials"

db = mysql.connector.connect(
  host = "localhost",
  user = "root",
  passwd = "Nakuru9665*",
  database = "ClinicalTrials"
)
print(db)

# Create cursor
mycursor = db.cursor()

engine = create_engine('mysql+pymysql://{user}:{passwd}@{host}/{database}'.format(host=host, database=database, user=user, passwd=passwd))

# Webdriver instance
driver = webdriver.Chrome(executable_path = "/Users/phoebelokwee/Downloads/chromedriver")

# Tell website to give results of our search term
def get_url(search_term):
  """Generate a url from search term"""
  template = "https://www.ncbi.nlm.nih.gov/clinvar/?term={}"
  search_term = search_term.replace(' ', '+')
  return template.format(search_term)
       
def check_exists_by_xpath(xpath):
  try:
    driver.find_element_by_xpath(xpath)
  except NoSuchElementException:
    return False
  return True

# Get url for genetic disorders listed in clinvar
url = get_url('genetic disorders')
driver.get(url)

# Clean dataframe from the data in the two lists
def get_full_dataFrame(x, y):
  df = pd.DataFrame(y)
  df.dropna(inplace = True)
  df['Links'] = x
  df.rename(columns={0:'Saved',1:'Status',2:'Study Title',3:'Conditions',4:'Interventions',5:'Locations','Links':'Links'}, inplace = True)
  df.drop('Saved', axis=1)
  return df

# Save in csv file and update by scraping all page
pageCounter = 0
url2 = get_url('cvid')
df = pd.DataFrame()
driver.get(url2)
soup = BeautifulSoup(driver.page_source)
maxPageCount = int(soup.find('input', {'id':'pageno'})['last'])
while pageCounter <= maxPageCount - 1:
  time.sleep(3)
  html = driver.page_source
  df1 = pd.read_html(html)[0]
  df = df.append(df1, ignore_index=True)
  df.to_csv('test.csv')
  if check_exists_by_xpath('//*[@title="Next page of results"]'):
    page_button = driver.find_element_by_xpath('//*[@title="Next page of results"]')
    page_button.click()
    pageCounter +=1
  else:
    print('Last page')
    break

# get url for clinical trials that are still recruiting
def get_clinicaltrial_url(search_term):
  """Generate a url from search term"""
  template = "https://clinicaltrials.gov/ct2/results?cond={}&Search=Apply&recrs=a&age_v=&gndr=&type=&rslt="
  search_term = search_term.replace(' ', '+')
  return template.format(search_term)

# pages < totalPages
# Get further information from each available study
def get_study_info(study_link):
  """Generate a url from search term"""
  template = "https://clinicaltrials.gov{}"
  study_link = study_link.replace(' ', '+')
  return template.format(study_link)

# Loops through all available trials, saves their details and links for more information in lists
def get_available_trials(condition):
  url = get_clinicaltrial_url(condition)
  driver.get(url)
  time.sleep(2)
  links = []
  value_row_list = []
  # if check_exists_by_xpath('//*[@id="theDataTable_info"]/b'):
  #   pageNumbers = int(driver.find_element_by_xpath('//*[@id="theDataTable_info"]/b').text)
  #   totalPages = math.ceil(pageNumbers/10) - 1
  # else:
  #   totalPages = 1
  pages = 0
  while True:
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source)
    table = soup.find('table', {'id':'theDataTable'})
    slinks = []
    row_list = []
    if table:
      table_data = table.find_all('tr')
    else:
      table_data = None 
      data = {'Saved':[None], 'Status':[None], 'Study Title':[None], 'Conditions':[None], 'Interventions':[None], 'Locations':[None],'Links':[None]}
      df = pd.DataFrame(data)
      return df
      break 
    for link in table.find_all('a', href = True):
      links.append(get_study_info(link['href'])) 
    for cell in table_data:
      td = cell.find_all('td')[1:]
      row = [i.text.replace('\n','') for i in td]
      value_row_list.append(row)
    if check_exists_by_xpath("//a[@class='paginate_button next disabled']") == False and check_exists_by_xpath('//*[@id="theDataTable_next"]'):
      button = driver.find_element_by_xpath('//*[@id="theDataTable_next"]')
      button.click()
      pages =+ 1
      time.sleep(5)
    else:
      print('None available')
      return get_full_dataFrame(links, value_row_list)

# Get dataframe with study details 
def get_study_details(search_term):
  title = []
  summary = []
  sex = []
  age = []
  health = []
  contact = []
  study = get_study_info(search_term)
  driver.get(study)
  time.sleep(2)
  soup = BeautifulSoup(driver.page_source)
  tabular_view = soup.find('li', {'id':'tabular'})
  info_link_list = []
  for links in tabular_view.find_all('a', href = True):
    info_link_list.append(links['href'])
  for i in info_link_list:
    study = get_study_info(i)
    driver.get(study)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source)
    info_table = soup.find_all('tr')
    study_title = info_table[18].text.rstrip('\n')
    title.append(study_title)
    summary_study = info_table[20].text.rstrip('\n')
    summary.append(summary_study)
    sex_eligibility = info_table[39].text.rstrip('\n')
    sex.append(sex_eligibility)
    age_eligibility = info_table[40].text.rstrip('\n')
    age.append(age_eligibility)
    health_eligibility = info_table[41].text.rstrip('\n')
    health.append(health_eligibility)
    contact_information = info_table[42].text.rstrip('\n')
    contact.append(contact_information)
  final_df = pd.DataFrame({'Title':title, 'Summary':summary, 'Sex Eligibility':sex, 'Age Eligibility':age, 'Contact information':contact})
  return final_df
  
study_details = get_study_details()
study_details.dropna()
study_details.to_csv('study.csv')

# Clean list of genetic disorders
# get column in terms of a list and collect some info
# Lots of list comprehension stuff coming
data = pd.read_csv("clinVar.csv")
data.head()
data.columns
Conditions = data['Condition(s)'].tolist()

# Get only the unique conditions to avoid repetition
unique_list = []
for x in Conditions:
  if x not in unique_list:
    unique_list.append(x)

print(unique_list)

# Concatenate the different strings to make it to sth more palatable
comma_separated = ", ".join(unique_list)
len(comma_separated)
type(comma_separated)

myList = list(comma_separated.split(","))
len(myList)

# Create unique based off this new criteria again
unique_list_final = []
for x in myList:
  if x not in unique_list_final:
    unique_list_final.append(x)

len(unique_list_final)

# Create a list conaining key word ""...see more" which distorts search results in clinvar
new_list = []
sub_string = ["...see more", "adult type", "agenesis of", "allele 4", "alpha"]
for i in unique_list_final:
  for sub in sub_string:
    if sub in i:
      new_list.append(i)
len(new_list)
new_list

# Remove all strings containing see more
for condition in unique_list_final:
  for j in new_list:
    if condition == j:
      unique_list_final.remove(condition)

len(unique_list_final)
len(unique_list_final)
# create new list using strings that now do not have ...see more
tags = ["...see more"]
confused = []
for tag in tags:
  for c in new_list:
    c = c.replace(tag, "")
    confused.append(c)

len(confused)
confused
# Remove white spaces from these words
for i in confused:
  j = i.strip()
  confused.remove(i)
  confused.append(j)
confused

# Append to unique_final_list as our final list of unique conditions
for i in confused:
  unique_list_final.append(i)

len(unique_list_final)
unique_list_final

unique_list_final1 = []
for x in unique_list_final:
  if x not in unique_list_final1:
    unique_list_final1.append(x)

len(unique_list_final1)

for i in unique_list_final1:
  i.lstrip()
  i.rstrip()
  unique_list_final1.remove(i)
  unique_list_final1.append(j)

len(unique_list_final1)
unique_list_final1.sort()

# Start from here next time
unique_list_final1[270:290]

# I hope there is a better way to do this, I did everything manually:
# Acute myeloid, 'Acute myeloid leukemia', Alzheimer disease, 'Aplastic anemia', 'Hepatocellular carcinoma', not giving desired results 
genetic_disorders = ['acenocoumarol', 'acetazolamide-responsive ataxia','acetalozamide', '3-Methylglutaconic aciduria type 2','Barth Syndrome', '3-methylglutaconic aciduria type V', '3MC syndrome 2', 'Osa syndrome', 'ABri amyloidosis', 'Spastic Paraplegia', 'Familial hypercholesterolemia', 'APOE4(-)-FREIBURG', 'ASAH1-related disorders', 'Spinal muscular atrophy', 'Farber disease', 'Rolandic epilepsy', 'Abnormal electroretinogram', 'Absence seizures', 'Calpain-3', 'Muscular dystrophy', 'Accelerated skeletal maturation', 'Achondrogenesis', 'Achondroplasia', 'Achromatopsia', 'Acid alpha-glucosidase deficiency', 'Pompe disease','Acrocephalosyndactyly', 'Acromesomelic dysplasia', 'Acromicric dysplasia', 'Marfan syndrome', 'Acute infantile liver failure', 'Acute monoblastic leukemia', 'Myelodysplastic syndrome', 'Acyl-CoA dehydrogenase family', 'Addison disease', 'Adenocarcinoma of stomach', 'Adenoma', 'Adenylosuccinate lyase deficiency', 'Adrenocortical carcinoma', 'Adult hypophosphatasia', 'Adult polyglucosan body disease', 'Adult proximal spinal muscular atrophy', 'Age-related macular degeneration', 'Alagille syndrome', 'Alpha-1-antitrypsin deficiency', 'Alpha-N-acetylgalactosaminidase deficiency type 1', 'Alport syndrome', 'Alstrom syndrome', 'Amelocerebrohypohidrotic syndrome', 'Amish lethal microcephaly', 'Amyotrophic lateral sclerosis 14', 'Amyotrophic lateral sclerosis 6', 'Amyotrophic lateral sclerosis 1', 'Amyotrophic lateral sclerosis type 8', 'Amyotrophy', 'Anophthalmia syndrome', 'Microphthalmia syndrome', 'Anterior segment dysgenesis 1', 'Anterior segment dysgenesis 6', 'Anteverted nares', 'Antithrombin III deficiency', 'Aortic dilatation', 'Apparent mineralocorticoid excess', 'Argininosuccinate lyase deficiency', 'Arrhythmia', 'Arrhythmogenic right ventricular dysplasia 9', 'Arthrogryposis', 'Arthrogryposis multiplex congenita 3', 'Arts syndrome', 'Asperger syndrome', 'Asphyxiating thoracic dystrophy', 'Asthma', 'Ataxia-Oculomotor Apraxia', 'Ataxia-oculomotor apraxia 1', 'Atelosteogenesis type 1', 'Atelosteogenesis type II', 'Atrioventricular block', 'Atypical Gaucher Disease', 'Atypical hemolytic uremic syndrome', 'Atypical hemolytic-uremic syndrome 3', 'Autism 15', 'Autism with high cognitive abilities', 'Autosomal dominant distal hereditary motor neuropathy', 'Charcot-Marie-Tooth disease', 'Autosomal dominant nonsyndromic deafness', 'Ophthalmoplegia', 'Dystonia', 'Autosomal recessive cerebellar ataxia', 'Autosomal recessive hypophosphatemic vitamin D refractory rickets', 'Autosomal recessive multiple pterygium syndrome', 'Autosomal recessive osteopetrosis 2', 'Axenfeld-Rieger syndrome type 1', 'Axial myopathy', 'Azorean disease', 'B lymphoblastic leukemia lymphoma', 'Baller-Gerold syndrome', 'Basal ganglia calcification', 'Beare-Stevenson cutis gyrata syndrome', 'Becker muscular dystrophy', 'Benign familial hematuria', 'Benign familial neonatal seizures 2', 'Bestrophinopathy', 'Bethlem myopathy 1', 'Bietti crystalline corneoretinal dystrophy', 'Bilateral conductive hearing impairment', 'Biotinidase deficiency', 'Blepharophimosis', 'Bone mineral density quantitative trait locus 18', 'Bowing of the long bones', 'Brachydactyly type A2', 'Brain small vessel disease with hemorrhage', 'Branchiootic syndrome 1', 'Breast carcinoma', 'Breast-ovarian cancer', 'Brittle cornea syndrome 1', 'Broad thumb', 'Rubinstein-Taybi Syndrome', 'Bronchiectasis', 'Brugada syndrome', 'Budd-Chiari syndrome', 'Homocystinuria', 'CFTR-related disorders', 'Cystic fibrosis', 'CHEK2', 'CIC-DUX Sarcoma', 'Congenital disorder of glycosylation', 'COLLAGEN TYPE III POLYMORPHISM', 'Macular dystrophy', 'Cafe-au-lait spot', 'Camptomelic dysplasia', 'Cancer of cervix', 'Carbonic anhydrase VA deficiency', 'Carcinoma of colon', 'Carnitine palmitoyltransferase 1A deficiency', 'Carpenter syndrome', 'Cataract', 'Caudal regression sequence', 'Celiac disease', 'Central core disease', 'Centronuclear Myopathy', 'Cerebellar hemisphere hypoplasia', 'Cerebral atrophy', 'Cerebral cavernous malformation', 'Cerebrooculofacioskeletal syndrome 1', 'Ceroid lipofuscinosis neuronal 2', 'Charlevoix-Saguenay spastic ataxia', 'Childhood hypophosphatasia', 'Cholestasis', 'Chondrocalcinosis 2', 'Choroid plexus papilloma', 'Choroidal neovascularization', 'Chromophobe renal cell carcinoma', 'Chromosome 2q37 deletion syndrome', 'Chronic diarrhea', 'Chronic granulomatous disease', 'Chronic kidney disease', 'Chronic sinusitis', 'Citrullinemia type II', 'Classic homocystinuria', 'Cleft palate', 'Clinodactyly of the 5th finger', 'Clubfoot', 'Cockayne syndrome', 'Coffin-Lowry syndrome', 'Coffin-Siris syndrome 1', 'Coloboma', 'Colon polyps', 'Colorectal adenoma', 'Combined Pituitary Hormone Deficiency', 'Combined Deficiency of Sialidase and Beta Galactosidase', 'Combined malonic and methylmalonic aciduria', 'Combined oxidative phosphorylation deficiency 10', 'Combined oxidative phosphorylation deficiency 20', 'Common variable agammaglobulinemia', 'Common variable immunodeficiency 4', 'Common variable immunodeficiency 8', 'Complete combined 17-alpha-hydroxylase/17', 'Conduction disorder of the heart', 'Cone-rod dystrophy', 'Stargardt disease', 'Congenital Indifference to Pain', 'Congenital absence of salivary gland', 'Congenital amegakaryocytic thrombocytopenia', 'Congenital bile acid synthesis defect', 'Congenital cataract', 'Congenital diaphragmatic hernia', 'Congenital disorder of glycosylation', 'Congenital heart disease', 'Congenital hypothyroidism', 'Congenital macrodactylia', 'Congenital muscular dystrophy', 'Congenital myasthenic syndrome', 'Congenital myopathy with fiber type disproportion', 'Congenital ocular coloboma', 'Congenital stationary night blindness', 'Congestive heart failure', 'Corneal Dystrophy', 'Coronal craniosynostosis', 'Cowden syndrome', 'Cranioectodermal dysplasia 2', 'Craniofacial-deafness-hand syndrome', 'Craniosynostosis', 'Creatine deficiency syndrome 1', 'Crigler-Najjar syndrome type 1', 'Crouzon syndrome', 'Crouzon syndromeFGFR2 related craniosynostosis', 'Curry-Hall syndrome', 'Cutaneous malignant melanoma', 'Cutaneous photosensitivity', 'Malignant tumor of breast']

test_list = ['Acute myeloid', 'Acute myeloid leukemia', 'Alzheimer disease', 'Aplastic anemia', 'Hepatocellular carcinoma']

len(genetic_disorders)

# Add all created dataframes into our database
trial_data = []
for disorder in new_list:
  trial_data.append(get_available_trials(disorder))
  for df in trial_data:
    df.insert(loc=0, column='Names', value= '{0}'.format(disorder), allow_duplicates=True)
    df.to_sql(name='GeneticDisorders', con=engine,index=False, if_exists='append')
    # df.to_csv('d{0}.csv'.format(disorder))