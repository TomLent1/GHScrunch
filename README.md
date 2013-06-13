GHScrunch
=========

by Akos Kokai

A Python program for extracting Globally Harmonised System (GHS) hazard classification information for chemicals out of various international government documents. The program will output lists of chemicals with their associated hazard classifications in CSV format. The goal is to add these GHS classifications to datasets used for comparative chemical hazard assessment, particularly for assessments guided by the [GreenScreen](http://cleanproduction.org/Greenscreen.php) framework. This is a work in progress.

For information on the Globally Harmonised System of Classification and Labelling of Chemicals, see [the UNECE's GHS website](http://www.unece.org/trans/danger/publi/ghs/ghs_welcome_e.html).


Information sources
-------------------

I use the official published classification documents from the following GHS implementations, all of which are included with this repo.


### Aotearoa New Zealand: HSNO Chemical Classifications ###

* The Environmental Protection Authority's [Chemical Classification and Information Database (CCID)](http://www.epa.govt.nz/search-databases/Pages/HSNO-CCID.aspx), which details the chemicals classified in accordance with the Hazardous Substance and New Organisms (HSNO) regulations.
* The correlation between HSNO classifications and GHS Rev. 3 classifications is described in [this document](http://www.epa.govt.nz/Publications/hsnogen-ghs-nz-hazard.pdf) (PDF).
* Data source: File 'CCID Key Studies (4 June 2013).xls', obtained through personal communication with NZ EPA.
* Files are in GHS-nz/, output is in GHS-nz/output/

The spreadsheet contains a database export of the HSNO CCID. It contains chemical names, CASRN, classification codes and text, and also a summary of the toxicological data that inform each classification. There is one classification per row in the spreadsheet (23168 classifications). This program simply adds GHS translations to each classification – according to the document cited above – and produces a condensed version of all the entries in a CSV file (some fields are omitted). It also produces a table (CSV file) of all unique classification codes that appear in the dataset, along with the full text of their HSNO and corresponding GHS classifications.


### Japan: GHS Classifications ###

* Classification results of 1424 chemicals by Inter-ministerial Committee (2006)
* Classification Results of 52 chemicals by METI (2007)
* Classification Results of 93 chemicals by METI and MOE (2008)
* Downloaded from [NITE GHS website](http://www.safe.nite.go.jp/english/ghs_index.html)
* Files are in GHS-jp/, output is in GHS-jp/output/

All three batches of classifications are distributed in series of Excel workbooks (xls), each containing up to 100 sheets. Each sheet contains the classification results for one chemical in an identical layout. Chemicals are identified by an index ID, CASRN, and chemical name. The 2006 classifications appear to be based on the first edition of GHS or on Revision 1. The subsequent classifications (which include new chemicals and updates to previously classified chemicals) are based on Revision 2. This program compiles the cumulative results of all the classifications and their updates and produces output (CSV files) organized by hazard class. 

For reference, these are the hazard classes that are listed as separate rows in the Japan GHS spreadsheets.

#### PHYSICAL HAZARDS:
* Explosives
* Flammable gases
* Flammable aerosols
* Oxidizing gases
* Gases under pressure
* Flammable liquids
* Flammable solids
* Self-reactive substances and mixtures
* Pyrophoric liquids
* Pyrophoric solids
* Self-heating substances and mixtures
* Substances and mixtures, which in contact with water, emit flammable gases
* Oxidizing liquids
* Oxidizing solids
* Organic peroxides
* Corrosive to metals

#### HEALTH HAZARDS:
* Acute toxicity (oral)
* Acute toxicity (dermal)
* Acute toxicity (inhalation: gas)
* Acute toxicity (inhalation: vapour)
* Acute toxicity (inhalation: dust, mist)
* Skin corrosion / irritation
* Serious eye damage / eye irritation
* Respiratory/skin sensitizer
* Germ cell mutagenicity
* Carcinogenicity
* Toxic to reproduction
* Specific target organs/systemic toxicity following single exposure
* Specific target organs/systemic toxicity following repeated exposure
* Aspiration hazard

#### ENVIRONMENTAL HAZARDS:
* Hazardous to the aquatic environment (acute)
* Hazardous to the aquatic environment (chronic)

Note that Acute toxicity is subdivided into 5 exposure routes, and aquatic toxicity is subdivided into acute/chronic. We preserve those subdivisions in the output of this program. Additionally, the program teases apart "Respiratory/skin sensitizer" classifications into separate respiratory and skin sensitization subcategories (for consistency with GreenScreen).

For each hazard class, the spreadsheets tabulate the following results of chemical evaluations: 
- Classification
- Symbol (named)
- Signal word
- Hazard statement (unfortunately without H-statement codes)
- Rationale for classification

The Classification field may contain any of the following things:
- A GHS category number and/or name, which depends on criteria set out specifically for each hazard class. 
- "Not Classified" - This means that the available evidence did not meet the hazard criteria.
- "Classification not possible" - This means that there were no data with which to evaluate the substance. Different from "Not classified."
- "Not applicable" - Classification criteria are not applicable to this substance.

The hazard statement could be informative, but I still need to figure out what to do with them.


### Republic of Korea: GHS Classifications ###

* The amended list of GHS classification and labelling for toxic chemicals (2011) by the National Institute of Environmental Research
* [NIER GHS Main page](http://ncis.nier.go.kr/ghs/)
* Downloaded from [this page](http://ncis.nier.go.kr/ghs/search/searchlist_view.jsp?seq=17)
* Files are in GHS-kr/, output is in GHS-kr/output/

The document is in 한국어, with only substance names in English. Fortunately, it is straightforwardly structured and includes numeric GHS chapter references for hazard classes, and H-statement codes. I was able to confirm my understanding of the document using Google Translate. This program produces a table (CSV file) of substance names; CASRN; combined hazard class, category, and H-statements (in English); and M-factors. It further produces a text file containing a list of all unique combined hazard class/category/H-statement fields that appear in the dataset.

For reference, these are the hazard classes that are represented in the Korea GHS classification list.

#### PHYSICAL HAZARDS:
* Flammable gases
* Gases under pressure
* Flammable liquids
* Flammable solids
* Substances and mixtures which, in contact with water, emit flammable gases
* Oxidizing solids
* Organic peroxides

#### HEALTH HAZARDS:
* Acute toxicity (oral)
* Acute toxicity (dermal)
* Acute toxicity (inhalation)
* Skin corrosion/irritation
* Serious eye damage/irritation
* Respiratory sensitization
* Skin sensitization
* Germ cell mutagenicity
* Carcinogenicity
* Reproductive toxicity
* Specific target organ toxicity - Single exposure
* Specific target organ toxicity - Repeated exposure
* Aspiration hazard

#### ENVIRONMENTAL HAZARDS:
* Hazardous to the aquatic environment (acute)
* Hazardous to the aquatic environment (chronic)

In the spreadsheet, each line describes one substance with one hazard classification. Columns E-F are the hazard class and category, respectively (e.g. the first one is Oxidizing solids (2.14), Category 3). Columns G-J are for labelling, respectively: symbol (coded), signal word, and hazard statement (coded), and M-factor. The program takes into account the multi-row merged cells which span classifications for the same CASRN (to avoid having many empty CASRN fields).

Using the hazard class names allows us (via Google Translate) to distinguish the following hazards that have the same GHS chapter number:
* 급성 독성-경구 (3.1) = Acute toxicity - oral
* 급성 독성-경피 (3.1) = Acute toxicity - dermal
* 급성 독성-흡입 (3.1) = Acute toxicity - inhalation
* 피부 과민성 (3.4) = Skin sensitization
* 호흡기 과민성 (3.4) = Respiratory sensitization
* 수생환경유해성-급성 (4.1) = Hazardous to the aquatic environment - acute
* 수생환경유해성-만성 (4.1) = Hazardous to the aquatic environment - chronic

