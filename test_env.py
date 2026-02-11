from dotenv import load_dotenv
import os

print("CWD:", os.getcwd())

env_path = os.path.join(os.getcwd(), ".env")
print("ENV EXISTS:", os.path.exists(env_path))
print("ENV PATH:", env_path)

load_dotenv(dotenv_path=env_path)

print("OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))
