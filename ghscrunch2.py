#!/usr/local/bin/python2.7
# coding=utf-8

# ghscrunch2.py
# Extract GHS hazard classification information for chemicals out of various
# international government documents, and output as a series of CSV files. 
# By Akos Kokai. 
# Uses the xlrd module (http://www.python-excel.org/).

import csv, codecs, cStringIO
import xlrd

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def h_statement(h_code):
# H-statements from http://en.wikipedia.org/wiki/GHS_hazard_statement - 
# Thumbs down to the UN for making their GHS-Rev4 PDF file copy-protected.
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
    return h_statements[h_code]


def splitsens(texts):
# For splitting apart "Respiratory sensitizer:... Skin sensitizer:..."
# in several cells in a row. I didn't strip off errant hyphens, because
# in the symbol/signal/statement fields, "-" is used to denote the absence
# of the named hazard, e.g. "(Respiratory sensitizer)-\n(Skin sensitizer)-".
    resp_list = []
    skin_list = []
    for x in texts:
        if 'Skin' in x:
            a = x.find('Skin')
            resp_str = x[:a].rstrip(';([ \n\r')
            skin_str = x[a:].rstrip('; \n\r')
        else: 
            resp_str = skin_str = x.rstrip(' \n')
        resp_list = resp_list + [resp_str]
        skin_list = skin_list + [skin_str]
    return resp_list, skin_list

# Japan GHS classifications (2006-2008)
def crunch_jp():
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
    GHS_jp_rev_files = [
                        'GHS-jp/METI_H19_GHS_review_e.xls',
                        'GHS-jp/METI_H20_GHS_review_e.xls'
                        ]
    GHS_jp_new_files = [
                        'GHS-jp/METI_H19_GHS_new_e.xls',
                        'GHS-jp/METI_H20_GHS_new_e.xls'
                        ]

# These are all the hazard lists we will create.
    hazard_lists = {
        'explosive': [], 'flamm_gas': [], 'flamm_aer': [], 'oxid_gas': [], 
        'gas_press': [], 'flamm_liq': [], 'flamm_sol': [], 'self_react': [], 
        'pyro_liq': [], 'pyro_sol': [], 'self_heat': [], 'water_fire': [], 
        'oxid_liq': [], 'oxid_sol': [], 'org_perox': [], 'cor_metal': [], 
        'acute_oral': [], 'acute_derm': [], 'acute_gas': [], 'acute_vap': [], 
        'acute_air': [], 'skin_cor': [], 'eye_dmg': [], 'resp_sens': [], 
        'skin_sens': [], 'mutagen': [], 'cancer': [], 'repr_tox': [], 
        'sys_single': [], 'sys_rept': [], 'asp_haz': [], 'aq_acute': [], 
        'aq_chronic': []
    }
# These are the fields we will populate in each hazard list.
    list_header = ['CASRN', 'Name', 'Hazard class', 'Classification',
                   'Symbol', 'Signal word', 'Hazard statement',
                   'Rationale for classification', 'Date']
    for h in hazard_lists:
        hazard_lists[h].append(list_header)

    for filename in GHS_jp_2006_files:
        chembook = xlrd.open_workbook(filename)
# Ignore the first sheet (it's just a list of chemicals in the workbook).
#        for chempage in range(1, chembook.nsheets):
        for chempage in range(1,6): # Testing...
            chemsheet = chembook.sheet_by_index(chempage)
# Cells are identified by (row, col) where A1 is (0, 0).
            casrn_field = chemsheet.cell_value(2, 2)
            chemname = chemsheet.cell_value(1, 3)
# We want one line for each CASRN.
            for casrn in casrn_field.split(','):
