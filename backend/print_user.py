from app.config import get_settings
url = get_settings().database_url
print(url.split('://')[1].split(':')[0])
