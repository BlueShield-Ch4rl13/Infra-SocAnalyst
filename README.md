## 🗺️ Arquitectura Técnica

```mermaid
flowchart TB
    %% Definición de Estilos
    classDef proxmox fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef lxc fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef vm_siem fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef vm_win fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef vm_atk fill:#ffebee,stroke:#c62828,stroke-width:2px;
    classDef docker fill:#e3f2fd,stroke:#1565c0,stroke-width:1px,stroke-dasharray: 5 5;

    subgraph PROXMOX [Hypervisor: Proxmox VE]
        direction TB
        BRIDGE((Virtual Bridge\nvmbr0\nModo Promiscuo))

        subgraph RED_MGT [VLAN 10: Red de Gestión SOC]
            direction LR
            
            subgraph WAZUH_VM [VM: SRV-WAZUH / IP: 10.0.10.20]
                W_MAN(Wazuh Manager\nMotor de Reglas)
                W_IDX[(Wazuh Indexer\nBBDD Logs)]
                W_DASH[Wazuh Dashboard\nKibana UI]
            end

            subgraph SOC_LXC [LXC Privilegiado: SOC-CORE / IP: 10.0.10.10]
                W_AGT_LXC(Wazuh Agent\nLog Forwarder)
                PORTAINER[Portainer CE\nGestión Docker]
                
                subgraph DOCKER_STACK [Stack Docker Compose]
                    TETRAGON[Tetragon\neBPF Prevención]
                    SURICATA[Suricata\nNIDS / IPS]
                    PROMETHEUS[(Prometheus\nTSDB)]
                    GRAFANA[Grafana\nMétricas UI]
                end
            end
        end

        subgraph RED_ATK [VLAN 20: Red de Endpoints y Pruebas]
            direction LR
            
            subgraph WIN_VM [VM: WIN-CLIENT / IP: 10.0.20.100]
                W_AGT_WIN(Wazuh Agent)
                VULN_SVC[Servicios Vulnerables]
            end

            subgraph ATK_VM [VM: LINUX-ATK / IP: 10.0.20.110]
                RED_TEAM[Scripts Red Team\nNmap, Netcat]
            end
        end

        %% Conexiones Físicas / Capa 2
        SOC_LXC <--> BRIDGE
        WAZUH_VM <--> BRIDGE
        WIN_VM <--> BRIDGE
        ATK_VM <--> BRIDGE
        
        %% Interacciones Lógicas eBPF / NIDS
        TETRAGON -.->|Hook en Ring 0| PROXMOX
        SURICATA -.->|Sniffing Capa 2/3| BRIDGE
    end

    %% Asignación de clases
    class PROXMOX proxmox;
    class SOC_LXC lxc;
    class WAZUH_VM vm_siem;
    class WIN_VM vm_win;
    class ATK_VM vm_atk;
    class DOCKER_STACK docker;```

```mermaid
sequenceDiagram
    autonumber
    participant ATK as Atacante (VLAN 20)
    participant SUR as Suricata (NIDS Docker)
    participant TET as Tetragon (eBPF Docker)
    participant AGT as Wazuh Agent (LXC)
    participant MAN as Wazuh Manager (VM)
    participant KIB as Wazuh Dashboard (UI)

    %% Escenario 1: Ataque de Red
    rect rgb(255, 235, 238)
        Note over ATK, KIB: Escenario A: Reconocimiento de Red (Nmap)
        ATK->>SUR: Escaneo de puertos hostil
        SUR->>AGT: Escribe firma detectada en eve.json
        AGT->>MAN: Envía log cifrado (Puerto 1514)
        MAN->>MAN: Correlaciona regla (Nivel 8+)
        MAN-->>AGT: Ejecuta Active Response (firewall-drop)
        AGT->>SUR: Inyecta regla IPTables (Bloqueo IP)
        MAN->>KIB: Muestra alerta roja en el Dashboard
    end

    %% Escenario 2: Ataque a Nivel de Sistema
    rect rgb(227, 242, 253)
        Note over ATK, KIB: Escenario B: Intento de Reverse Shell / Volcado Credenciales
        ATK->>TET: Ejecuta binario ofuscado / Lee /etc/shadow
        TET->>TET: Intercepta syscall (sys_execve / sys_read)
        TET-->>ATK: Envía SIGKILL al proceso (Bloqueo < 1ms)
        TET->>AGT: Escribe evento de bloqueo en tetragon.log
        AGT->>MAN: Envía log cifrado de Kernel
        MAN->>KIB: Muestra alerta de prevención (eBPF Enforcement)
    end
```
