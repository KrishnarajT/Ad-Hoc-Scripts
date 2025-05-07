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
    r'(\d{2})(\d{2})(20\d{2})',              # DDMMYYYY (2000+)
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
    r'\d{2}\d{2}\d{4}',                      # DDMMYYYY
]

# Mapping of patterns to their format strings
PATTERN_TO_FORMAT = {
    r'(20\d{2})-(\d{2})-(\d{2})': "%Y-%m-%d",
    r'(20\d{2})(\d{2})(\d{2})': "%Y%m%d",
    r'(\d{2})-(\d{2})-(20\d{2})': "%d-%m-%Y",
    r'(\d{2})/(\d{2})/(20\d{2})': "%d/%m/%Y",
    r'(20\d{2})/(\d{2})/(\d{2})': "%Y/%m/%d",
    r'(\d{2})(\d{2})(20\d{2})': "%d%m%Y",
    r'(\d{1,2})-(\w{3})-(20\d{2})': "%d-%b-%Y",
    r'(\w{3})\s+(\d{1,2}),\s+(20\d{2})': "%b %d, %Y",
    r'(\d{1,2})\s+(\w{3})\s+(20\d{2})': "%d %b %Y",
    r'(20\d{2})_(\d{2})_(\d{2})': "%Y_%m_%d",
    r'(\d{2})_(\d{2})_(20\d{2})': "%d_%m_%Y",
    r'\d{4}-\d{2}-\d{2}': "%Y-%m-%d",
    r'\d{2}-\d{2}-\d{4}': "%d-%m-%Y",
    r'\d{2}/\d{2}/\d{4}': "%d/%m/%Y",
    r'\d{4}/\d{2}/\d{2}': "%Y/%m/%d",
    r'\d{4}\d{2}\d{2}': "%Y%m%d",
    r'\d{2}\d{2}\d{4}': "%d%m%Y",
}

def try_parse_date(date_str, match_groups=None):
    """Attempt to parse a date string, prioritizing years >= 2000."""
    try:
        if match_groups:
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
            # Extract groups for patterns that capture year, month, day
            groups = match.groupdict()
            if not groups:
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
                # Return the parsed date and the format pattern that matched
                return parsed_date, pattern
    return None, None

def get_common_date_format(date_formats):
    """Determine the most common date format from a list of matched patterns."""
    if not date_formats:
        return "%Y-%m-%d"  # Default format
    
    # Count occurrences of each format
    format_counts = Counter(date_formats)
    
    # Map the most common pattern to its format string
    most_common_pattern = format_counts.most_common(1)[0][0]
    return PATTERN_TO_FORMAT.get(most_common_pattern, "%Y-%m-%d"), format_counts

def main():
    parsed_dates = []
    matched_formats = []
    folder_path = input("Enter the folder path containing images: ")
    if not os.path.isdir(folder_path):
        print("Invalid folder path")
        return
    # Iterate through all files in the current directory
    for filename in os.listdir(folder_path):
        date, pattern = extract_dates_from_filename(filename)
        if date and pattern:
            parsed_dates.append(date)
            matched_formats.append(pattern)
            print(f"Found date {date.strftime('%Y-%m-%d')} in file: {filename}")
    
    if not parsed_dates:
        print("No valid dates found in any filenames.")
        return
    
    # Determine the most common date format
    common_format, format_counts = get_common_date_format(matched_formats)
    print("\nFormat counts:")
    for pattern, count in format_counts.items():
        fmt = PATTERN_TO_FORMAT.get(pattern, "Unknown")
        print(f"{fmt}: {count} files")
    print(f"\nMost common date format: {common_format}")
    
    # Print all dates in the common format
    print("\nParsed dates in common format:")
    for date in parsed_dates:
        print(date.strftime(common_format))

if __name__ == "__main__":
    main()