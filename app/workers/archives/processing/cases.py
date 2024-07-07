import os
import re
from datetime import datetime, date
import anthropic
import json

from ....schema.archives.cases import CreatePage

SECTIONS = ['Syllabus', 'Opinion', 'Dissent', 'Concurrence']


def process_legal_document(path):
    print("Processing legal document: ", path)
    text = read_document(path)
    print(text)
    print("Document read")
    case_name, case_date, case_source = extract_case_name_date_source(text[:10000])
    print("Case name and date extracted")
    sections = identify_sections(text)
    print("Sections identified")
    concurring_voice = sections["Concurring_Voice"]
    dissenting_voice = sections["Disagreeing_Voice"]
    pages = []
    
    for section_type, section_text in sections.items():
        if section_type in SECTIONS:
            section_pages = split_into_pages(section_type, section_text, concurring_voice, dissenting_voice)
            print(f"Pages split for {section_type}")
            pages = pages + section_pages
    print("Pages split")

    return pages, case_name, case_date, case_source


################################################################################
# Pages metadata extraction
################################################################################
def split_into_pages(section_type, section_text, concurring_voice, dissenting_voice):
    # Split section into logical paragraphs
    pages = []
    lines = section_text.split("\n")
    current_page = ""
    current_page_number = 1
    next_page_number = -1
    for line in lines:
        # If line start with a number followed by space or line ends with space followed by a number.
        next_page_number = extract_page_number(current_page_number, line)
        if next_page_number is not None:
            page = CreatePage(
                text=current_page,
                section_type=section_type,
                page_number=current_page_number,
                is_binding=is_binding_law(section_type),
                concurring_voice=concurring_voice if section_type == "Concurrence" else None,
                dissenting_voice=dissenting_voice if section_type == "Dissent" else None
            )
            pages.append(page)
            current_page_number = next_page_number
            current_page = ""
        else:
            current_page += line
    return pages


def extract_page_number(current_page_number, text):
    next_page_number = None
    # Pattern for page number at the beginning
    start_pattern = r'^(\d+)\s+\S'
    
    # Pattern for page number at the end
    end_pattern = r'\s+(\d+)$'
    
    # Check for page number at the beginning
    start_match = re.match(start_pattern, text)
    if start_match:
        next_page_number = int(start_match.group(1))
    
    # Check for page number at the end
    end_match = re.search(end_pattern, text)
    if end_match:
        next_page_number = int(end_match.group(1))
    
    if next_page_number is not None:
        print(f"Current page number: {current_page_number}, Next page number: {next_page_number}")
    if next_page_number != current_page_number + 1:
        return None
    # If no page number found, return None
    return next_page_number

def is_binding_law(section_type):
    return section_type == 'Opinion'

################################################################################
# Section identification functions
################################################################################
def identify_sections(text):
    # Use regex or other text analysis to identify major sections
    sections = {section: "" for section in SECTIONS}
    sections["Concurring_Voice"] = ""
    sections["Disagreeing_Voice"] = ""

    lines = text.split("\n")
    current_section = ""
    # FIXME: These are incredibly naive checks. We need to improve this.
    for i, line in enumerate(lines):
        #if i < 100:
        #    print(line)
        if "Syllabus" in line:
            current_section = "Syllabus"
        elif "Opinion of the Court" in line:
            current_section = "Opinion"
        elif ", concurring in the judgment." in line:
            # Extract the namme of the concurring justice: Get the text before the comma
            concurring_voice = line.split(",")[0]
            #re.sub(r"\s+", " ", concurring_voice)
            sections["Concurring_Voice"] += concurring_voice
            current_section = "Concurrence"
        elif ", dissenting." in line:
            dissenting_voice = line.split(",")[0]
            #re.sub(r"\s+", " ", dissenting_voice)
            sections["Disagreeing_Voice"] += dissenting_voice
            current_section = "Dissent"
        else:
            if current_section != "" and line != "":
                sections[current_section] += line + "\n"

    return sections


################################################################################
# Case metadata extraction functions
################################################################################
def extract_case_name_date_source(text : str):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    print('text: ', text)   
    SYSTEM_PROMPT = """
        You will be provided with the first few lines of a case file with decision under the Court. Your task is to extract the case name and date from the text.

        The case name is the title of the case and the date is the date of the decision. 
        
        You only need to provide the case name and date in the format: 
        {
        "case_name": {case_name},
        "case_date": {case_date}
        }

        Example:  
        {
        "case_name": "Daimler AG v. Bauman",
        "case_date": "01/14/1994"
        }
        """
    output = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.5,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Case: {text}"
                    }
                ]
            }
        ]
    )
    response = output.content[0].text
    print(response)
    # Extract case name and date from the response
    response_json = json.loads(response)
    if 'case_name' in response_json and 'case_date' in response_json:
        case_name, case_date = response_json['case_name'], response_json['case_date']
    else:
        case_name, case_date = None, None
    return case_name, case_date, None
    

def extract_case_name_date_source_from_path(path):
    file_name = os.path.basename(path)
    # Extract case name and date from the filename
    file_name = file_name.replace(".txt", "")
    file_name = file_name.replace(".pdf", "")
    file_name = file_name.replace("_", " ")
    #print(file_name)
    # Need to use regex to extract the case name and date: date (e.g. (01 14 2014)) is surrounded by parentheses and case name is separated by underscores
    date_pattern = r'\((\d+\s+\d+\s+\d+)\)'
    date_match = re.search(date_pattern, file_name)
    case_date = date_match.group(1)
    case_name = file_name.replace(f"({case_date})", "")
    # Also remove the number int-int from the case name
    case_name = re.sub(r'\d+-\d+', '', case_name)
    # Remove any leading or trailing spaces
    case_name = case_name.strip()
    # Express date in a proper format, converting to date object
    case_date = case_date.replace(" ", "/")
    case_date: date = datetime.strptime(case_date, "%m/%d/%Y").date()
    case_source = None # FIXME: Need to extract the source from the text
    print(case_name)
    print(case_date)
    return case_name, case_date, case_source

################################################################################
# Utility functions
################################################################################
def read_document(path):
    # Attempt to read the document with UTF-8 encoding
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        # If a UnicodeDecodeError occurs, try reading with 'ISO-8859-1' encoding
        with open(path, "r", encoding="ISO-8859-1") as f:
            text = f.read()
    return text

"""
if __name__ == "__main__":
    path = "/Users/amantimalsina/dev/ALETHIA/LAW/alethia-law/app/data/personal_jurisdiction/11-965_Daimler_AG_v._Bauman_(01_14_2014).txt"
    pages, case_name, case_date = process_legal_document(path)
    print(pages[65])
"""