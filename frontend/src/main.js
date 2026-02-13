function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Mentorship Tools')
    .addItem('Run Matchmaker', 'runMatchingFromSheet')
    .addToUi();
}