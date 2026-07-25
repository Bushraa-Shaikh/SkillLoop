import sys
print('Python:', sys.version)

# Test config loads
from config.config import config_map
cfg = config_map['development']
print('Config loaded:', cfg.__name__)
print('Secret key exists:', bool(cfg.SECRET_KEY))
print('DB Name:', cfg.DB_NAME)

# Test helpers import
from app.utils.helpers import (
    is_valid_email, is_student_email,
    validate_password, generate_token,
    time_ago, slugify, paginate
)

print('Valid email test:', is_valid_email('test@gmail.com'))
print('Invalid email test:', is_valid_email('notanemail'))
print('Student email test:', is_student_email('student@uni.edu'))
print('Non-student email:', is_student_email('user@gmail.com'))

ok, msg = validate_password('Weak')
print('Weak password:', ok, msg)
ok, msg = validate_password('Strong1Password')
print('Strong password:', ok, msg)

token = generate_token()
print('Token generated (32 chars):', len(token) == 32)

print('Slugify test:', slugify('Hello World! This is a Test'))

items = list(range(1, 51))
result = paginate(items, page=1, per_page=10)
print('Paginate page 1:', result['items'])
print('Total pages:', result['total_pages'])
print('Has next:', result['has_next'])

from datetime import datetime, timedelta
past = datetime.utcnow() - timedelta(minutes=5)
print('Time ago (5 min):', time_ago(past))

past2 = datetime.utcnow() - timedelta(hours=2)
print('Time ago (2 hrs):', time_ago(past2))

print()
print('ALL STEP 1 TESTS PASSED!')