## 🗺️ Arquitectura Técnica

```mermaid

```

🚀 SOC Técnico Avanzado: eBPF, NIDS, SOAR AI-Integrado
📋 Introducción
Este proyecto representa el diseño e implementación de una plataforma de Centro de Operaciones de Seguridad (SOC) técnico avanzado y de vanguardia, destinada a un entorno de laboratorio o de red de pequeña empresa. El objetivo es proporcionar una capacidad de monitoreo, detección de amenazas, gestión de incidentes y automatización de respuestas con un enfoque en tecnologías de vanguardia como eBPF (Extended Berkeley Packet Filter) para la aplicación de políticas de seguridad a nivel de kernel y la integración de Inteligencia Artificial (IA) local para el análisis de amenazas.

La arquitectura se ha diseñado con un enfoque jerárquico y por zonas, optimizando la visibilidad y el control del tráfico.

🏗️ Esquema de Arquitectura Técnica (Mejorado)
El siguiente diagrama detalla la topología de red y la distribución de servicios del proyecto. Es una versión profesionalizada del boceto original, que proporciona una visión limpia y jerárquica.

🛠️ Desglose de Componentes
El proyecto se estructura en tres zonas principales de red: Zona Pública, Zona DMZ y Zona Interna.

🌐 Zona 1: Pública y DMZ
Esta zona maneja el tráfico entrante desde Internet y aloja servicios públicos.

Internet: Fuente de tráfico externo.

Main Firewall / WAF (Web Application Firewall): El primer punto de entrada, que actúa como un cortafuegos robusto y un WAF para proteger el servidor web de ataques a nivel de aplicación (como inyección SQL o Cross-Site Scripting).

Zona DMZ: Un segmento de red aislado que aloja el WWW Server (Servidor Web). Esta configuración garantiza que si el servidor web es comprometido, el atacante no tiene acceso directo a la red interna.

🧱 Zona 2: Cortafuegos Principal e Interno
Main Internal Firewall / Switch: El cortafuegos central que segmenta la DMZ de la red interna y la red interna de la pública. También actúa como el conmutador central de la red interna, orquestando el tráfico entre subredes.

🛡️ Zona 3: Red Interna
Esta zona aloja los sistemas críticos, los clientes y la infraestructura del SOC.

A. Subred de Servidores (Server Subnet)
Se compone de dos nodos de servidores principales que centralizan las operaciones de seguridad.

Central SOC Management Server (Wazuh AIO - All-in-One):

Wazuh Manager: El cerebro del SIEM, que recibe logs, alertas y telemetría de todos los agentes. Ejecuta reglas de correlación y análisis de archivos.

Wazuh Indexer: Una base de datos distribuida de búsqueda y análisis (reemplazo de Elasticsearch). Almacena y busca todos los datos de seguridad.

Wazuh Dashboard (Kibana): La interfaz gráfica de usuario para la visualización de datos, búsqueda de logs y gestión del SOC.

Wazuh Agent (Interno): Monitorea la salud del propio servidor de gestión.

Consolidated Security Services Host (Host de Servicios de Seguridad Consolidado - Docker-Enabled):
Un servidor dedicado que aloja múltiples contenedores Docker, organizados lógicamente en dos áreas principales.

Pila de Telemetría (Telemetry Stack):

Suricata (NIDS/IPS): Un sistema de detección y prevención de intrusiones de red (NIDS/IPS) que analiza el tráfico de red interno para identificar actividad maliciosa. Sus alertas se envían al Wazuh Manager.

Tetragon (eBPF Enforcement): Un motor de observabilidad y aplicación de políticas de seguridad basado en eBPF. Se ejecuta directamente en el kernel de Linux para interceptar llamadas al sistema (syscalls), archivos y sockets, permitiendo aplicar políticas de "denegación por defecto" a nivel de kernel y detener procesos maliciosos en milisegundos.

Prometheus: Una base de datos de series temporales para el almacenamiento de métricas locales. Recopila métricas de rendimiento de los contenedores Docker y los servicios de seguridad.

Grafana: Una plataforma de visualización de datos que se conecta a Prometheus para proporcionar cuadros de mando locales sobre la salud y el rendimiento de los servicios de seguridad internos.

Pila de Incidentes y SOAR (Incidents & SOAR Processing Stack):

Shuffle (SOAR Workflow Automation): Una plataforma de orquestación, automatización y respuesta de seguridad (SOAR) sin código. Shuffle es el núcleo de la automatización: recibe alertas de Wazuh, orquesta flujos de trabajo (workflows), interactúa con APIs externas y crea casos en TheHive.

