#!/usr/local/bin/python3.3

# ghscrunch3.py
# Extract GHS hazard classification information for chemicals out of various
# international government documents, and output as a series of CSV files. 
# By Akos Kokai. 
# Uses the xlrd module (http://www.python-excel.org/).


import xlrd
import csv
import argparse


def ghs_hazard(ref):
    # Look up the hazard class based on GHS chapter reference.
    # Accurate to GHS Revision 4.
    ghs_chapters = {
        '2.1': 'Explosives',
        '2.2': 'Flammable gases',
        '2.3': 'Aerosols',
        '2.4': 'Oxidizing gases',
        '2.5': 'Gases under pressure',
        '2.6': 'Flammable liquids',
        '2.7': 'Flammable solids',
        '2.8': 'Self-reactive substances and mixtures',
        '2.9': 'Pyrophoric liquids',
        '2.10': 'Pyrophoric solids',
        '2.11': 'Self-heating substances and mixtures',
        '2.12': 'Substances and mixtures which, in contact with water, emit flammable gases',
        '2.13': 'Oxidizing liquids',
        '2.14': 'Oxidizing solids',
        '2.15': 'Organic peroxides',
        '2.16': 'Corrosive to metals',
        '3.1': 'Acute toxicity',
        '3.2': 'Skin corrosion/irritation',
        '3.3': 'Serious eye damage/irritation',
        '3.4': 'Respiratory or skin sensitization',
        '3.5': 'Germ cell mutagenicity',
        '3.6': 'Carcinogenicity',
        '3.7': 'Reproductive toxicity',
        '3.8': 'Specific target organ toxicity - Single exposure',
        '3.9': 'Specific target organ toxicity - Repeated exposure',
        '3.10': 'Aspiration hazard',
        '4.1': 'Hazardous to the aquatic environment',
        '4.2': 'Hazardous to the ozone layer'
    }
    return ghs_chapters[ref]


