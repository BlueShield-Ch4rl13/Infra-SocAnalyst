# 🚀 Advanced SOC Lab: eBPF, NIDS, SOAR & Local AI Integration

![Badge Status](https://img.shields.io/badge/Status-Completed-success)
![Wazuh](https://img.shields.io/badge/SIEM-Wazuh-blue)
![Tetragon](https://img.shields.io/badge/eBPF-Tetragon-orange)
![Shuffle](https://img.shields.io/badge/SOAR-Shuffle-purple)
![Ollama](https://img.shields.io/badge/AI-Ollama-black)

## 📋 Introducción

Este proyecto representa el diseño e implementación de un **Centro de Operaciones de Seguridad (SOC) de vanguardia**, desplegado en un entorno de laboratorio basado en Proxmox VE. 

El objetivo principal es proporcionar una capacidad integral de monitorización, detección de amenazas, gestión de incidentes y automatización de respuestas (SOAR). Destaca por la integración de tecnologías punteras como **eBPF (Extended Berkeley Packet Filter)** mediante Tetragon para la prevención a nivel de kernel, y el uso de **Inteligencia Artificial (IA) local (Ollama)** para el análisis semántico de alertas de seguridad frente a ataques simulados de Red Team.

---

## 🏗️ Arquitectura Técnica de Red e Infraestructura

El siguiente esquema detalla la topología de red, la segmentación de zonas, la ubicación del atacante y el flujo de telemetría y respuesta de incidentes.

```mermaid
flowchart TB
    %% Estilos de los nodos
    classDef cloud fill:#f3f4f6,stroke:#374151,stroke-width:2px;
    classDef fw fill:#fee2e2,stroke:#991b1b,stroke-width:2px;
    classDef dmz fill:#fef3c7,stroke:#92400e,stroke-width:2px;
    classDef endpoints fill:#d1fae5,stroke:#065f46,stroke-width:2px;
    classDef wazuh fill:#ffedd5,stroke:#9a3412,stroke-width:2px;
    classDef docker fill:#e0f2fe,stroke:#075985,stroke-width:2px;
    classDef api fill:#f3e8ff,stroke:#5b21b6,stroke-width:2px;
    classDef attacker fill:#fecaca,stroke:#b91c1c,stroke-width:2px,color:#7f1d1d;

    %% Entorno Externo y Atacante
    ATK["🥷 Máquina Atacante\n(Kali Linux / Red Team)"]:::attacker
    INET{{"INTERNET"}}:::cloud
    
    ATK --> INET
    
    %% Perímetro y Zona DMZ
    FW_EXT["🛡️ External Firewall / WAF"]:::fw
    WWW["🌐 Servidor Web\n(Zona DMZ)"]:::dmz
    
    INET <--> FW_EXT
    FW_EXT <--> WWW
    
    %% Red Interna / Core
    FW_INT["🛡️ Internal Firewall / Switch"]:::fw
    FW_EXT <--> FW_INT

    %% Zona de Clientes
    subgraph RED_CLIENTES ["Subred de Endpoints (Víctimas)"]
        direction LR
        WIN["💻 Win Client\n(Wazuh Agent)"]:::endpoints
        LIN["🐧 Linux Client\n(Wazuh Agent)"]:::endpoints
    end
    FW_INT <--> RED_CLIENTES

    %% Zona de Gestión SOC
    subgraph RED_SOC ["Subred de Gestión SOC"]
        direction TB
        WAZUH["🧠 Wazuh All-in-One\n(Manager, Indexer, Dashboard)\n[Wazuh Agent local]"]:::wazuh
        
        subgraph DOCKER_HOST ["🐳 Servidor Docker (Microservicios)"]
            direction LR
            DOCKER_SENSORS["📡 Stack Telemetría\n- Tetragon (eBPF)\n- Suricata (NIDS)\n- Prometheus / Grafana\n[Wazuh Agent local]"]:::docker
            
            DOCKER_SOAR["🤖 Stack SOAR e IA\n- Shuffle (Orquestador)\n- TheHive (Casos)\n- Ollama IA (Análisis)\n[Wazuh Agent local]"]:::docker
        end
        
        %% Conexión interna Docker
        DOCKER_SENSORS ---> DOCKER_SOAR
    end
    FW_INT <--> RED_SOC

    %% Zona de Inteligencia Externa
    subgraph APIS_EXTERNAS ["Inteligencia de Amenazas (CTI)"]
        direction TB
        VT["🦠 VirusTotal API"]:::api
        ABUSE["🚫 AbuseIP API"]:::api
    end

    %% --- FLUJOS DE DATOS ---
    
    %% 1. Flujos de Ataque (Líneas rojas punteadas)
    linkStyle 0,1,2,3,4 stroke:#b91c1c,stroke-width:2px;
    ATK -. "Ataque Web (Exploit)" .-> WWW
    ATK -. "Movimiento Lateral / C2" .-> WIN

    %% 2. Telemetría SOC (Líneas grises punteadas)
    WIN -. "Logs cifrados (Puerto 1514)" .-> WAZUH
    LIN -. "Logs cifrados (Puerto 1514)" .-> WAZUH
    DOCKER_SENSORS -. "eve.json / tetragon.log" .-> WAZUH

    %% 3. SOAR y Automatización (Líneas continuas gruesas)
    WAZUH == "Webhooks (Alertas Nivel > 10)" ==> DOCKER_SOAR
    DOCKER_SOAR == "Peticiones REST API" ==> APIS_EXTERNAS

```



