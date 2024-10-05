function enviarEmails() {
  // Get the active spreadsheet and its active sheet
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  // Get the data range of the sheet
  var dataRange = sheet.getDataRange();
  // Retrieve values from the data range
  var data = dataRange.getValues();

  var assunto = 'Collaboration in Research on Brazilian Taxonomic Collections';

  // Use a Set to store unique emails
  var emailSet = new Set();

  // Iterate over the rows and extract emails
  for (var i = 1; i < data.length; i++) { // Start at 1 to skip the header row
    var emails = data[i][8]; // Assuming emails are in column I (index 8)
    if (emails) {
      var emailList = emails.split(','); // Split the string by commas
      for (var j = 0; j < emailList.length; j++) {
        var email = emailList[j].trim(); // Trim whitespace around the email
        if (email) { // Check if the email is not empty
          emailSet.add(email); // Add the email to the set
        }
      }
    }
  }

  // Iterate over the set of unique emails and send emails
  emailSet.forEach(function(email) {
    var mensagem = criarMensagemPersonalizada(email); // Create the personalized message
    MailApp.sendEmail(email, assunto, mensagem); // Send the email
    Logger.log('Email sent to: ' + email); // Log the sent email
  });
}

function criarMensagemPersonalizada(email) {
  // Example data that can be extracted from the spreadsheet
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var dataRange = sheet.getDataRange();
  var data = dataRange.getValues();
  
  // Search for the recipient in the spreadsheet
  for (var i = 1; i < data.length; i++) {
    var emails = data[i][8];
    var nome = data[i][1]; // Assuming names are in column B (index 1)
    if (emails) {
      var emailList = emails.split(',');

      for (var j = 0; j < emailList.length; j++) {
        var emailAtual = emailList[j].trim();
        if (emailAtual === email) {
          return 'Olá curador(a) da(o) ' + nome + ',\n\n' +
                 'Sou Mário Henrique de Assis Silva, mestrando no Programa Interunidades de Pós-Graduação em Bioinformática (PGBIOINFO) da Universidade Federal de Minas Gerais (UFMG).\n\n' +
                 'Estamos realizando um estudo sobre as coleções Taxonômicas brasileiras com a finalidade de verificar quais as características das coleções e dos dados sobre a coleção.\n\n' +
                 'Por isso, precisamos da sua colaboração em responder o questionário abaixo e divulgar para outros curadores da sua instituição:\n' +
                 'https://forms.gle/ZzjSX9hCWSfLJwLZ7\n\n'+
                 'Pedimos desculpas caso você já tenha recebido um e-mail semelhante e, se for o caso, por favor, ignore esta mensagem.\n\n'+
                 'Desde já, agradecemos sua atenção!\n\n' +
                 'Atenciosamente,\n' +
                 'Mário Henrique de Assis Silva';
        }
      }
    }
  }
  return 'Olá,\n\nEste é um e-mail genérico.\n\nAtenciosamente';
}
