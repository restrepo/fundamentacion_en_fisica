/**
 * Crea en Google Forms las pruebas de entrada y salida de Fundamentación en Física
 * (capítulos 2, 3 y 4), como cuestionarios con clave, puntos y retroalimentación.
 *
 * Uso: script.google.com → Nuevo proyecto → pegar este archivo → ejecutar crearPruebas
 * → autorizar. Los enlaces quedan en el registro de ejecución y en la carpeta
 * «Pruebas de entrada y salida» de su Drive.
 */

const PRUEBAS = /*PRUEBAS*/;

function crearPruebas() {
  const carpeta = DriveApp.createFolder('Pruebas de entrada y salida');
  const enlaces = [];
  PRUEBAS.forEach(function (p) {
    const form = FormApp.create(p.titulo);
    form.setIsQuiz(true)
        .setDescription('Responda solo, sin consultar. No cuenta para la nota: queremos saber qué piensa.\n\n' + p.notacion)
        .setShuffleQuestions(false)
        .setLimitOneResponsePerUser(false)
        .setConfirmationMessage('¡Gracias! Sus respuestas quedaron registradas.');
    // El número de identificación empareja la entrada y la salida de cada estudiante.
    form.addTextItem()
        .setTitle('Número de identificación')
        .setHelpText('Solo números, sin puntos ni espacios. Use el mismo en la prueba de entrada y en la de salida.')
        .setRequired(true)
        .setValidation(FormApp.createTextValidation()
            .requireTextMatchesPattern('[0-9]{6,12}')
            .setHelpText('Escriba solo números (entre 6 y 12 dígitos), sin puntos ni espacios.')
            .build());

    form.addMultipleChoiceItem()
        .setTitle('¿Qué prueba presenta?')
        .setChoiceValues(['Entrada (al empezar el capítulo)', 'Salida (al terminar el capítulo)'])
        .setRequired(true);

    p.preguntas.forEach(function (q, i) {
      const item = form.addMultipleChoiceItem();
      item.setTitle((i + 1) + '. ' + q[0])
          .setChoices(q[1].map(function (texto, k) { return item.createChoice(texto, k === q[2]); }))
          .setPoints(1)
          .setRequired(true)
          .setFeedbackForCorrect(FormApp.createFeedback().setText(q[3]).build())
          .setFeedbackForIncorrect(FormApp.createFeedback().setText(q[3]).build());
    });

    const hoja = SpreadsheetApp.create('Respuestas · ' + p.titulo);
    form.setDestination(FormApp.DestinationType.SPREADSHEET, hoja.getId());
    DriveApp.getFileById(form.getId()).moveTo(carpeta);
    DriveApp.getFileById(hoja.getId()).moveTo(carpeta);

    enlaces.push(p.titulo + '\n  Para responder: ' + form.getPublishedUrl() +
                 '\n  Para editar:    ' + form.getEditUrl() +
                 '\n  Respuestas:     ' + hoja.getUrl());
  });
  Logger.log(enlaces.join('\n\n'));
}
