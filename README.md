GHScrunch
=========

by Akos Kokai

A Python program for extracting Globally Harmonised System (GHS) hazard classification information for chemicals out of various international government documents. The program will output lists of chemicals with their associated hazard classifications in CSV format. The goal is to add these GHS classifications to datasets used for comparative chemical hazard assessment, particularly for assessments guided by the [GreenScreen](http://cleanproduction.org/Greenscreen.php) framework. This is a work in progress.

For information on the Globally Harmonised System of Classification and Labelling of Chemicals, see [the UNECE's GHS website](http://www.unece.org/trans/danger/publi/ghs/ghs_welcome_e.html).


Information sources and explanation
-----------------------------------

I use the official published classification documents from the following GHS implementations, all of which are included with this repo.


### Aotearoa New Zealand: HSNO Chemical Classifications ###

* Classifications from the Environmental Protection Authority's [Chemical Classification and Information Database (CCID)](http://www.epa.govt.nz/search-databases/Pages/HSNO-CCID.aspx)
* Data source: File `CCID Key Studies (4 June 2013).xls`, obtained through personal communication with NZ EPA.
* The correlation between HSNO classifications and GHS Rev. 3 classifications is described in [a document](http://www.epa.govt.nz/Publications/hsnogen-ghs-nz-hazard.pdf) (PDF), which is also included in this repo.
* Files are in `GHS-nz/`, output is in `GHS-nz/output/`

**What the program does:** Reads data exported from the HSNO CCID, and produces CSV files containing chemical IDs, names, classifications, and key studies (basis for classification). The program adds GHS translations to each HSNO classification, according to the document cited above. 

The program filters the dataset in order to separate information that might be considered redundant from a broad chemical hazard assessment perspective: classifications of solutions of other substances. The filtering algorithm looks at substances which share the same CASRN but have different names, and seems to work reasonably well for this dataset. Three output files are produced: The main file `GHS-nz/output/GHS-nz.csv` contains classifications of pure substances. 'Redundant' substances are written to `GHS-nz/output/exclude.csv`, and are almost all solutions whose classifications are a subset of the pure substance's classifications. Solutions that appear to have unique classifications (not a subset of the pure substance's classifications) are written to `GHS-nz/output/variants.csv`. In the latter two output files, CASRN values for each different substance are preceded by "_v" + a sequential number, to help with identifier wrangling.

Finally, the program produces `GHS-nz/output/sublists.csv`, a table of all unique classification codes that appear in the dataset, along with the full text of their HSNO and corresponding GHS classifications.

**How the data source is organized:** The spreadsheet is a data export from the HSNO CCID. It contains chemical names, CASRN, classification codes and text, and summaries of the key toxicological studies or data that inform each classification. There is one classification per row in the spreadsheet (23168 classifications). Substances are identified non-uniquely by CASRN, and uniquely by name – that is, multiple variants share the same CASRN.


### Japan: GHS Classifications ###

* Classification results of 1424 chemicals by Inter-ministerial Committee (2006)
* Classification Results of 52 chemicals by METI (2007) – 20 new chemicals, 32 revisions
* Classification Results of 93 chemicals by METI and MOE (2008) – 89 new chemicals, 4 revisions
* All were downloaded from [NITE GHS website](http://www.safe.nite.go.jp/english/ghs_index.html)
* Files are in `GHS-jp/`, output is in `GHS-jp/output/`

**What the program does:** Compiles the cumulative results of all chemical classifications and revisions. Produces output organized by hazard class: one CSV file per hazard class (e.g. `GHS-jp/output/mutagen.csv`), containing GHS classifications of every individual chemical in the dataset for that hazard class – one chemical per row. For consistency with standard GHS and GreenScreen, the program splits "Respiratory/skin sensitizer" classifications into separate respiratory and skin sensitization classes. Classifications that are unqualified "Not applicable", "Not classified", or "Classification not possible" are left out of the hazard-specific output files, and instead are collected in three CSV files corresponding to those designations. Finally, the program outputs a list of all the unique classification text strings, `GHS-jp/output/classifications.txt`, and an index of all chemicals in the dataset, `GHS-jp/output/index.csv`, for diagnostic purposes.

**How the data source is organized:** All three batches of classifications (2006, 2007, 2008) are distributed in series of Excel workbooks, each containing up to 100 sheets. Each sheet contains the classification results for one chemical in an identical layout. Chemicals are identified by an index ID, CASRN, and chemical name. Japanese government's classification manual, used for the initial (2006) classifications, is included: `GHS-jp/ghs_manual_e(2005).pdf`. The subsequent classifications (which include new chemicals and updated records for previously classified chemicals) are based on GHS Revision 2.

For each hazard class, the spreadsheets tabulate the following results of chemical evaluations: 
- Classification
- Symbol (named)
- Signal word
- Hazard statement (unfortunately without H-statement codes)
- Rationale for classification

The Classification field may contain any of the following things:
- A GHS classification - i.e., a category number and/or name specific to the hazard class. 
- "Not Classified" - This means that the available evidence did not meet the hazard criteria.
- "Classification not possible" - This means that there were no data with which to evaluate the substance. Different from "Not classified."
- "Not applicable" - Classification criteria are not applicable to this substance.


### Republic of Korea: GHS Classifications ###

* The amended list of GHS classification and labelling for toxic chemicals (2011) by the National Institute of Environmental Research
* [NIER GHS Main page](http://ncis.nier.go.kr/ghs/)
* Downloaded from [this page](http://ncis.nier.go.kr/ghs/search/searchlist_view.jsp?seq=17)
* Files are in `GHS-kr/`, output is in `GHS-kr/output/`

**What the program does:** Reads the spreadsheet of Korean GHS classifications and produces `GHS-kr/output/GHS-kr.csv`, containing a table of substance names, CASRN, combined hazard class/category/H-statements (in English), and M-factors. It further produces a text file `GHS-kr/output/sublists.txt` containing a list of all unique combined hazard class/category/H-statement fields that appear in the dataset.

**How the data source is organized:** The document is in 한국어, with only substance names in English. It is straightforwardly structured and includes numeric GHS chapter references for hazard classes, and H-statement codes. I was able to convincingly translate the key elements of the document using Google Translate (some of my notes are in `GHS-kr/GHS-kr-trans-attempt.ods`, LibreOffice spreadsheet). 

In the original spreadsheet, each line describes one substance with one hazard classification. Columns E-F are the hazard class and category, respectively (e.g. the first one is Oxidizing solids (2.14), Category 3). Columns G-J are for labelling, respectively: symbol (coded), signal word, and hazard statement (coded), and M-factor. The program takes into account the multi-row merged cells which span classifications for the same CASRN (to avoid having many empty CASRN fields).

Using the hazard class names allows (via Google Translate) distinguishing the following hazards that have the same GHS chapter number:
* 급성 독성-경구 (3.1) = Acute toxicity - oral
* 급성 독성-경피 (3.1) = Acute toxicity - dermal
* 급성 독성-흡입 (3.1) = Acute toxicity - inhalation
* 피부 과민성 (3.4) = Skin sensitization
* 호흡기 과민성 (3.4) = Respiratory sensitization
* 수생환경유해성-급성 (4.1) = Hazardous to the aquatic environment - acute
* 수생환경유해성-만성 (4.1) = Hazardous to the aquatic environment - chronic

