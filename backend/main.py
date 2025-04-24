from fastapi import FastAPI

app = FastAPI(title="UALR chatbot API")   
@app.get("/") 
async def main_route():     
  return {"message": "Hey, It is me Goku"}