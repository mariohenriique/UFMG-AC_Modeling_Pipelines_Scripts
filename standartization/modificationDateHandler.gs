function onEdit(e) {
  // Get the active sheet where the edit occurred
  var sheet = e.source.getActiveSheet();
  var sheetName = sheet.getName();
  
  // Names of specific target sheets
  var targetSheetNames = ["Planilha 2024", "planilha_unificada"];
  
  // Check if the edit occurred in one of the specific sheets
  if (targetSheetNames.indexOf(sheetName) !== -1) {
    var editedCell = e.range;

    // Dynamically get the number of columns in the sheet
    var lastColumn = sheet.getLastColumn();
    
    // Check if the edit occurred in columns A to the last column, excluding column B (2), and not in rows 1 or 2
    if (editedCell.getColumn() >= 1 && editedCell.getColumn() <= lastColumn && editedCell.getColumn() !== 2 && editedCell.getRow() > 2) {
      var row = editedCell.getRow();
      var dateCell = sheet.getRange(row, 2); // Column B

      // Get the current date and remove the time
      var today = new Date();
      today.setHours(4, 0, 0, 0); // Set the time to 00:00:00

      // Check if the entire row is empty from columns A to the last column
      var range = sheet.getRange(row, 1, 1, lastColumn); // Range from A to the last column
      var values = range.getValues()[0]; // Get the values of the row as an array

      // Check if the row is empty
      var isRowEmpty = values.every(function(cell) {
        return cell === "" || cell === null;
      });

      if (isRowEmpty) {
        // If the row is completely empty, set the date cell to empty
        dateCell.setValue("");
      } else {
        // Get the current value of the date cell
        var currentDate = dateCell.getValue();
        if (currentDate instanceof Date) {
          // Remove the time from the current date in the cell
          currentDate.setHours(0, 0, 0, 0);
        } else {
          // If it's not a valid date, set currentDate to an invalid date
          currentDate = new Date(0);
        }

        // Update the cell with today's date only if it's different from the current date
        if (currentDate.getTime() !== today.getTime()) {
          dateCell.setValue(today);
        }
      }
    }
  }
}
