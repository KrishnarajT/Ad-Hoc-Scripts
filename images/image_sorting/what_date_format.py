import os
import re
from collections import Counter, defaultdict

# List of possible date regex patterns (non-separator forms first)
date_patterns = [
    (r'(\d{8})', 'YYYYMMDD'),   # 20250414
    (r'(\d{4})(\d{2})(\d{2})', 'YYYYMMDD'),
    (r'(\d{4})(\d{2})(\d{2})', 'YYYYDDMM'),
    (r'(\d{2})(\d{2})(\d{4})', 'DDMMYYYY'),
    (r'(\d{2})(\d{2})(\d{4})', 'MMDDYYYY'),
    (r'(\d{2})-(\d{2})-(\d{4})', 'DD-MM-YYYY'),
    (r'(\d{4})-(\d{2})-(\d{2})', 'YYYY-MM-DD'),
    (r'(\d{2})_(\d{2})_(\d{4})', 'DD_MM_YYYY'),
]

# Store parsed dates with their parts
parsed_dates = []

# Scan files in current directory
for file in os.listdir('.'):
    for pattern, label in date_patterns:
        match = re.search(pattern, file)
        if match:
            groups = match.groups()
            if len(groups) == 1:
                date_str = groups[0]
                parsed_dates.append((file, date_str))
            elif len(groups) == 3:
                parsed_dates.append((file, groups))
            break  # stop after first matching pattern

# If no dates found, exit
if not parsed_dates:
    print("No dates detected in filenames.")
    exit()

# Now check cap analysis
month_position_counter = Counter()
day_position_counter = Counter()
format_votes = Counter()

for file, date_parts in parsed_dates:
    if isinstance(date_parts, str) and len(date_parts) == 8:
        y, m, d = int(date_parts[0:4]), int(date_parts[4:6]), int(date_parts[6:8])
        month_position_counter['pos2'] += m <= 12
        day_position_counter['pos3'] += d <= 31
        format_votes['YYYYMMDD'] += (m <= 12 and d <= 31)
        
        m, d = int(date_parts[6:8]), int(date_parts[4:6])
        month_position_counter['pos3'] += m <= 12
        day_position_counter['pos2'] += d <= 31
        format_votes['YYYYDDMM'] += (m <= 12 and d <= 31)

    elif isinstance(date_parts, tuple):
        nums = list(map(int, date_parts))
        for idx, val in enumerate(nums):
            if val <= 12:
                month_position_counter[f'pos{idx+1}'] += 1
            if val <= 31:
                day_position_counter[f'pos{idx+1}'] += 1

        # Vote for most likely format (simplified logic)
        if nums[0] > 31 and nums[1] <= 12 and nums[2] <= 31:
            format_votes['YYYYMMDD'] += 1
        elif nums[0] <= 31 and nums[1] <= 12 and nums[2] > 31:
            format_votes['DDMMYYYY'] += 1

# Display analysis
print("\n📊 Month Position Counts:")
for k, v in month_position_counter.items():
    print(f"{k}: {v}")

print("\n📊 Day Position Counts:")
for k, v in day_position_counter.items():
    print(f"{k}: {v}")

print("\n📊 Format Votes:")
for fmt, count in format_votes.items():
    print(f"{fmt}: {count}")

# Most likely format
if format_votes:
    final_format = format_votes.most_common(1)[0][0]
    print(f"\n✅ Most likely date format: {final_format}")
else:
    print("\n❌ Could not confidently infer a date format.")
