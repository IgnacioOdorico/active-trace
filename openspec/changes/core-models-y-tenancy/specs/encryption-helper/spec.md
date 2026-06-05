## ADDED Requirements

### Requirement: encrypt cifra texto plano con AES-256-CBC
La función `encrypt(plaintext: str) -> str` SHALL cifrar el texto plano usando AES-256-CBC con HKDF derivado de `ENCRYPTION_KEY` y retornar el ciphertext en base64 con prefijo `[cifrado]`.

#### Scenario: Encrypt produce output con prefijo
- **WHEN** se cifra un texto plano "DNI 12345678"
- **THEN** el resultado SHALL comenzar con `[cifrado]`
- **AND** el resto SHALL ser una cadena base64 válida

#### Scenario: Encrypt es determinista con misma key
- **WHEN** se cifra el mismo texto plano dos veces con la misma `ENCRYPTION_KEY`
- **THEN** ambos ciphertext SHALL ser diferentes (diferente IV)
- **AND** ambos SHALL descifrar al mismo texto plano

### Requirement: decrypt descifra ciphertext a texto plano
La función `decrypt(ciphertext: str) -> str` SHALL recibir una cadena con prefijo `[cifrado]`, descifrar usando AES-256-CBC y retornar el texto plano original.

#### Scenario: Decrypt con ciphertext válido
- **WHEN** se descifra un ciphertext generado por `encrypt`
- **THEN** retorna el texto plano original

#### Scenario: Decrypt con ciphertext inválido
- **WHEN** se descifra un ciphertext con prefijo faltante o base64 inválido
- **THEN** SHALL lanzar `EncryptionError`

### Requirement: is_encrypted detecta formato cifrado
La función `is_encrypted(value: str) -> bool` SHALL retornar `True` si el valor comienza con `[cifrado]`.

#### Scenario: Valor cifrado detectado
- **WHEN** se evalúa un valor que comienza con `[cifrado]`
- **THEN** SHALL retornar `True`

#### Scenario: Valor no cifrado
- **WHEN** se evalúa un texto plano sin prefijo
- **THEN** SHALL retornar `False`

### Requirement: Nunca se loguean valores PII en claro
Las funciones de encriptación SHALL asegurar que ningún callback de logging o error trace exponga el texto plano (plaintext) en logs, excepciones o trazas.

#### Scenario: Excepción de decrypt no expone texto plano
- **WHEN** `decrypt` lanza `EncryptionError`
- **THEN** el mensaje de error NO SHALL contener el texto plano
