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
  
  // 2. Map weights from the sheet to match Python's keys exactly
  const weights = {
    "Experience": settingsSheet.getRange("B2").getValue(),
    "Field":      settingsSheet.getRange("B3").getValue(),
    "CareerStage":settingsSheet.getRange("B4").getValue(),
    "Studies":    settingsSheet.getRange("B5").getValue(),
    "Objectives": settingsSheet.getRange("B6").getValue()
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
 * Takes the 'matches' array from FastAPI and writes it to the Results tab.
 */
function writeResultsToSheet(matchResponse) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let resultSheet = ss.getSheetByName("Results");
  
  if (!resultSheet) {
    resultSheet = ss.insertSheet("Results");
  }
  
  resultSheet.clear();

  // 1. Headers
  resultSheet.getRange(1, 1, 1, 2).setValues([["Mentor Name", "Mentee Name"]]);

  const matchData = matchResponse.matches; // This is now an array: [{mentor: "...", mentee: "..."}, ...]

  // 2. Map the array of objects into rows
  // We extract the specific values for 'mentor' and 'mentee' keys
  const output = matchData.map(match => [match.mentor, match.mentee]);

  if (output.length > 0) {
    // 3. Write the clean names to the sheet
    resultSheet.getRange(2, 1, output.length, 2).setValues(output);
    
    // Resizes columns for better visibility
    resultSheet.autoResizeColumns(1, 2);
    resultSheet.getRange("A1:B1").setFontWeight("bold");
  }
  
  SpreadsheetApp.getUi().alert("Matching Complete! Check the Results tab.");
}