def h_statement(h):
    # H-statements: List from GHS Revision 4.
    # Did not include the abbreviated combinations (e.g. H302 + H332).
    h_statements = {
        # Physical hazards
        'H200': 'Unstable explosive',
        'H201': 'Explosive; mass explosion hazard',
        'H202': 'Explosive; severe projection hazard',
        'H203': 'Explosive; fire, blast or projection hazard',
        'H204': 'Fire or projection hazard',
        'H205': 'May mass explode in fire',
        'H220': 'Extremely flammable gas',
        'H221': 'Flammable gas',
        'H222': 'Extremely flammable aerosol',
        'H223': 'Flammable aerosol',
        'H224': 'Extremely flammable liquid and vapour',
        'H225': 'Highly flammable liquid and vapour',
        'H226': 'Flammable liquid and vapour',
        'H227': 'Combustible liquid',
        'H228': 'Flammable solid',
        'H229': 'Pressurized container: may burst if heated',
        'H230': 'May react explosively even in the absence of air',
        'H231': 'May react explosively even in the absence of air at elevated pressure and/or temperature',
        'H240': 'Heating may cause an explosion',
        'H241': 'Heating may cause a fire or explosion',
        'H242': 'Heating may cause a fire',
        'H250': 'Catches fire spontaneously if exposed to air',
        'H251': 'Self-heating; may catch fire',
        'H252': 'Self-heating in large quantities; may catch fire',
        'H260': 'In contact with water releases flammable gases which may ignite spontaneously',
        'H261': 'In contact with water releases flammable gas',
        'H270': 'May cause or intensify fire; oxidizer',
        'H271': 'May cause fire or explosion; strong oxidizer',
        'H272': 'May intensify fire; oxidizer',
        'H280': 'Contains gas under pressure; may explode if heated',
        'H281': 'Contains refrigerated gas; may cause cryogenic burns or injury',
        'H290': 'May be corrosive to metals',
        # Health hazards
        'H300': 'Fatal if swallowed',
        'H301': 'Toxic if swallowed',
        'H302': 'Harmful if swallowed',
        'H303': 'May be harmful if swallowed',
        'H304': 'May be fatal if swallowed and enters airways',
        'H305': 'May be harmful if swallowed and enters airways',
        'H310': 'Fatal in contact with skin',
        'H311': 'Toxic in contact with skin',
        'H312': 'Harmful in contact with skin',
        'H313': 'May be harmful in contact with skin',
        'H314': 'Causes severe skin burns and eye damage',
        'H315': 'Causes skin irritation',
        'H316': 'Causes mild skin irritation',
        'H317': 'May cause an allergic skin reaction',
        'H318': 'Causes serious eye damage',
        'H319': 'Causes serious eye irritation',
        'H320': 'Causes eye irritation',
        'H330': 'Fatal if inhaled',
        'H331': 'Toxic if inhaled',
        'H332': 'Harmful if inhaled',
        'H333': 'May be harmful if inhaled',
        'H334': 'May cause allergy or asthma symptoms or breathing difficulties if inhaled',
        'H335': 'May cause respiratory irritation',
        'H336': 'May cause drowsiness or dizziness',
        'H340': 'May cause genetic defects',
        'H341': 'Suspected of causing genetic defects',
        'H350': 'May cause cancer',
        'H351': 'Suspected of causing cancer',
        'H360': 'May damage fertility or the unborn child',
        'H361': 'Suspected of damaging fertility or the unborn child',
        'H362': 'May cause harm to breast-fed children',
        'H370': 'Causes damage to organs',
        'H371': 'May cause damage to organs',
        'H372': 'Causes damage to organs through prolonged or repeated exposure',
        'H373': 'May cause damage to organs through prolonged or repeated exposure',
        # Environmental hazards
        'H400': 'Very toxic to aquatic life',
        'H401': 'Toxic to aquatic life',
        'H402': 'Harmful to aquatic life',
        'H410': 'Very toxic to aquatic life with long lasting effects',
        'H411': 'Toxic to aquatic life with long lasting effects',
        'H412': 'Harmful to aquatic life with long lasting effects',
        'H413': 'May cause long lasting harmful effects to aquatic life',
        'H420': 'Harms public health and the environment by destroying ozone in the upper atmosphere'
    }
    return h_statements[h]


def splitsens(info):
    # For Japan GHS classifications.
    # Splits apart info for respiratory sensitization and skin sensitization
    # in a given row of cells. I didn't strip off errant hyphens, because in
    # the symbol/signal/statement fields, "-" is used to denote the absence
    # of the hazard, e.g. "(Respiratory sensitizer)-\n(Skin sensitizer)-".
    # Don't include hazard class names in input, better to predetermine those.
    resp_list = ['Respiratory sensitizer']
    skin_list = ['Skin sensitizer']
    for x in info:
        x = str(x)
        if 'Skin' in x:
            a = x.find('Skin')
            resp_str = x[:a].rstrip(';([ \n\r')
            skin_str = x[a:].rstrip('; \n\r')
        else: 
            resp_str = skin_str = x.rstrip(' \n')
        resp_list = resp_list + [resp_str]
        skin_list = skin_list + [skin_str]
    return resp_list, skin_list


def update(chemical, hazard_class, datalist):
    # For Japan GHS classifications.
    # Copies spreadsheet data to the chemical classification record.
    # Does not overwrite the original classification info with blank parts
    # (sections not updated) of the revised classification.
    if hazard_class not in chemical:
        chemical[hazard_class] = datalist
    elif datalist[1] != '':
        chemical[hazard_class] = datalist