TheHive (Incident Management/Case Ticketing): Una plataforma de gestión de incidentes de seguridad escalable y de código abierto. TheHive es donde los analistas del SOC documentan, rastrean y gestionan los incidentes.

Ollama IA (IA de Análisis de Amenazas - Artificial Intelligence): Una instancia local de Ollama que ejecuta modelos de lenguaje (como Llama 3) para analizar telemetría cruda, resumir alertas complejas y proporcionar contexto sobre amenazas sin necesidad de enviar datos a la nube.

Wazuh Agent (Consolidado): Un agente de Wazuh instalado en el host Docker que monitorea la salud del host, recolecta logs de los contenedores y envía la telemetría al Wazuh Manager.

B. Subred de Clientes (Client Subnet)
Win Client (Cliente Windows): Estación de trabajo Windows monitoreada con un agente de Wazuh.

Linux Client (Cliente Linux): Estación de trabajo o servidor Linux monitoreado con un agente de Wazuh.

Ambos agentes envían logs y alertas al Wazuh Manager central.

🌐 Zona 4: Integraciones Externas
Zonas Inteligencia de Amenazas Externas y APIs:
Un box dedicado que representa las integraciones con servicios externos para enriquecer los datos de seguridad.

VirusTotal: API para consultar la reputación de archivos y direcciones IP sospechosas.

AbuseIP: API para consultar la reputación de direcciones IP.

Shuffle es el componente central que interactúa de manera bi-direccional con estas APIs externas para automatizar la recopilación de inteligencia de amenazas.

🔁 Flujo de Datos y Automatizaciones
El proyecto destaca por su flujo de datos eficiente y sus capacidades de automatización.

1. Recopilación de Telemetría y Alertas
Agentes de Wazuh (Clientes, Docker Host): Recolectan logs de archivos, eventos de sistema, estado de archivos y telemetría de Docker y los envían de forma cifrada al Wazuh Manager.

Tetragon (eBPF): Envía telemetría detallada de eventos de kernel a nivel de sistema al agente consolidado, que lo reenvía al Wazuh Manager.

Suricata (NIDS): Envía alertas de tráfico de red sospechoso al agente consolidado, que lo reenvía al Wazuh Manager.

2. Análisis y Visualización
Wazuh Manager: Recibe todos los datos y aplica reglas de correlación. Si se cumple una regla (por ejemplo, "Intento de ejecución de binario malicioso en kernel bloqueado por Tetragon" o "Ataque de red detectado por Suricata"), genera una alerta.

Wazuh Indexer: Almacena la alerta.

Wazuh Dashboard: Permite a los analistas visualizar la alerta.

3. Automatización de Respuestas (SOAR)
Wazuh Manager: Cuando se genera una alerta crítica, el Manager dispara una integración automatizada (un Webhook HTTP POST) hacia Shuffle.

Shuffle (SOAR): Recibe la alerta JSON. El flujo de trabajo de Shuffle (workflow) puede entonces automágicamente:

Consultar la reputación de la IP atacante en VirusTotal y AbuseIP.

Enviar la telemetría cruda de Tetragon a Ollama IA para obtener un resumen inteligible.

Crear un Caso en TheHive, rellenando los campos con la alerta de Wazuh, los resultados de las APIs externas y el resumen de la IA.

Enviar una notificación al canal de comunicación del equipo de seguridad (por ejemplo, Slack o Discord).

🚀 Pila Tecnológica y Protocolos
Plataforma SOC: Wazuh (AIO), agentes de Wazuh.

Seguridad de Red: Main Firewall / WAF, Suricata (NIDS/IPS).

Seguridad de Kernel/Sistema: Tetragon (eBPF).

Gestión de Incidentes: TheHive.

Automatización/SOAR: Shuffle.

Observabilidad: Prometheus, Grafana.

IA de Análisis: Ollama IA.

APIs Externas: VirusTotal, AbuseIP.

Contenerización: Docker, Docker Compose (para el Host de Servicios).

Protocolos Clave: HTTPS (para dashboards y APIs), SSH (para gestión), gRPC/custom Wazuh Protocols (para comunicación agente-manager).

📝 Conclusión y Futuras Mejoras
Este proyecto demuestra un enfoque integrado y moderno para un SOC, centralizando la detección, el análisis y la respuesta. La inclusión de eBPF y la IA local lo posicionan como un laboratorio de seguridad técnico de vanguardia.

Futuras Mejoras:

Implementar clustering de Wazuh Indexer para alta disponibilidad.

Desplegar un pfSense como el cortafuegos principal para un monitoreo de red más detallado a nivel de zona.

Añadir herramientas de análisis forense como Velociraptor para la respuesta remota a incidentes.
