import os
import re
from datetime import datetime
from collections import Counter
import dateutil.parser as dp

# List of regex patterns for various date formats
DATE_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}',                    # YYYY-MM-DD
    r'\d{2}-\d{2}-\d{4}',                    # DD-MM-YYYY or MM-DD-YYYY
    r'\d{2}/\d{2}/\d{4}',                    # DD/MM/YYYY or MM/DD/YYYY
    r'\d{4}/\d{2}/\d{2}',                    # YYYY/MM/DD
    r'\d{4}\d{2}\d{2}',                      # YYYYMMDD
    r'\d{2}\d{2}\d{4}',                      # DDMMYYYY or MMDDYYYY
    r'\d{1,2}-\w{3}-\d{2,4}',                # D-MMM-YY or DD-MMM-YYYY
    r'\w{3}\s+\d{1,2},\s+\d{4}',             # Mon DD, YYYY
    r'\d{1,2}\s+\w{3}\s+\d{4}',              # DD Mon YYYY
    r'\d{1,2}-\d{1,2}-\d{2}',                # DD-MM-YY or MM-DD-YY
    r'\d{1,2}/\d{1,2}/\d{2}',                # DD/MM/YY or MM/DD/YY
    r'\d{4}_\d{2}_\d{2}',                    # YYYY_MM_DD
    r'\d{2}_\d{2}_\d{4}',                    # DD_MM_YYYY or MM_DD_YYYY
]

def try_parse_date(date_str):
    """Attempt to parse a date string using dateutil.parser or custom logic."""
    try:
        # Prefer years in a reasonable range (e.g., 1900-2099)
        parsed_date = dp.parse(date_str, fuzzy=True, dayfirst=True, yearfirst=False)
        year = parsed_date.year
        # Adjust years that are likely misinterpreted (e.g., 0211 -> 2011)
        if year < 1900 or year > 2099:
            # Try to infer a more likely year by assuming a 2-digit year was intended
            match = re.match(r'(\d{2})(\d{2})(\d{2})', date_str) or re.match(r'(\d{2}).*?(\d{2}).*?(\d{2})', date_str)
            if match:
                day, month, year_suffix = match.groups()
                possible_year = int(f"20{year_suffix}")
                if 1900 <= possible_year <= 2099:
                    try:
                        # Reconstruct date string with a more likely year
                        new_date_str = date_str.replace(f"{day}{month}{year_suffix}", f"{possible_year}{month}{day}")
                        parsed_date = dp.parse(new_date_str, fuzzy=True, dayfirst=True)
                    except ValueError:
                        pass
        return parsed_date
    except ValueError:
        return None

def extract_dates_from_filename(filename):
    """Extract and parse dates from a filename using regex patterns."""
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, filename)
        for match in matches:
            parsed_date = try_parse_date(match)
            if parsed_date and 1900 <= parsed_date.year <= 2099:
                return parsed_date
    return None

def get_common_date_format(dates):
    """Determine the most common date format from a list of dates."""
    if not dates:
        return "%Y-%m-%d"  # Default format if no dates found
    
    # Convert dates to string representations in various formats
    format_counts = Counter()
    format_examples = {
        "%Y-%m-%d": r"\d{4}-\d{2}-\d{2}",
        "%d-%m-%Y": r"\d{2}-\d{2}-\d{4}",
        "%m/%d/%Y": r"\d{2}/\d{2}/\d{4}",
        "%Y/%m/%d": r"\d{4}/\d{2}/\d{2}",
        "%Y%m%d": r"\d{8}",
        "%d%m%Y": r"\d{8}",
        "%d-%b-%Y": r"\d{1,2}-\w{3}-\d{4}",
        "%b %d, %Y": r"\w{3}\s+\d{1,2},\s+\d{4}",
        "%d %b %Y": r"\d{1,2}\s+\w{3}\s+\d{4}",
    }
    
    for date in dates:
        date_str = date.strftime("%Y-%m-%d")
        for fmt, pattern in format_examples.items():
            try:
                # Try formatting the date and see if it matches the pattern
                formatted = date.strftime(fmt)
                if re.match(pattern, formatted):
                    format_counts[fmt] += 1
            except ValueError:
                continue
    
    # Return the most common format, or default if none found
    return format_counts.most_common(1)[0][0] if format_counts else "%Y-%m-%d"

def main():
    parsed_dates = []
    
    # Iterate through all files in the current directory
    for filename in os.listdir('.'):
        date = extract_dates_from_filename(filename)
        if date:
            parsed_dates.append(date)
            print(f"Found date {date.strftime('%Y-%m-%d')} in file: {filename}")
    
    if not parsed_dates:
        print("No valid dates found in any filenames.")
        return
    
    # Determine the most common date format
    common_format = get_common_date_format(parsed_dates)
    print(f"\nMost common date format: {common_format}")
    
    # Print all dates in the common format
    print("\nParsed dates in common format:")
    for date in parsed_dates:
        print(date.strftime(common_format))

if __name__ == "__main__":
    main()