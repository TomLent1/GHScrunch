#!/usr/local/bin/python3.3

# ghscrunch.py
# Extract GHS hazard classification information for chemicals out of various
# international government documents, and output as a series of CSV files. 
# By Akos Kokai. 
# Uses the xlrd module (http://www.python-excel.org/).

import xlrd
import csv

def splitsens(texts):
# This is intended for splitting apart "Respiratory sensitizer:... 
# Skin sensitizer:..." in several cells in a row. I didn't strip off errant 
# hyphens, because in the symbol/signal/statement fields, '-' is used to 
# denote absence of the named hazard warning. For example, 
# "(Respiratory sensitizer)-" or "(Skin sensitizer)-"
    resp_list = []
    skin_list = []
    for x in texts:
        if "Skin" in x:
            a = x.find("Skin")
            resp_str = x[:a].rstrip(";([ \n\r")
            skin_str = x[a:].rstrip("; \n\r")
        else: 
            resp_str = skin_str = x.rstrip(" \n")
        resp_list = resp_list + [resp_str]
        skin_list = skin_list + [skin_str]
    return resp_list, skin_list

# Japan GHS classifications of 1424 chemicals, 2006
def crunch_jp_2006():
    GHS_jp_2006_files = [
        "GHS-jp/classification_result_e(ID001-100).xls",
        "GHS-jp/classification_result_e(ID101-200).xls",
        "GHS-jp/classification_result_e(ID201-300).xls",
        "GHS-jp/classification_result_e(ID301-400).xls",
        "GHS-jp/classification_result_e(ID401-500).xls",
        "GHS-jp/classification_result_e(ID501-600).xls",
        "GHS-jp/classification_result_e(ID601-700).xls",
        "GHS-jp/classification_result_e(ID701-800).xls",
        "GHS-jp/classification_result_e(ID801-900).xls",
        "GHS-jp/classification_result_e(ID901-1000).xls",
        "GHS-jp/classification_result_e(ID1001-1100).xls",
        "GHS-jp/classification_result_e(ID1101-1200).xls",
        "GHS-jp/classification_result_e(ID1201-1300).xls",
        "GHS-jp/classification_result_e(ID1301-1400).xls",
        "GHS-jp/classification_result_e(ID1401-1424).xls"
    ]

# These are all the hazard lists we will create.
    hazard_lists = {
        "explosive": [], "flamm_gas": [], "flamm_aer": [], "oxid_gas": [], 
        "gas_press": [], "flamm_liq": [], "flamm_sol": [], "self_react": [], 
        "pyro_liq": [], "pyro_sol": [], "self_heat": [], "water_fire": [], 
        "oxid_liq": [], "oxid_sol": [], "org_perox": [], "cor_metal": [], 
        "acute_oral": [], "acute_derm": [], "acute_gas": [], "acute_vap": [], 
        "acute_air": [], "skin_cor": [], "eye_dmg": [], "resp_sens": [], 
        "skin_sens": [], "mutagen": [], "cancer": [], "repr_tox": [], 
        "sys_single": [], "sys_rept": [], "asp_haz": [], "aq_acute": [], 
        "aq_chronic": []
    }
# These are the fields we will populate in each hazard list.
    list_header = ["CASRN", "Name", "Hazard class", 
                   "Classification", "Symbol", "Signal word", 
                   "Hazard statement", "Rationale for classification"]
    for h in hazard_lists:
        hazard_lists[h].append(list_header)

    for filename in GHS_jp_2006_files:
        chembook = xlrd.open_workbook(filename)
# Ignore the first sheet (it's just a list of chemicals in the workbook).
        for chempage in range(1, chembook.nsheets):
            chemsheet = chembook.sheet_by_index(chempage)
# Cells are identified by (row,col) where A1 is (0,0).
            casrn_field = chemsheet.cell_value(2,2)
            chemname = chemsheet.cell_value(1,3)
# We want one line for each CASRN.
            for casrn in casrn_field.split(","):
