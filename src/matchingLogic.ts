import { Participant } from "./types";
import { MatchSettings } from "./types";
import { MatchResponse } from "./types";

function callPythonMatcher(mentees: Participant[], mentors: Participant[], weights: MatchSettings): MatchResponse {
  const url = "http://0.0.0.0:8000"; // My FastAPI endpoint
  
  const options: GoogleAppsScript.URL_Fetch.URLFetchRequestOptions = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({
      mentees: mentees,
      mentors: mentors,
      weights: weights
    })
  };

  const response = UrlFetchApp.fetch(url, options);
  return JSON.parse(response.getContentText());
}