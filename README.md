# FindClinicalTrials

FindClinicalTrials is a program that enables users to search for currently available and recruiting clinical trials for Genetic Disorders chronicled on Clinvar (https://www.ncbi.nlm.nih.gov/clinvar/).
I first scraped https://www.ncbi.nlm.nih.gov/clinvar/ by searching for genetic disorders and saving the Conditions column. I then use that information to scrape for available clinical  trials in clinicaltrials.gov and save the information in a MySQL database. 

## Files:
### clinvarClinical.py
In this file, 