# We are going to extract columns 2 and onwards, for each of these rows.
# Hazard class name is in col 2, Classification in col 3, and so on...
# Physical Hazards:
                hazard_lists['explosive'].append([casrn, chemname] + chemsheet.row_values(5)[2:] + ['2006'])
                hazard_lists['flamm_gas'].append([casrn, chemname] + chemsheet.row_values(6)[2:] + ['2006'])
                hazard_lists['flamm_aer'].append([casrn, chemname] + chemsheet.row_values(7)[2:] + ['2006'])
                hazard_lists['oxid_gas'].append([casrn, chemname] + chemsheet.row_values(8)[2:] + ['2006'])
                hazard_lists['gas_press'].append([casrn, chemname] + chemsheet.row_values(9)[2:] + ['2006'])
                hazard_lists['flamm_liq'].append([casrn, chemname] + chemsheet.row_values(10)[2:] + ['2006'])
                hazard_lists['flamm_sol'].append([casrn, chemname] + chemsheet.row_values(11)[2:] + ['2006'])
                hazard_lists['self_react'].append([casrn, chemname] + chemsheet.row_values(12)[2:] + ['2006'])
                hazard_lists['pyro_liq'].append([casrn, chemname] + chemsheet.row_values(13)[2:] + ['2006'])
                hazard_lists['pyro_sol'].append([casrn, chemname] + chemsheet.row_values(14)[2:] + ['2006'])
                hazard_lists['self_heat'].append([casrn, chemname] + chemsheet.row_values(15)[2:] + ['2006'])
                hazard_lists['water_fire'].append([casrn, chemname] + chemsheet.row_values(16)[2:] + ['2006'])
                hazard_lists['oxid_liq'].append([casrn, chemname] + chemsheet.row_values(17)[2:] + ['2006'])
                hazard_lists['oxid_sol'].append([casrn, chemname] + chemsheet.row_values(18)[2:] + ['2006'])
                hazard_lists['org_perox'].append([casrn, chemname] + chemsheet.row_values(19)[2:] + ['2006'])
                hazard_lists['cor_metal'].append([casrn, chemname] + chemsheet.row_values(20)[2:] + ['2006'])
# Health Hazards:
                hazard_lists['acute_oral'].append([casrn, chemname] + chemsheet.row_values(24)[2:] + ['2006'])
                hazard_lists['acute_derm'].append([casrn, chemname] + chemsheet.row_values(25)[2:] + ['2006'])
                hazard_lists['acute_gas'].append([casrn, chemname] + chemsheet.row_values(26)[2:] + ['2006'])
                hazard_lists['acute_vap'].append([casrn, chemname] + chemsheet.row_values(27)[2:] + ['2006'])
                hazard_lists['acute_air'].append([casrn, chemname] + chemsheet.row_values(28)[2:] + ['2006'])
                hazard_lists['skin_cor'].append([casrn, chemname] + chemsheet.row_values(29)[2:] + ['2006'])
                hazard_lists['eye_dmg'].append([casrn, chemname] + chemsheet.row_values(30)[2:] + ['2006'])
# For respiratory & skin sensitization, we need to split the strings.
                resp_only, skin_only = splitsens(chemsheet.row_values(31)[3:] + ['2006'])
                hazard_lists['resp_sens'].append([casrn, chemname, 'Respiratory sensitizer'] + resp_only)
                hazard_lists['skin_sens'].append([casrn, chemname, 'Skin sensitizer'] + skin_only)
                hazard_lists['mutagen'].append([casrn, chemname] + chemsheet.row_values(32)[2:] + ['2006'])
                hazard_lists['cancer'].append([casrn, chemname] + chemsheet.row_values(33)[2:] + ['2006'])
                hazard_lists['repr_tox'].append([casrn, chemname] + chemsheet.row_values(34)[2:] + ['2006'])
                hazard_lists['sys_single'].append([casrn, chemname] + chemsheet.row_values(35)[2:] + ['2006'])
                hazard_lists['sys_rept'].append([casrn, chemname] + chemsheet.row_values(36)[2:] + ['2006'])
                hazard_lists['asp_haz'].append([casrn, chemname] + chemsheet.row_values(37)[2:] + ['2006'])