def update_all(chemicals, source_file):
    # For Japan GHS classifications.
    # Creates or updates the dict of chemical classifications from a given
    # spreadsheet. Specifying date allows revisions to be clearly seen, but
    # not going to deal with parsing the dates given in the spreadsheets.
    chembook = xlrd.open_workbook(source_file)
    # Ignore the first sheet (it's just a list of chemicals in the workbook).
    for chempage in range(1, chembook.nsheets):
        chemsheet = chembook.sheet_by_index(chempage)
        # Cells are identified by (row, col) where A1 is (0, 0).
        id = chemsheet.cell_value(1,0)
        casrn_field = chemsheet.cell_value(2, 2)
        # Must use their ID numbers as unique ID if CASRN is blank.
        if casrn_field.strip() == '' or casrn_field.strip() == '-':
            casrn_field = id
        chemname = chemsheet.cell_value(1, 3)
        date = chemsheet.cell_value(2, 4)
        # But I also want one CASRN per chemical listing.
        for c in casrn_field.split(','):
            casrn = c.strip()
            if casrn not in chemicals:
                chemicals[casrn] = dict(name=chemname)
            # We are going to extract columns 2-7 for each of the rows.
            # Hazard class name is in col 2, Classification is in col 3, ...
            update(chemicals[casrn], 'explosive', chemsheet.row_values(5)[2:8] + [date])
            update(chemicals[casrn], 'flamm_gas', chemsheet.row_values(6)[2:8] + [date])
            update(chemicals[casrn], 'flamm_aer', chemsheet.row_values(7)[2:8] + [date])
            update(chemicals[casrn], 'oxid_gas', chemsheet.row_values(8)[2:8] + [date])
            update(chemicals[casrn], 'gas_press', chemsheet.row_values(9)[2:8] + [date])
            update(chemicals[casrn], 'flamm_liq', chemsheet.row_values(10)[2:8] + [date])
            update(chemicals[casrn], 'flamm_sol', chemsheet.row_values(11)[2:8] + [date])
            update(chemicals[casrn], 'self_react', chemsheet.row_values(12)[2:8] + [date])
            update(chemicals[casrn], 'pyro_liq', chemsheet.row_values(13)[2:8] + [date])
            update(chemicals[casrn], 'pyro_sol', chemsheet.row_values(14)[2:8] + [date])
            update(chemicals[casrn], 'self_heat', chemsheet.row_values(15)[2:8] + [date])
            update(chemicals[casrn], 'water_fire', chemsheet.row_values(16)[2:8] + [date])
            update(chemicals[casrn], 'oxid_liq', chemsheet.row_values(17)[2:8] + [date])
            update(chemicals[casrn], 'oxid_sol', chemsheet.row_values(18)[2:8] + [date])
            update(chemicals[casrn], 'org_perox', chemsheet.row_values(19)[2:8] + [date])
            update(chemicals[casrn], 'cor_metal', chemsheet.row_values(20)[2:8] + [date])
            update(chemicals[casrn], 'acute_oral', chemsheet.row_values(24)[2:8] + [date])
            update(chemicals[casrn], 'acute_derm', chemsheet.row_values(25)[2:8] + [date])
            update(chemicals[casrn], 'acute_gas', chemsheet.row_values(26)[2:8] + [date])
            update(chemicals[casrn], 'acute_vap', chemsheet.row_values(27)[2:8] + [date])
            update(chemicals[casrn], 'acute_air', chemsheet.row_values(28)[2:8] + [date])
            update(chemicals[casrn], 'skin_cor', chemsheet.row_values(29)[2:8] + [date])
            update(chemicals[casrn], 'eye_dmg', chemsheet.row_values(30)[2:8] + [date])
            # For respiratory & skin sensitization, we need to split the strings.
            resp_only, skin_only = splitsens(chemsheet.row_values(31)[3:8])
            update(chemicals[casrn], 'resp_sens', resp_only + [date])
            update(chemicals[casrn], 'skin_sens', skin_only + [date])
            update(chemicals[casrn], 'mutagen', chemsheet.row_values(32)[2:8] + [date])
            update(chemicals[casrn], 'cancer', chemsheet.row_values(33)[2:8] + [date])
            update(chemicals[casrn], 'repr_tox', chemsheet.row_values(34)[2:8] + [date])
            update(chemicals[casrn], 'sys_single', chemsheet.row_values(35)[2:8] + [date])
            update(chemicals[casrn], 'sys_rept', chemsheet.row_values(36)[2:8] + [date])
            update(chemicals[casrn], 'asp_haz', chemsheet.row_values(37)[2:8] + [date])
            update(chemicals[casrn], 'aq_acute', chemsheet.row_values(41)[2:8] + [date])
            update(chemicals[casrn], 'aq_chronic', chemsheet.row_values(42)[2:8] + [date])