# We are going to extract columns 2 and onwards, for each of these rows.
# Hazard class name is in col 2, Classification in col 3, and so on...
# Physical Hazards:
                hazard_lists["explosive"].append([casrn, chemname] + chemsheet.row_values(5)[2:])
                hazard_lists["flamm_gas"].append([casrn, chemname] + chemsheet.row_values(6)[2:])
                hazard_lists["flamm_aer"].append([casrn, chemname] + chemsheet.row_values(7)[2:])
                hazard_lists["oxid_gas"].append([casrn, chemname] + chemsheet.row_values(8)[2:])
                hazard_lists["gas_press"].append([casrn, chemname] + chemsheet.row_values(9)[2:])
                hazard_lists["flamm_liq"].append([casrn, chemname] + chemsheet.row_values(10)[2:])
                hazard_lists["flamm_sol"].append([casrn, chemname] + chemsheet.row_values(11)[2:])
                hazard_lists["self_react"].append([casrn, chemname] + chemsheet.row_values(12)[2:])
                hazard_lists["pyro_liq"].append([casrn, chemname] + chemsheet.row_values(13)[2:])
                hazard_lists["pyro_sol"].append([casrn, chemname] + chemsheet.row_values(14)[2:])
                hazard_lists["self_heat"].append([casrn, chemname] + chemsheet.row_values(15)[2:])
                hazard_lists["water_fire"].append([casrn, chemname] + chemsheet.row_values(16)[2:])
                hazard_lists["oxid_liq"].append([casrn, chemname] + chemsheet.row_values(17)[2:])
                hazard_lists["oxid_sol"].append([casrn, chemname] + chemsheet.row_values(18)[2:])
                hazard_lists["org_perox"].append([casrn, chemname] + chemsheet.row_values(19)[2:])
                hazard_lists["cor_metal"].append([casrn, chemname] + chemsheet.row_values(20)[2:])
# Health Hazards:
                hazard_lists["acute_oral"].append([casrn, chemname] + chemsheet.row_values(24)[2:])
                hazard_lists["acute_derm"].append([casrn, chemname] + chemsheet.row_values(25)[2:])
                hazard_lists["acute_gas"].append([casrn, chemname] + chemsheet.row_values(26)[2:])
                hazard_lists["acute_vap"].append([casrn, chemname] + chemsheet.row_values(27)[2:])
                hazard_lists["acute_air"].append([casrn, chemname] + chemsheet.row_values(28)[2:])
                hazard_lists["skin_cor"].append([casrn, chemname] + chemsheet.row_values(29)[2:])
                hazard_lists["eye_dmg"].append([casrn, chemname] + chemsheet.row_values(30)[2:])
# For respiratory & skin sensitization, we need to split the strings.
                resp_only, skin_only = splitsens(chemsheet.row_values(31)[3:])
                hazard_lists["resp_sens"].append([casrn, chemname, "Respiratory sensitizer"] + resp_only)
                hazard_lists["skin_sens"].append([casrn, chemname, "Skin sensitizer"] + skin_only)
                hazard_lists["mutagen"].append([casrn, chemname] + chemsheet.row_values(32)[2:])
                hazard_lists["cancer"].append([casrn, chemname] + chemsheet.row_values(33)[2:])
                hazard_lists["repr_tox"].append([casrn, chemname] + chemsheet.row_values(34)[2:])
                hazard_lists["sys_single"].append([casrn, chemname] + chemsheet.row_values(35)[2:])
                hazard_lists["sys_rept"].append([casrn, chemname] + chemsheet.row_values(36)[2:])
                hazard_lists["asp_haz"].append([casrn, chemname] + chemsheet.row_values(37)[2:])
# Environmental Hazards:
                hazard_lists["aq_acute"].append([casrn, chemname] + chemsheet.row_values(41)[2:])
                hazard_lists["aq_chronic"].append([casrn, chemname] + chemsheet.row_values(42)[2:])

# Output one list of chemicals (& their classification info) per hazard class.
    for h in hazard_lists:
        with open(h + ".csv", "w", newline="") as csvfile:
            listwriter = csv.writer(csvfile, dialect='excel')
            listwriter.writerows(hazard_lists[h])


def main():
     crunch_jp_2006()

main()

# Japan GHS classifications of 52 chemicals, 2007
# ID index is in first sheet of each file.
# "GHS-jp/METI_H19_GHS_new_e.xls"
# "GHS-jp/METI_H19_GHS_review_e.xls"


# Japan GHS classifications of 93 chemicals, 2008
# ID index is in first sheet of each file.
# "GHS-jp/METI_H20_GHS_new_e.xls"
# "GHS-jp/METI_H20_GHS_review_e.xls"