# Environmental Hazards:
                hazard_lists['aq_acute'].append([casrn, chemname] + chemsheet.row_values(41)[2:] + ['2006'])
                hazard_lists['aq_chronic'].append([casrn, chemname] + chemsheet.row_values(42)[2:] + ['2006'])

# Test some things...
    print(hazard_lists['acute_oral'].find('61788-33-8'))
    
# Output one list of chemicals (& their classification info) per hazard class.
#     for h in hazard_lists:
#         with open('GHS-jp/output/' + h + '.csv', 'w') as csvfile:
#             listwriter = UnicodeWriter(csvfile)
#             listwriter.writerows(hazard_lists[h])
####### Really, we should be trying to write a CSV or XLS file that matches 
####### the CML upload template.

####### Need to incorporate the revisions by replacement, and new assessments.



# Korea GHS classification (2011)
def crunch_kr():
    chembook = xlrd.open_workbook('GHS-kr/GHS-kr-2011-04-15.xls')
    chemsheet = chembook.sheet_by_index(0)
# There are defined, and sometimes distinct, values for each row within 
# what appear as multi-row merged cells. This is good.
#   Name:           (r, 1)
#   CASRN:          (r, 3)
#   Hazard class    (r, 4)
#   Hazard category (r, 5)
#   Pictogram code? (r, 6)
#   unknown!        (r, 7)
#   H-stmnt code    (r, 8) - make a function to look up full H-statement!
#    print(chembook.encoding)
    for r in range(16,1209):
        haz_class_field = chemsheet.cell_value(r, 4)
        haz_class_num = haz_class_field[haz_class_field.find('('):].strip('()')
        haz_class_en = ''
# Make a function to look up the English name of the hazard class.
# For Acute Tox, need to deduce the exposure route too (can use Korean text)
# 급성 독성-경구(3.1) = Acute toxicity - oral (3.1)
# 급성 독성-경피(3.1) = Acute toxicity - dermal (3.1)
# 급성 독성-흡입(3.1) = Acute toxicity - inhalation (3.1)
# For Respiratory/Skin sensitization, we need to determine which.
# 피부 과민성(3.4) = Skin sensitization (3.4)
# 호흡기 과민성 (3.4) = Respiratory sensitization (3.4)
# For Aquatic Tox, need to deduce Acute or Chronic
# 수생환경유해성-급성(4.1) = Hazardous to the aquatic environment - acute (4.1)
# 수생환경유해성-만성(4.1) = Hazardous to the aquatic environment - chronic (4.1)
        if haz_class_num == '3.1':
            if u'급성 독성-경구' in haz_class_field:
                haz_class_en = 'Acute toxicity - oral (3.1)'
            elif u'급성 독성-경피' in haz_class_field:
                haz_class_en = 'Acute toxicity - dermal (3.1)'
            elif u'급성 독성-흡입' in haz_class_field:
                haz_class_en = 'Acute toxicity - inhalation (3.1)'
            else:
                print('Found a different hazard class 3.1 in row ' + str(r))
        if haz_class_num == '3.4':
            if u'피부 과민성' in haz_class_field:
                haz_class_en = 'Skin sensitization (3.4)'
            elif u'호흡기 과민성' in haz_class_field:
                haz_class_en = 'Respiratory sensitization (3.4)'
            else:
                print('Found a different hazard class 3.4 in row ' + str(r))
        if haz_class_num == '4.1':
            if u'수생환경유해성-급성' in haz_class_field:
                haz_class_en = 'Hazardous to the aquatic environment - acute (4.1)'
            elif u'수생환경유해성-만성' in haz_class_field:
                haz_class_en = 'Hazardous to the aquatic environment - chronic (4.1)'
            else:
                print('Found a different hazard class 4.1 in row ' + str(r))


def main():
    crunch_jp()
#    crunch_kr()

main()
