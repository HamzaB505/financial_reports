import re

def extract_info_from_query(query):
    # Define regex patterns for extracting information
    task_pattern = r"(calculate|retrieve|generate|compare|summarize|find|extract|provide|get)"
    task_type_pattern = r"(report|data|analysis|summary|information|statistics)"
    year_pattern = r"(\b20\d{2}\b)"  # Matches years like 2020, 2021, etc.
    quarter_pattern = r"(\b[1-4]Q\b|\bQ[1-4]\b|\b[1-4](st|nd|rd|th)?\s*(Q|quarter)\b)"  # Matches quarters like 1Q, Q1, 1st Q, 1st quarter, etc.
    company_pattern = r"\b(?:for|of|from|by)\s+([A-Za-z\s]+?)(?=\s+(?:\d{4}|\d(st|nd|rd|th)?\s*(Q|quarter)|report|data|information|summary|analysis|of))"

    # Extract task
    task_match = re.search(task_pattern, query, re.IGNORECASE)
    task = task_match.group(0) if task_match else None

    # Extract task type
    task_type_match = re.search(task_type_pattern, query, re.IGNORECASE)
    task_type = task_type_match.group(0) if task_type_match else None

    # Extract year
    year_match = re.search(year_pattern, query)
    year = year_match.group(0) if year_match else None

    # Extract quarter
    quarter_match = re.search(quarter_pattern, query, re.IGNORECASE)
    quarter = quarter_match.group(0) if quarter_match else None
    
    # Standardize quarter format to Q1, Q2, etc.
    if quarter:
        if re.search(r"\b1(st|Q|quarter)?\b", quarter, re.IGNORECASE):
            quarter = "Q1"
        elif re.search(r"\b2(nd|Q|quarter)?\b", quarter, re.IGNORECASE):
            quarter = "Q2"
        elif re.search(r"\b3(rd|Q|quarter)?\b", quarter, re.IGNORECASE):
            quarter = "Q3"
        elif re.search(r"\b4(th|Q|quarter)?\b", quarter, re.IGNORECASE):
            quarter = "Q4"
    
    # Extract company name
    company_match = re.search(company_pattern, query, re.IGNORECASE)
    if company_match:
        company = company_match.group(1).strip()
        # Remove leading articles and trailing keywords
        company = re.sub(r'^\b(the|a|an)\b\s+', '', company, flags=re.IGNORECASE)  # Remove leading 'the', 'a', 'an'
        company = re.sub(r'\s+(of|report|data|information|summary|analysis)$', '', company, flags=re.IGNORECASE)  # Remove trailing keywords
    else:
        company = None

    # Return extracted information as a dictionary
    return {
        "task": task,
        "task_type": task_type,
        "company": company,
        "year": year,
        "quarter": quarter
        
    }

