from google import genai

API_KEY = "AQ.Ab8RN6JFXGS1MyyibrTz4jmKxyAOd-1XStbO8ZXqEf7gtGcQNg"

client = genai.Client(api_key=API_KEY)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Say hello in one sentence."
)

print(response.text)