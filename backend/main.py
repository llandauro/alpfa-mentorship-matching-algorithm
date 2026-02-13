from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
from matchmaker import MatchingAlgorithm

app = FastAPI()

class MatchRequest(BaseModel):
    mentees: List[Dict]
    mentors: List[Dict]
    weights: Dict[str, int]

@app.post("/match")
async def run_match(data: MatchRequest):
    # convert incoming json to dataframes for matching algorithm
    df_mentees = pd.DataFrame(data.mentees)
    df_mentors = pd.DataFrame(data.mentors)
    
    # Initialize matching algorithm algorithm
    selector = MatchingAlgorithm(df_mentees, df_mentors, weights=data.weights)
    selector.run_matching() 
    
    return {"matches": selector.matches}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # if 0.0.0.0 fails, should try ipv4 address