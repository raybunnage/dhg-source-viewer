import dotenv
import os
from supabase import create_client

dotenv.load_dotenv()

print(os.environ["SUPABASE_URL"])
print(os.environ["SUPABASE_KEY"])

supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

# data = supabase.table("todos").insert({"name": "item 3"}).execute()

# data = supabase.table("todos").select("*").eq("name", "item 2").execute()

# print(data)
email = "rayb@seattlespineinstitute.com"
password = "a*2B13B0"
try:
    session = supabase.auth.sign_in_with_password(
        {"email": email, "password": password}
    )
    # print(session.session.access_token)
    # print(session)
except Exception as e:
    print(f"Error: {e}")

data = supabase.table("todos").select("*").execute()
print(f"data: {data}")

# supabase.postgrest.auth(session.access_token)

supabase.auth.sign_out()


# curl 'https://jdksnfkupzywjdfefkyj.supabase.co/rest/v1/todos?select=*' \
# -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impka3NuZmt1cHp5d2pkZmVma3lqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQxODkwMTMsImV4cCI6MjA0OTc2NTAxM30.035475oKIiE1pSsfQbRoje4-FRT9XDKAk6ScHYtaPsQ" \
# -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsImtpZCI6InVGOVpGaXdXV0hVT3lodlgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2pka3NuZmt1cHp5d2pkZmVma3lqLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiIwOWQ0ZDc4MS04N2VhLTQ5OTYtYjQwNi05NTE3ZjMxMjZiMmEiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzM0Njg1ODY3LCJpYXQiOjE3MzQ2ODIyNjcsImVtYWlsIjoicmF5YkBzZWF0dGxlc3BpbmVpbnN0aXR1dGUuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbCI6InJheWJAc2VhdHRsZXNwaW5laW5zdGl0dXRlLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiIwOWQ0ZDc4MS04N2VhLTQ5OTYtYjQwNi05NTE3ZjMxMjZiMmEifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTczNDY4MjI2N31dLCJzZXNzaW9uX2lkIjoiYzNhYjVhZmMtYTIyYy00OWM2LTg1MjMtNWQ0NDJmZTYyNjgwIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.2Kz6kG2F9jyj1L5jRhYa7OaH2JNdY6u7pK3lbiWeXzw"
