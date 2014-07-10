import calendar
from collections import OrderedDict
import re

from django import template

register = template.Library()

first_letter = re.compile(r'\b[a-z]')
not_all_caps = re.compile(r'[a-gi-ru-z]')  # CLFs, DHAs, 75th
patronymic = re.compile(r"(Mac|Mc|'|-)([a-z])")
# @see http://blog.apastyle.org/apastyle/2012/03/title-case-and-sentence-case-capitalization-in-apa-style.html
lower_case_words = ('and', 'by', 'for', 'of', 'the', 'to')
upper_case_words = ('CCSVI', 'DSME', 'MLA', 'NDP', 'RCMP')

abbreviations = [
    # Mixed-case abbreviations
    ('Comm.', 'Committee'),
    ('Educ.', 'Education'),
    ('Fed.', 'Federal'),
    ('Fin.', 'Finance'),
    ("Gov't.", 'Government'),
    ("Gov't", 'Government'),
    ('Prem.', 'Premier'),
    ('Prov.', 'Provincial'),
    ('Res.', 'Resolution'),
    ('Yar.', 'Yarmouth'),

    # Ambigious abbreviations
    ('ADDICTION SERV.', 'Addiction Services'),
    ('ASSAULT SERV.', 'Assault Services'),
    ('CARE SERV.', 'Care Services'),
    ('COM. SERV.', 'Community Services'),
    ('COMMUN. SERV.', 'Community Services'),
    ('EMERGENCY SERV.', 'Emergency Services'),
    ('OXYGEN SERV.', 'Oxygen Services'),
    ('PSYCHOLOGY SERV.', 'Psychology Services'),
    ('ACAD. FED.', 'Acadian Federation'),
    ('TURKEY FED.', 'Turkey Federation'),
    ('TIM HORTONS HOSP.', 'Tim Hortons Hospitality'),
    ('GAS REG.', 'Gas Regulation'),
    ('REG. Nurse', 'Registered Nurse'),

    # Uppercase abbreviations
    ('ADMIN.', 'Administration'),
    ('ADV.', 'Advanced'),
    ('AFFS.', 'Affairs'),
    ('AGRIC.', 'Agriculture'),
    ('AMT.', 'Amount'),
    ('ANNA.', 'Annapolis'),
    ('ANNIV.', 'Anniversary'),
    ('APPT.', 'Appointment'),
    ('ASSOC.', 'Association'),
    ('ATL.', 'Atlantic'),
    ('AUTH.', 'Authority'),
    ('BD.', 'Board'),
    ('BDS.', 'Boards'),
    ('BDS', 'Boards'),
    ('BLDG.', 'Building'),
    ('BLDGS.', 'Buildings'),
    ('BUS.', 'Business'),
    ('CAN.', 'Canada'),
    ('CAP.', 'Capital'),
    ('CDN.', 'Canadian'),
    ('CENT.', 'Central'),
    ('CFLs', 'Compact Fluorescent Lamps'),
    ('CONS.', 'Consolidated'),
    ('CORP.', 'Corporation'),
    ('CTR.', 'Centre'),
    ('CTR', 'Centre'),
    ('CTRS.', 'Centres'),
    ('CO.', 'County'),
    ('COL.', 'Colchester'),
    ('COS.', 'Counties'),
    ('COM.', 'Community'),
    ('COMM.', 'Committee'),
    ('COMMN.', 'Commission'),
    ('COMMUN.', 'Community'),
    ('COMP.', 'Competition'),
    ('CONGRATS.', 'Congratulations'),
    ('CONST.', 'Construction'),
    ('COUN.', 'Council'),
    ('CUMB.', 'Cumberland'),
    ('DART.', 'Dartmouth'),
    ('DEP.', 'Deputy'),
    ('DEPT.', 'Department'),
    ('DEV.', 'Development'),
    ('DIST.', 'District'),
    ('EAST.', 'Eastern'),
    ('ECON.', 'Economic'),
    ('ED.', 'Education'),
    ('EDUC.', 'Education'),
    ('ELEM.', 'Elementary'),
    ('EMERG.', 'Emergency'),
    ('ENVIRON.', 'Environment'),
    ('EQUIP.', 'Equipment'),
    ('EXEC.', 'Executive'),
    ('EXECS.', 'Executives'),
    ('FAM.', 'Family'),
    ('FDN.', 'Foundation'),
    ('FED.', 'Federal'),
    ('FIN.', 'Finance'),
    ('FISH.', 'Fisheries'),
    ('FL.', 'Floor'),
    ('GEN.', 'General'),
    ("GOV.'T.", 'Government'),
    ("GOV'T.", 'Government'),
    ("GOV'T", 'Government'),
    ('GRAD.', 'Graduate'),
    ('GRAD', 'Graduate'),
    ('GRADS.', 'Graduates'),
    ('GRADS', 'Graduates'),
    ('HBR.', 'Harbour'),
    ('HFX.', 'Halifax'),
    ('HOSP.', 'Hospital'),
    ('HR.', 'Hour'),
    ('HWY.', 'Highway'),
    ('IND.', 'Industry'),
    ('INFO.', 'Information'),
    ('INFO', 'Information'),
    ('INIT.', 'Initiative'),
    ('INSTIT.', 'Institute'),
    ('INTL.', 'International'),
    ('LBR.', 'Labour'),
    ('LEG.', 'Legislative'),
    ('LOC.', 'Local'),
    ('LTD.', 'Limited'),
    ('LUN.', 'Lunenburg'),
    ('LWR.', 'Lower'),
    ('MAR.', 'Maritime'),
    ('MED.', 'Medical'),
    ('MGT.', 'Management'),
    ('MIN.', 'Minister'),
    ('MUN.', 'Municipal'),
    ('N.S.', 'Nova Scotia'),
    ('NAT.', 'Natural'),
    ("NAT'L.", 'National'),
    ('NATL.', 'National'),
    ('PAYT.', 'Payment'),
    ('PERF.', 'Performance'),
    ('PKG.', 'Package'),
    ('PMT.', 'Payment'),
    ('PR', 'Public Relations'),
    ('PREM.', 'Premier'),
    ('PREM', 'Premier'),
    ('PROG.', 'Program'),
    ('PROGS.', 'Programs'),
    ('PROJ.', 'Project'),
    ('PROV.', 'Provincial'),
    ('PUB.', 'Public'),
    ('RD.', 'Road'),
    ('RDS.', 'Roads'),
    ('REF.', 'Reference'),
    ('REG.', 'Regional'),
    ('REGS.', 'Regulations'),
    ('REPT.', 'Report'),
    ('REPTS.', 'Reports'),
    ('RES.', 'Resources'),
    ('RTE.', 'Route'),
    ('RYL.', 'Royal'),
    ('S.', 'South'),
    ('SEPT.', 'September'),
    ('SO.', 'South'),
    ('SCH.', 'School'),
    ('SOC.', 'Society'),
    ('SERV.', 'Service'),
    ('SM.', 'Small'),
    ('SRV.', 'Services'),
    ('STA.', 'Station'),
    ('STATS.', 'Statistics'),
    ('TECH.', 'Technician'),
    ('TECHS.', 'Technicians'),
    ('TEL.', 'Telephone'),
    ('W.', 'West'),
    ('YAR.', 'Yarmouth'),
    ('YR.', 'Year'),
    ('YRS.', 'Years'),

    # Acronyms
    ('B.C.', 'British Columbia'),
    ('C.B.', 'Cape Breton'),
    ('CBRM', 'Cape Breton Regional Municipality'),
    ('CNSOPB', 'Canada-Nova Scotia Offshore Petroleum Board'),
    ('DHA', 'District Health Authorities'),
    ('DHAs', 'District Health Authorities'),
    ('DSTN', 'DSME Trenton Ltd'),
    ('EECD', 'Education and Early Childhood Development'),
    ('EI', 'Employment Insurance'),
    ('EIBI', 'Early Intensive Behavioural Intervention'),
    ('EMO', 'Emergency Management Office'),
    ('ERDT', 'Economic and Rural Development and Tourism'),
    ('HRM', 'Halifax Regional Municipality'),
    ('LAE', 'Labour and Advanced Education'),
    ('LFA', 'Lobster Fishing Area'),
    ('LWD', 'Labour and Workforce Development'),
    ('MOU', 'Memorandum of Understanding'),
    ('N.B.', 'New Brunswick'),
    ('NSGEU', 'Nova Scotia Government and General Employees Union'),
    ('NSLC', 'Nova Scotia Liquor Corporation'),
    ('NSP', 'Nova Scotia Power'),
    ('OAS', 'Old Age Security'),
    ('P.E.I.', 'Prince Edward Island'),
    ('PSC', 'Public Service Commission'),
    ('RRFB', 'Resource Recovery Fund Board'),
    ('SNS', 'Service Nova Scotia'),
    ('SNSMR', 'Service Nova Scotia and Municipal Relations'),
    ('SWSDA', 'South West Shore Development Authority'),
    ('TIR', 'Transportation and Infrastructure Renewal'),
    ('URB', 'Utility and Review Board'),
    ('WCB', "Workers' Compensation Board"),

    # Must come after "P.E.I.".
    ('E.', 'East'),
]

patterns = []
for old, new in abbreviations:
    pattern = r'\b' + re.escape(old)
    if not old.endswith('.'):
        pattern += r'\b'
    patterns.append((re.compile(pattern), new))

@register.filter()
def month_name(month_number):
    return calendar.month_name[month_number]

def upper_case_match(match):
    return match.group(0).upper()

@register.filter()
def heading(string):
    if not_all_caps.match(string):
        return string
    else:
        for pattern, repl in patterns:
          string = pattern.sub(repl, string)
        words = []
        for word in string.split(' '):
            word = word.lower()
            if not word in lower_case_words:
                word = first_letter.sub(upper_case_match, word)
            words.append(word)
        return ' '.join(words)

def capitalize_patronymic(match):
    return match.group(1) + match.group(2).upper()

@register.filter()
def speaker_name(name):
    if not_all_caps.match(name):
        return name
    else:
        return ' '.join(patronymic.sub(capitalize_patronymic, component.lower().capitalize()) for component in name.split(' '))

@register.filter()
def speech_class(speech):
    if speech.speaker_id:
        return 'person'
    elif speech.speaker_display:
        return 'role'
    else:
        return 'narrative'
