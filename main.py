import re

import requests
from bs4 import BeautifulSoup

from constants import start_pattern_acquirer_company, start_pattern_acquirer_law_firm, start_pattern_acquiree_company, \
    start_pattern_acquiree_law_firm


def compile_pattern(start_pattern, end_pattern=None):
    start_pattern_escaped = re.escape(start_pattern)
    end_pattern_escaped = re.escape(end_pattern) if end_pattern else None
    start_pattern_space = re.sub(r'\\ ', '[ \xa0]', start_pattern_escaped)
    end_pattern_space = re.sub(r'\\ ', '[ \xa0]', end_pattern_escaped) if end_pattern_escaped else None
    if end_pattern:
        # return re.compile(rf'{re.escape(start_pattern)}(.*?){re.escape(end_pattern)}', re.DOTALL | re.IGNORECASE)
        return re.compile(rf'{start_pattern_space}(.*?){end_pattern_space}', re.DOTALL | re.IGNORECASE)
    # return re.compile(rf'{re.escape(start_pattern)}', re.DOTALL | re.IGNORECASE)
    return re.compile(rf'{start_pattern_space}(.*?){end_pattern_space}', re.DOTALL | re.IGNORECASE)

def get_index(text, patterns):
    for index, pattern in enumerate(patterns):
        compiled_pattern = compile_pattern(pattern)
        match = compiled_pattern.search(text)
        if match:
            return index
    return


def extract_section(text, start_patterns, end_patterns=None, buffer=5000):
    if end_patterns is None:
        for start_pattern in start_patterns:
            pattern = compile_pattern(start_pattern)
            try:
                match = list(pattern.finditer(text))[-1]
            except IndexError:
                continue
            match_index = match.start()
            return text[match_index:match_index+buffer]
    else:
        for start_pattern, end_pattern in zip(start_patterns, end_patterns):
            pattern = compile_pattern(start_pattern, end_pattern)
            match = pattern.search(text)
            if match:
                return match.group()


def extract_attorneys(section):
    # attorneys_regex = re.compile(r'(Attn|Attention):?\s+(.*?)(?=\s*(Email:|Fax:))', re.DOTALL | re.IGNORECASE | re.MULTILINE)
    attorneys_regex = re.compile(r'(Attn|Attention):?\s+(.*?)(?=(E-mail:|Fax:|\Z))',
                                 re.DOTALL | re.IGNORECASE | re.MULTILINE)
    matches = attorneys_regex.findall(section)
    attorneys = []
    for match in matches:
        cleaned_match = re.sub(r'\s*(Email:|Fax:).*', '', match[1], flags=re.IGNORECASE).strip()
        cleaned_match = cleaned_match.replace('\xa0', ' ')  # Replace non-breaking space with regular space
        lawyers = [name.strip() for name in cleaned_match.split('\n') if name.strip()]
        attorneys.extend(lawyers)
    return attorneys


def main(url):
    with requests.Session() as session:
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/96.0.4664.93 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8',
            'referer': '',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        response = session.get(url)
        response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    # index = get_index(text, start_pattern_acquiree_law_firm)
    #
    # if index is None:
    #     raise Exception("Could not find acquirer company update constants.py")

    acquirer_company_section = extract_section(text, start_pattern_acquirer_company, start_pattern_acquirer_law_firm)
    acquirer_law_firm_section = extract_section(text, start_pattern_acquirer_law_firm, start_pattern_acquiree_company)
    acquiree_company_section = extract_section(text, start_pattern_acquiree_company, start_pattern_acquiree_law_firm)
    acquiree_law_firm_section = extract_section(text, start_pattern_acquiree_law_firm)

    acquirer_company_attorneys = extract_attorneys(acquirer_company_section)
    acquirer_law_firm_attorneys = extract_attorneys(acquirer_law_firm_section)
    acquiree_company_attorneys = extract_attorneys(acquiree_company_section)
    acquiree_law_firm_attorneys = extract_attorneys(acquiree_law_firm_section)

    return {
        "Acquirer Company Attorneys": acquirer_company_attorneys,
        "Acquirer Law Firm Attorneys": acquirer_law_firm_attorneys,
        "Acquiree Company Attorneys": acquiree_company_attorneys,
        "Acquiree Law Firm Attorneys": acquiree_law_firm_attorneys,
    }


