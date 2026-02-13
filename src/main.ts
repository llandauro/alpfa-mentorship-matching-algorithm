function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Mentorship Tools')
    .addItem('Open Matcher Settings', 'showSidebar')
    .addToUi();
}

function showSidebar() {
  // Loads an HTML file that i would create in my src folder
  const html = HtmlService.createHtmlOutputFromFile('sidebar')
    .setTitle('Matching Settings')
    .setWidth(300);
  SpreadsheetApp.getUi().showSidebar(html);
}