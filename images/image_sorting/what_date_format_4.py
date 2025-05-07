import os
import re
from datetime import datetime
from collections import Counter
import dateutil.parser as dp

# List of regex patterns for various date formats, prioritizing YYYY >= 2000
DATE_PATTERNS = [
    r'(20\d{2})-(\d{2})-(\d{2})',            # YYYY-MM-DD (2000+)
    r'(20\d{2})(\d{2})(\d{2})',              # YYYYMMDD (2000+)
    r'(\d{2})-(\d{2})-(20\d{2})',            # DD-MM-YYYY or MM-DD-YYYY (2000+)
    r'(\d{2})/(\d{2})/(20\d{2})',            # DD/MM/YYYY or MM/DD/YYYY (2000+)
    r'(20\d{2})/(\d{2})/(\d{2})',            # YYYY/MM/DD (2000+)
    r'(\d{2})(\d{2})(20\d{2})',              # DDMMYYYY or MMDDYYYY (2000+)
    r'(\d{1,2})-(\w{3})-(20\d{2})',          # D-MMM-YYYY (2000+)
    r'(\w{3})\s+(\d{1,2}),\s+(20\d{2})',     # Mon DD, YYYY (2000+)
    r'(\d{1,2})\s+(\w{3})\s+(20\d{2})',      # DD Mon YYYY (2000+)
    r'(20\d{2})_(\d{2})_(\d{2})',            # YYYY_MM_DD (2000+)
    r'(\d{2})_(\d{2})_(20\d{2})',            # DD_MM_YYYY or MM_DD_YYYY (2000+)
    # Fallback patterns for ambiguous cases
    r'\d{4}-\d{2}-\d{2}',                    # YYYY-MM-DD
    r'\d{2}-\d{2}-\d{4}',                    # DD-MM-YYYY or MM-DD-YYYY
    r'\d{2}/\d{2}/\d{4}',                    # DD/MM/YYYY or MM/DD/YYYY
    r'\d{4}/\d{2}/\d{2}',                    # YYYY/MM/DD
    r'\d{4}\d{2}\d{2}',                      # YYYYMMDD
    r'\d{2}\d{2}\d{4}',                      # DDMMYYYY or MMDDYYYY
]

def try_parse_date(date_str, match_groups=None):
    """Attempt to parse a date string, prioritizing years >= 2000."""
    try:
        if match_groups:
            # Reconstruct date string from matched groups
            year = match_groups.get('year')
            month = match_groups.get('month', '01')
            day = match_groups.get('day', '01')
            if year and int(year) >= 2000:
                date_str = f"{year}-{month}-{day}"
        parsed_date = dp.parse(date_str, fuzzy=True, dayfirst=True, yearfirst=False)
        if parsed_date.year >= 2000:
            return parsed_date
    except (ValueError, TypeError):
        pass
    return None

def extract_dates_from_filename(filename):
    """Extract and parse dates from a filename, ensuring year >= 2000."""
    for pattern in DATE_PATTERNS:
        matches = re.finditer(pattern, filename)
        for match in matches:
            date_str = match.group(0)
            # Extract groups for patterns that explicitly capture year, month, day
            groups = match.groupdict()
            if not groups:
                # Named groups not used, assign based on pattern structure
                if pattern.startswith(r'(20\d{2})-(\d{2})-(\d{2})'):
                    groups = {'year': match.group(1), 'month': match.group(2), 'day': match.group(3)}
                elif pattern.startswith(r'(20\d{2})(\d{2})(\d{2})'):
                    groups = {'year': match.group(1), 'month': match.group(2), 'day': match.group(3)}
                elif pattern.endswith(r'-(20\d{2})'):
                    groups = {'day': match.group(1), 'month': match.group(2), 'year': match.group(3)}
                elif pattern.endswith(r'/(20\d{2})'):
                    groups = {'day': match.group(1), 'month': match.group(2), 'year': match.group(3)}
                elif pattern.startswith(r'(20\d{2})/'):
                    groups = {'year': match.group(1), 'month': match.group(2), 'day': match.group(3)}
                elif pattern.endswith(r'(20\d{2})'):
                    groups = {'day': match.group(1), 'month': match.group(2), 'year': match.group(3)}
            parsed_date = try_parse_date(date_str, groups)
            if parsed_date:
                return parsed_date
    return None

def get_common_date_format(dates):
    """Determine the most common date format from a list of dates."""
    if not dates:
        return "%Y-%m-%d"  # Default format
    
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
        for fmt, pattern in format_examples.items():
            try:
                formatted = date.strftime(fmt)
                if re.match(pattern, formatted):
                    format_counts[fmt] += 1
            except ValueError:
                continue
    
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