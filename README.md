# Infra-SocAnalyst
In Progress

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
