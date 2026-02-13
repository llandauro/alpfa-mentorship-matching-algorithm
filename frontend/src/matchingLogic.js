/**
 * Updates to accept the dynamic URL and adds the required ngrok header.
 */
function callPythonMatcher(apiUrl, mentees, mentors, weights) {
  // Ensure the URL ends with the /match endpoint
  const endpoint = apiUrl.endsWith('/') ? `${apiUrl}match` : `${apiUrl}/match`;
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      "ngrok-skip-browser-warning": "true" // CRITICAL: Bypasses the ngrok warning page
    },
    payload: JSON.stringify({
      mentees: mentees,
      mentors: mentors,
      weights: weights
    }),
    muteHttpExceptions: true // Helps with debugging if the server returns an error
  };

  const response = UrlFetchApp.fetch(endpoint, options);
  
  if (response.getResponseCode() !== 200) {
    throw new Error(`API Error (${response.getResponseCode()}): ${response.getContentText()}`);
  }

  return JSON.parse(response.getContentText());
}

/**
 * Grabs data from the sheets and triggers the process.
 */
function runMatchingFromSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const settingsSheet = ss.getSheetByName("Settings");
  
  if (!settingsSheet) throw new Error("Settings sheet not found! Please create a tab named 'Settings'.");
  
  // 1. Get the dynamic URL from cell B1
  const apiUrl = settingsSheet.getRange("B1").getValue().toString().trim(); 
  if (!apiUrl) throw new Error("Please enter your ngrok URL in cell B1 of the Settings tab.");
  
  // 2. Map weights from the sheet
  const weights = {
    field_weight: settingsSheet.getRange("B2").getValue(),
    experience_weight: settingsSheet.getRange("B3").getValue(),
    stage_weight: settingsSheet.getRange("B4").getValue()
  };

  // 3. Grab the data
  const mentees = getSheetData("Mentees");
  const mentors = getSheetData("Mentors");

  // 4. Call the API
  const results = callPythonMatcher(apiUrl, mentees, mentors, weights);

  // 5. Write back
  writeResultsToSheet(results);
}

/**
 * Converts a sheet's rows into an array of objects.
 * Assumes the first row contains the keys (Name, Field, etc.)
 */
function getSheetData(sheetName) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  if (!sheet) throw new Error(`Sheet "${sheetName}" not found!`);

  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const rows = data.slice(1);

  return rows.map(row => {
    const obj = {};
    headers.forEach((header, index) => {
      obj[header.toString().trim()] = row[index];
    });
    return obj;
  });
}

/**
 * Takes the 'matches' object from FastAPI and writes it to the Results tab.
 */
function writeResultsToSheet(matchResponse) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let resultSheet = ss.getSheetByName("Results");
  
  // Create the sheet if it doesn't exist
  if (!resultSheet) {
    resultSheet = ss.insertSheet("Results");
  }
  
  resultSheet.clear();
  resultSheet.getRange(1, 1, 1, 2).setValues([["Mentor Index/ID", "Mentee Index/ID"]]);

  const matchData = matchResponse.matches; // { "0": 1, "2": 0 }
  const output = Object.entries(matchData).map(([mentor, mentee]) => [mentor, mentee]);

  if (output.length > 0) {
    resultSheet.getRange(2, 1, output.length, 2).setValues(output);
  }
  
  SpreadsheetApp.getUi().alert("Matching Complete! Check the Results tab.");
}