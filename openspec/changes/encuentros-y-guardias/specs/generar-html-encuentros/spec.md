## ADDED Requirements

### Requirement: Generar fragmento HTML del cronograma de encuentros
El sistema SHALL generar un fragmento HTML con el cronograma de encuentros de una materia, listo para copiar y pegar en el aula virtual del LMS. La salida incluye una tabla semántica con: fecha, hora, título, enlace, estado y grabación.

#### Scenario: Generar HTML para materia con encuentros
- **WHEN** un usuario solicita el bloque HTML para una materia que tiene encuentros programados
- **THEN** el sistema retorna un string HTML con una tabla `<table>` semántica
- **THEN** la tabla incluye columnas: Fecha, Hora, Título, Enlace, Estado, Grabación
- **THEN** cada encuentro es una fila `<tr>` en la tabla

#### Scenario: HTML para materia sin encuentros
- **WHEN** un usuario solicita el bloque HTML para una materia sin encuentros
- **THEN** el sistema retorna un párrafo `<p>` indicando "No hay encuentros programados"

#### Scenario: HTML incluye meet_url como link
- **WHEN** un encuentro tiene meet_url
- **THEN** el HTML muestra la columna Enlace como `<a href="{meet_url}">Link</a>`

#### Scenario: HTML incluye video_url como link
- **WHEN** un encuentro tiene video_url
- **THEN** el HTML muestra la columna Grabación como `<a href="{video_url}">Ver grabación</a>`