if __name__ == '__main__':
    for target_url in [
        "https://www.sec.gov/Archives/edgar/data/1458962/000119312519014341/d681305ddefm14a.htm#toc681305_80",
        "https://www.sec.gov/Archives/edgar/data/1608638/000119312519039441/d689911ddefm14a.htm#toc689911_37",
        "https://www.sec.gov/Archives/edgar/data/822662/000114420419015819/tv517048-defm14a.htm#t54dSOCB",
        "https://www.sec.gov/Archives/edgar/data/92679/000119312519014338/d663129ddefm14a.htm#toc663129_68",
        "https://www.sec.gov/Archives/edgar/data/1500213/000114420419010177/tv514515-defm14a.htm#t21SI",
        "https://www.sec.gov/Archives/edgar/data/1096376/000119312519026360/d671126ddefm14a.htm#rom671126_670",
        # does not follow standard
        # "https://www.sec.gov/Archives/edgar/data/1491576/000119312518349423/0001193125-18-349423-index.htm",
        # "https://www.sec.gov/Archives/edgar/data/726513/000119312519028348/d670753ddefm14a.htm#toc670753_45",
        # "https://www.sec.gov/Archives/edgar/data/918580/000114420419005036/tv510554-defm14a.htm#t92SE",
        # "https://www.sec.gov/Archives/edgar/data/1522420/000119312519014477/d660544ddefm14a.htm#toc",
        "https://www.sec.gov/Archives/edgar/data/1609951/000119312519017818/d659828ddefm14a.htm#toc",
        "https://www.sec.gov/Archives/edgar/data/1469510/000104746919000291/a2237603zdefm14a.htm#da71901_security_ownership_of_certain_beneficial_owners",
        "https://www.sec.gov/Archives/edgar/data/920424/000104746918007677/a2237352zdefm14a.htm#ds72301_security_ownership_of_certain___sec02525",
        "https://www.sec.gov/Archives/edgar/data/920424/000104746918007677/a2237352zdefm14a.htm#ds72301_security_ownership_of_certain___sec02525",
        "https://www.sec.gov/Archives/edgar/data/1630132/000119312518345505/d664298ddefm14a.htm#rom664298_79",
        "https://www.sec.gov/Archives/edgar/data/1697152/000119312518128788/d507706ds1a.htm#rom507706_15",
        "https://www.sec.gov/Archives/edgar/data/792130/000119312518326077/0001193125-18-326077-index.htm",
        "https://www.sec.gov/Archives/edgar/data/1299130/000119312518351266/d646626ddefm14a.htm#toc646626_84",
        "https://www.sec.gov/Archives/edgar/data/912750/000119312519004644/d683511ddefm14a.htm#toc662440_131",
        "https://www.sec.gov/Archives/edgar/data/1669812/000119312519013385/d688542ddefm14a.htm#toc688542_130",
        "https://www.sec.gov/Archives/edgar/data/726514/000114036118044685/s002523x2_defm14a.htm#tSOCB",
        "https://www.sec.gov/Archives/edgar/data/1681714/000104746918002420/a2235046zdef14a.htm#dk75101_security_ownership_of_certain___sec02525",
        "https://www.sec.gov/Archives/edgar/data/77159/000119312519061580/d654690ddefm14a.htm#rom654690_145",
        "https://www.sec.gov/Archives/edgar/data/1087423/000119312518347874/d654192ddefm14a.htm#rom654192_75",
        "https://www.sec.gov/Archives/edgar/data/1344596/000114036118042517/s002486x5_defm14c.htm#tSOCB",
        "https://www.sec.gov/Archives/edgar/data/1235007/000104746918007270/a2237105zdefm14a.htm#do46301_security_ownership_of_certain___sec02525",
        "https://www.sec.gov/Archives/edgar/data/1506401/000119312519002559/d647708ddefm14a.htm#toc647708_86",
        "https://www.sec.gov/Archives/edgar/data/1477425/000104746918007718/a2237381zdefm14a.htm#bg46001_table_of_contents",
        "https://www.sec.gov/Archives/edgar/data/1466815/000119312518329609/d627705ddefm14c.htm#tx627705_131",
        "https://www.sec.gov/Archives/edgar/data/1039101/000114036119003768/s002479x5_defm14a.htm#tCBOLCS",
        "https://www.sec.gov/Archives/edgar/data/1594337/000104746918006876/a2236974zex-99_a1a.htm#mG44308a_main_toc",
        "https://www.sec.gov/Archives/edgar/data/33619/000119312518339843/d622564ddefm14a.htm#toc622564_78",
        "https://www.sec.gov/Archives/edgar/data/1118237/000114036118045639/s002558x5_defm14a.htm#tBOM",
        "https://www.sec.gov/Archives/edgar/data/1364962/000119312518343681/d651525ddefm14a.htm#toc651525_80",
        "https://www.sec.gov/Archives/edgar/data/1176316/000114420418064298/tv508941-defm14a.htm#TOC",
        "https://www.sec.gov/Archives/edgar/data/1610532/000162828018014621/hortonworksdefm14a.htm#sC52DE8E270535247A60B40065FF3002D",
    ]:
        print(f"{main(target_url)}")