def crunch_jp():
    # Process the Japan GHS classifications (2006-2008).
    GHS_jp_2006_files = [
        'GHS-jp/classification_result_e(ID001-100).xls',
        'GHS-jp/classification_result_e(ID101-200).xls',
        'GHS-jp/classification_result_e(ID201-300).xls',
        'GHS-jp/classification_result_e(ID301-400).xls',
        'GHS-jp/classification_result_e(ID401-500).xls',
        'GHS-jp/classification_result_e(ID501-600).xls',
        'GHS-jp/classification_result_e(ID601-700).xls',
        'GHS-jp/classification_result_e(ID701-800).xls',
        'GHS-jp/classification_result_e(ID801-900).xls',
        'GHS-jp/classification_result_e(ID901-1000).xls',
        'GHS-jp/classification_result_e(ID1001-1100).xls',
        'GHS-jp/classification_result_e(ID1101-1200).xls',
        'GHS-jp/classification_result_e(ID1201-1300).xls',
        'GHS-jp/classification_result_e(ID1301-1400).xls',
        'GHS-jp/classification_result_e(ID1401-1424).xls'
    ]
    GHS_jp_2007_files = [
                        'GHS-jp/METI_H19_GHS_review_e.xls',
                        'GHS-jp/METI_H19_GHS_new_e.xls'
                        ]
    GHS_jp_2008_files = [
                        'GHS-jp/METI_H20_GHS_review_e.xls',
                        'GHS-jp/METI_H20_GHS_new_e.xls'
                        ]

    # Initialize a dictionary of CASRN-identified chemicals. 
    # Each item will contain
    #   - a 'name' key, with chemical name as value.
    #   - keys for each hazard class, with lists of relevant classification
    #     information as their values.
    chemicals = dict()

    # These are all the hazard class keywords that we will use.
    hazard_classes = [
        'explosive',
        'flamm_gas',
        'flamm_aer',
        'oxid_gas',
        'gas_press',
        'flamm_liq',
        'flamm_sol',
        'self_react',
        'pyro_liq',
        'pyro_sol',
        'self_heat',
        'water_fire',
        'oxid_liq',
        'oxid_sol',
        'org_perox',
        'cor_metal',
        'acute_oral',
        'acute_derm',
        'acute_gas',
        'acute_vap',
        'acute_air',
        'skin_cor',
        'eye_dmg',
        'resp_sens',
        'skin_sens',
        'mutagen',
        'cancer',
        'repr_tox',
        'sys_single',
        'sys_rept',
        'asp_haz',
        'aq_acute',
        'aq_chronic'
    ]
    
    # First feed in the 2006 mass classification.
    for filename in GHS_jp_2006_files:
        update_all(chemicals, filename)
    # Then add subsequent revisions and additions.
    for filename in GHS_jp_2007_files:
        update_all(chemicals, filename)
    for filename in GHS_jp_2008_files:
        update_all(chemicals, filename)

    # Finally, output a list of chemicals & their classification info for 
    # each hazard class.
    # These are all the fields we have extracted:
    out_header = ['CASRN', 'Name', 'Hazard class', 'Classification', 
                  'Symbol', 'Signal word', 'Hazard statement', 
                  'Rationale for classification', 'Date of classification']
    # CASRN are the keys in the dict called chemicals. Name is stored in 
    # chemicals[<casrn>]['name'], and the rest of the data are stored in 
    # chemicals[<casrn>][<hazard_class>] as a list, in this order.
    
    # I want the output to be in separate CSV files for each hazard class.
    for h in hazard_classes:
        with open('GHS-jp/output/' + h + '.csv', 'w', newline='') as outfile:
            listwriter = csv.writer(outfile)
            listwriter.writerow(out_header)
            for c in chemicals.keys():
                listwriter.writerow([c] + [chemicals[c]['name']] + 
                                    chemicals[c][h])

    # Also output an index of chemicals, just to check for problems.
    with open('GHS-jp/output/index.csv', 'w', newline='') as outfile:
        listwriter = csv.writer(outfile)
        listwriter.writerow(['CASRN', 'Name'])
        for c in chemicals.keys():
            listwriter.writerow([c] + [chemicals[c]['name']])


