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
    print("Document read")
    case_name, case_date, case_source = extract_case_name_date_source(text[:10000])
    print("Case name and date extracted")
    sections = identify_sections(text)
    print("Sections identified")
    concurring_voice = sections["Concurring_Voice"]
    dissenting_voice = sections["Disagreeing_Voice"]
    pages = []
    
    previous_page_number = 1
    for section_type, section_text in sections.items():
        if section_type in SECTIONS:
            starting_page_number = previous_page_number 
            extracted_starting_page_number = extract_starting_page_number(section_text[:1000])
            if extracted_starting_page_number is not None:
                if extracted_starting_page_number >= previous_page_number:
                    starting_page_number = extracted_starting_page_number
            section_pages, last_page_number = split_into_pages(section_type, section_text, concurring_voice, dissenting_voice, starting_page_number)
            print(f"Pages split for {section_type}")
            pages = pages + section_pages
            previous_page_number = last_page_number
    print("Pages split")

    return pages, case_name, case_date, case_source


################################################################################
# Pages metadata extraction
################################################################################
def split_into_pages(section_type, section_text, concurring_voice, dissenting_voice, starting_page_number):
    # Split section into logical paragraphs
    pages = []
    lines = section_text.split("\n")
    current_page = ""
    # Extract current page number
    current_page_number = starting_page_number
    print(f"Current page number: {current_page_number}")
    next_page_number = -1
    for line in lines:
        # If line start with a number followed by space or line ends with space followed by a number.
        next_page_number = extract_page_number(current_page_number, line)
        if next_page_number is not None:
            print(f"Current page number: {current_page_number}, Next page number: {next_page_number}")
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
            current_page += line + "\n"
    if current_page != "":
        page = CreatePage(
            text=current_page,
            section_type=section_type,
            page_number=current_page_number,
            is_binding=is_binding_law(section_type),
            concurring_voice=concurring_voice if section_type == "Concurrence" else None,
            dissenting_voice=dissenting_voice if section_type == "Dissent" else None
        )
        pages.append(page)
    return pages, current_page_number


def extract_starting_page_number(text):
    # Pattern for page number at the beginning
    start_pattern = r'^\s*(\d+)\s+\S'
    end_pattern = r'\s+(\d+)\s*$'

    start_match = re.match(start_pattern, text)
    if start_match:
        return int(start_match.group(1))
    
    end_match = re.search(end_pattern, text)
    if end_match:
        return int(end_match.group(1))
    else: 
        return None


def extract_page_number(current_page_number, text):
    # Pattern for page number at the begi
    start_pattern = r'^\s*(\d+)\s+\S'
    end_pattern = r'\s+(\d+)\s*$'
    
    # Check for page number at the beginning
    start_match = re.match(start_pattern, text)
    if start_match:
        if int(start_match.group(1)) == current_page_number + 1:
            return int(start_match.group(1))

    
    # Check for page number at the end
    end_match = re.search(end_pattern, text)
    if end_match:
        if int(end_match.group(1)) == current_page_number + 1:
            return int(end_match.group(1))
        
    return None

def is_binding_law(section_type):
    return section_type == 'Opinion'

################################################################################
# Section identification functions
################################################################################
def identify_sections(text):
    print("Identifying sections")
    print(text[:1000])
    """
    Identify the major sections of the legal document
    @param text: The text of the legal document
    @return: A dictionary containing the text of the major sections

    FIXME: This is a very naive implementation. We need to improve this.
    """
    # Use regex or other text analysis to identify major sections
    sections = {section: "" for section in SECTIONS}
    sections["Concurring_Voice"] = ""
    sections["Disagreeing_Voice"] = ""

    lines = text.split("\n")
    print("extracted lines...", len(lines))
    current_section = ""
    current_text = ""
    # FIXME: These are incredibly naive checks. We need to improve this.
    for i, line in enumerate(lines):
        #print(f"Processing line {i} out of {len(lines)}")
        #print(line, current_section)
        if line != "":
            # If line ends with "-" or "—", then we want to find the next non-empty line and append it to the end of line and continue
            if line[-1] == "-" or line[-1] == "—":
                # Find the next non-empty line
                next_line = ""
                for j in range(i+1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line != "":
                        break
                # Strip the "-" or "—" from the current line and append the next line
                line = line[:-1]
                next_line = next_line[1:]
                line = line + next_line
            current_text += line + "\n"
            if syllabus_section(line):
                if current_section != "":
                    sections[current_section] += current_text
                    current_text = ""
                current_section = "Syllabus"
            elif opinion_section(line):
                if current_section != "":
                    sections[current_section] += current_text
                    current_text = ""
                current_section = "Opinion"
            elif concurring_section(line):
                if current_section != "":
                    sections[current_section] += current_text
                    current_text = ""
                # Extract the namme of the concurring justice: Get the text before the comma
                concurring_voice = line.split(",")[0]
                #re.sub(r"\s+", " ", concurring_voice)
                sections["Concurring_Voice"] += concurring_voice
                current_section = "Concurrence"
            elif dissenting_section(line):
                if current_section != "":
                    sections[current_section] += current_text
                    current_text = ""
                dissenting_voice = line.split(",")[0]
                sections[current_section] += current_text
                #re.sub(r"\s+", " ", dissenting_voice)
                sections["Disagreeing_Voice"] += dissenting_voice
                current_section = "Dissent"
    sections[current_section] += current_text

    print("Sections identified")

    return sections

def syllabus_section(text):
    # This one's easy. Just check if the text contains the word "Syllabus"
    if "Syllabus" in text:
        #print("Syllabus section found")
        #print(text)
        return True

def opinion_section(text):
    # Use regex or other text analysis to identify the opinion section
    pattern = r"Opinion(\s+)of(\s+)the(\s+)Court"
    if re.search(pattern, text):
        #print("Opinion section found")
        return True
    return None

def concurring_section(text):
    # Use regex or other text analysis to identify the concurring voice section
    pattern = r",\s+concurring\s+in\s+the\s+judgment\."
    if re.search(pattern, text):
        #print("Concurring section found")
        #print(text)
        return True
    return None

def dissenting_section(text):
    # Use regex or other text analysis to identify the dissenting voice section
    pattern = r",\s+dissenting\."
    if re.search(pattern, text):
        #print("Dissenting section found")
        #print(text)
        return True
    return None


################################################################################
# Case metadata extraction functions
################################################################################
def extract_case_name_date_source(text : str):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    SYSTEM_PROMPT = """
        You will be provided with the first few lines of a case file with decision under the Court. Your task is to extract the case name and date from the text.

        The case name is the title of the case and the date is the date of the decision. 
        
        You only need to provide the case name and date in the format: 
        {
        "case_name": {case_name},
        "case_date": {case_date}
        }
        If only year is available, use 01/01/{year} as the date. Moreover, the case_name needs to be in the format: "Plaintiff v. Defendant" with proper capitalization (NOT all caps). 

        Example Reponse: 
        {
        "case_name": "Daimler AG v. Bauman",
        "case_date": "01/14/1994"
        }

        IMPORTANT: Just reply with the JSON format above; DO NOT say anything else. The response will be put into json.loads() to extract the case name and date.
        So, make sure the response is in the correct format.
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
    pattern = r'"case_name":\s*"(?P<case_name>[^"]+)",\s*"case_date":\s*"(?P<case_date>[^"]+)"'

    # Search for matches
    match = re.search(pattern, response)

    if match:
        case_name = match.group("case_name")
        case_date = match.group("case_date")
    else:
        case_name, case_date = None, None
    print(f"Case Name: {case_name}, Case Date: {case_date}")

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