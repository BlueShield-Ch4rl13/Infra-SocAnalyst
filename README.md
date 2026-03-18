# Infra-SocAnalyst
In Progress

# 🛡️ Next-Gen Active SOC: eBPF & SOAR Integration

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![eBPF](https://img.shields.io/badge/Tech-eBPF_Tetragon-orange)
![Wazuh](https://img.shields.io/badge/SIEM-Wazuh-blue)

Este repositorio contiene la arquitectura, configuraciones y scripts de despliegue para un **Centro de Operaciones de Seguridad (SOC) de Defensa Activa**. Implementado sobre Proxmox VE, combina observabilidad de Kernel (Ring 0) con orquestación de respuesta en red.

## 🌟 Características Principales
* **Prevención en Microsegundos:** Uso de **Cilium Tetragon (eBPF)** para matar procesos maliciosos (`SIGKILL`) interceptando llamadas al sistema (`sys_execve`, `tcp_connect`).
* **Detección de Red (NIDS):** Inspección profunda de paquetes con **Suricata** en modo promiscuo virtual.
* **Orquestación y Respuesta (SOAR):** Centralización con **Wazuh** y baneos dinámicos mediante *Active Response*.
* **Observabilidad Avanzada:** Métricas de rendimiento de políticas en tiempo real con **Prometheus y Grafana**.

## 🚀 Guía de Despliegue Rápido (Quick Start)

1. **Configurar Host (Proxmox):** Desplegar un contenedor LXC Privilegiado (Ubuntu 24.04).
2. **Ejecutar Setup:**
   ```bash
   git clone [https://github.com/tu-usuario/NextGen-SOC-eBPF.git](https://github.com/tu-usuario/NextGen-SOC-eBPF.git)
   cd NextGen-SOC-eBPF/scripts
   chmod +x setup_soc.sh && ./setup_soc.sh

sequenceDiagram
    participant Atacante as Atacante (Win10)
    participant Suricata as Suricata (LXC)
    participant Agent as Wazuh Agent (LXC)
    participant Manager as Wazuh Manager (SIEM)
    participant FW as IPTables (Firewall)

    Atacante->>Suricata: Lanza Nmap Scan (T1595)
    Suricata->>Agent: Genera alerta en eve.json
    Agent->>Manager: Envía log codificado
    Manager->>Manager: Correlaciona con Regla Nivel 8+
    Manager-->>Agent: Dispara orden "Active Response"
    Agent->>FW: Ejecuta script 'firewall-drop'
    FW-->>Atacante: Bloquea IP Origen (Drop Traffic)
    Manager->>Kibana: Registra Incidente Crítico


flowchart TB
    subgraph PVE [Proxmox VE - Capa de Virtualización Física]
        direction TB
        
        subgraph VLAN10 [VLAN 10 - Red de Gestión y Seguridad SOC]
            direction LR
            subgraph VM1 [VM Ubuntu: SRV-WAZUH]
                direction TB
                WMAN[Wazuh Manager]
                WIDX[Wazuh Indexer]
                KIB[Kibana Dashboard]
            end

            subgraph LXC1 [LXC Privilegiado: SOC-CORE]
                direction TB
                WAGT[Wazuh Agent]
                subgraph DOCKER [Docker Compose Stack]
                    TET[Tetragon - eBPF]
                    SUR[Suricata - NIDS]
                    PRO[Prometheus]
                    GRA[Grafana]
                end
            end
        end

        subgraph VLAN20 [VLAN 20 - Red de Pruebas y Ataque]
            direction LR
            subgraph VM2 [VM Windows 10: WIN-CLIENT]
                WAGT2[Wazuh Agent]
                VULN[Sistema Vulnerable]
            end

            subgraph VM3 [VM Ubuntu: LINUX-CLI]
                ATK[Scripts Red Team\nNmap, Netcat, Curl]
            end
        end
        
        %% Conexiones lógicas de red y monitorización
        VLAN20 -.-> |Tráfico monitorizado por\nSuricata a través de vmbr0| VLAN10
        WAGT -.-> |Envío de logs JSON| WMAN
        WAGT2 -.-> |Envío de eventos Win| WMAN
        
        %% Acción de bloqueo
        TET ==> |Bloqueo SIGKILL\nen Kernel| LXC1
    end
    
    classDef vm fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef lxc fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef atck fill:#ffebee,stroke:#d32f2f,stroke-width:2px;
    
    class VM1,VM2 vm;
    class LXC1 lxc;
    class VM3 atck;



graph LR
    A[Script Malicioso\n'cat /etc/shadow'] --> B(Espacio de Usuario)
    B --> C{Llamada al Sistema\nsys_execve}
    
    subgraph Kernel Space (Ring 0)
        C --> D[eBPF Kprobe / Tracepoint]
        D --> E{Política Tetragon}
        E -- Coincide (Denegar) --> F[Señal SIGKILL]
        E -- No Coincide --> G[Ejecución Normal]
    end
    
    F --> H[Proceso Terminado en microsegundos]
    F --> I[Log a Wazuh]