def crunch_kr():
    # Process the Korea GHS classification (2011).
    chembook = xlrd.open_workbook('GHS-kr/GHS-kr-2011-04-15.xls')
    chemsheet = chembook.sheet_by_index(0)
    outfile = open('GHS-kr/output/GHS-kr.csv', 'w', newline='')
    listwriter = csv.writer(outfile)
    listwriter.writerow(['Name', 'CASRN', 'Hazard class', 'Category', 
                         'H-statement', 'M-factor'])
    for r in range(16,1208):
        # Name:           (r, 1)
        # CASRN:          (r, 3)
        # Don't overwrite name and CASRN with blanks from merged cells.
        if chemsheet.cell_value(r, 1) != '':
            name = chemsheet.cell_value(r, 1)
        if chemsheet.cell_value(r, 3) != '':
            casrn = chemsheet.cell_value(r, 3)
        # Hazard class    (r, 4)
        # Hazard category (r, 5)
        # Pictogram code  (r, 6) - (not used anymore?)
        # Signal word     (r, 7) - (in Korean)
        # H-stmnt code    (r, 8)
        # M-factor        (r, 9)
        haz_class_field = chemsheet.cell_value(r, 4)
        ref = haz_class_field[haz_class_field.find('('):].strip('()')
        haz_class_en = ghs_hazard(ref)
        if ref == '3.1':
            if u'급성 독성-경구' in haz_class_field:
                haz_class_en = 'Acute toxicity (oral)'
            elif u'급성 독성-경피' in haz_class_field:
                haz_class_en = 'Acute toxicity (dermal)'
            elif u'급성 독성-흡입' in haz_class_field:
                haz_class_en = 'Acute toxicity (inhalation)'
            else:
                print('Found a different hazard class 3.1 in row ' + str(r))
        if ref == '3.4':
            if u'피부 과민성' in haz_class_field:
                haz_class_en = 'Skin sensitization'
            elif u'호흡기 과민성' in haz_class_field:
                haz_class_en = 'Respiratory sensitization'
            else:
                print('Found a different hazard class 3.4 in row ' + str(r))
        if ref == '4.1':
            if u'수생환경유해성-급성' in haz_class_field:
                haz_class_en = 'Hazardous to the aquatic environment (acute)'
            elif u'수생환경유해성-만성' in haz_class_field:
                haz_class_en = 'Hazardous to the aquatic environment (chronic)'
            else:
                print('Found a different hazard class 4.1 in row ' + str(r))
        # Category values are integers stored as floats.
        category = 'Category ' + str(int(chemsheet.cell_value(r, 5)))
        h_code = chemsheet.cell_value(r, 8)
        h_state = h_code + ' - ' + h_statement(h_code)
        if chemsheet.cell_value(r, 9) != '':
            m_factor = str(int(chemsheet.cell_value(r, 9)))
        else: m_factor = ''
        listwriter.writerow([name, casrn, haz_class_en, category, 
                             h_state, m_factor])
    outfile.close()


def main():
    parser = argparse.ArgumentParser(description='Extract GHS hazard \
                classifications from country-specific documents.') 
    parser.add_argument('countries', action='store', nargs='+', 
                choices=['jp', 'kr'], 
                help='Process GHS classifications from these countries.')
    args = parser.parse_args()
    if 'jp' in args.countries:
        print('Processing GHS-Japan.')
        crunch_jp()
    if 'kr' in args.countries:
        print('Processing GHS-Korea.')
        crunch_kr()


main()
