from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

##############################
#### Enable CORS 
##############################
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## ####################################################
## Endpoints
## ####################################################
from endpoints import air_qualities, cats, feedings, foods, poops, telephone_numbers, weights

app.include_router(air_qualities.router)
app.include_router(cats.router)
app.include_router(feedings.router)
app.include_router(foods.router)
app.include_router(poops.router)
app.include_router(telephone_numbers.router)
app.include_router(weights.router)

# Reroute to the docs
@app.get("/")
async def docs_redirect():
    return RedirectResponse(url='/docs')

# Start the server
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)