# Política de seguridad

## Alcance

Los stacks de `compose/`, las reglas de Wazuh, Suricata, Falco y Tetragon, y los workflows de Shuffle. Es un laboratorio: los servicios escuchan en 127.0.0.1 por defecto (`SOC_BIND`) y todas las contraseñas salen de `.env`, que nunca se sube.

## Cómo reportar una vulnerabilidad

Si encuentras una vulnerabilidad, **no abras un issue público**. Escríbeme a
**contact@carlosvillalbalagos.com** o, si está activado, usa *Security → Report a
vulnerability* en este repositorio.

Incluye, si puedes:

- qué has encontrado y qué impacto tiene;
- cómo reproducirlo (una prueba de concepto ayuda);
- la versión o el commit afectado.

## Qué puedes esperar

- Acuse de recibo en 72 horas y una primera evaluación en 7 días.
- La corrección, coordinando contigo cuándo se publica, y el crédito por el hallazgo si lo quieres.

Se da soporte a lo que hay en la rama `main` de Infra-SocAnalyst.
