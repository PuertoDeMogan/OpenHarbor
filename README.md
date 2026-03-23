<img width="1207" height="360" alt="logo@2" src="https://github.com/user-attachments/assets/d8695312-8424-44c6-b247-678fd5798e25" />


# Open Harbor — Integración para Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/PuertoDeMogan/openharbor)](https://github.com/PuertoDeMogan/openharbor/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Monitoriza datos de puertos marítimos directamente en Home Assistant. Open Harbor se conecta al repositorio [OpenHarbor Data](https://github.com/PuertoDeMogan/OpenHarbor_Data) y crea sensores automáticamente según los datos disponibles de cada puerto.

---

## Características

- 🌊 Monitorización en tiempo real de puertos marítimos
- 📡 Creación automática de sensores — sin configuración manual
- 🔄 Intervalo de actualización configurable (en minutos)
- 🏖️ Soporte multi-puerto — monitoriza varios puertos en una sola entrada
- 🔌 Sin clave de API — datos completamente abiertos

---

## Requisitos

- Home Assistant **2024.1.0** o superior
- [HACS](https://hacs.xyz) instalado

---

## Instalación

### Mediante HACS (recomendado)

1. Abre HACS en tu instancia de Home Assistant
2. Ve a **Integraciones** → menú de tres puntos → **Repositorios personalizados**
3. Añade `https://github.com/PuertoDeMogan/openharbor` como **Integración**
4. Busca **Open Harbor** y haz clic en **Descargar**
5. Reinicia Home Assistant

### Manual

<details>
  
<summary>Fuera de HACS</summary>  

1. Descarga la última versión desde [GitHub Releases](https://github.com/PuertoDeMogan/openharbor/releases)
2. Copia la carpeta `custom_components/openharbor/` en el directorio `config/custom_components/` de tu instalación de HA
3. Reinicia Home Assistant

</details>

---

## Configuración

Para añadir la integración a tu instancia de Home Assistant, usa el botón:
<p>
    <a href="https://my.home-assistant.io/redirect/config_flow_start?domain=openharbor" class="my badge" target="_blank">
        <img src="https://my.home-assistant.io/badges/config_flow_start.svg">
    </a>
</p>

### Configuración Manual
1. Ve a **Configuración → Integraciones → Añadir integración**
3. Busca **Open Harbor**
<img width="563" height="206" alt="image" src="https://github.com/user-attachments/assets/fa1b4b5f-7bba-47a2-bb3d-97facb7894ce" />

4. Selecciona los puertos que quieres monitorizar en el desplegable
5. Establece el intervalo de actualización (por defecto: 15 minutos)
<img width="561" height="310" alt="image" src="https://github.com/user-attachments/assets/196a5acf-3667-4cb5-9980-00b09196098a" />

6. Haz clic en **Enviar**

---

## Sensores

Los sensores se crean **dinámicamente** según los datos disponibles de cada puerto. El número y tipo de sensores puede variar entre puertos.

Sensores habituales:

| Sensor | Ejemplo | Unidad |
|---|---|---|
| Air Temperature | 22,3 | °C |
| Water Temperature | 19,5 | °C |
| Wind Speed | 14,2 | km/h |
| Wind Direction | 210 | ° |
| Wave Height | 0,8 | m |
| Humidity | 68 | % |
| Berths Available | 12 | — |
| Port Status | open | — |

> Los sensores nuevos que se añadan a los datos de un puerto aparecerán automáticamente en el siguiente ciclo de actualización — sin necesidad de reiniciar HA.

---

## Puertos disponibles

Los puertos se obtienen automáticamente desde el [repositorio OpenHarbor Data](https://github.com/PuertoDeMogan/OpenHarbor_Data/tree/main/ports). A medida que se añadan nuevos puertos al repositorio, estarán disponibles en el asistente de configuración de la integración.

Actualmente disponibles:

| Puerto | ID |
|---|---|
| Puerto de Mogán | `puerto_mogan` |

---

## Opciones

Tras la configuración inicial, puedes modificarla en cualquier momento:

1. Ve a **Configuración → Integraciones**
2. Localiza **Open Harbor** y haz clic en **Configurar**
3. Actualiza los puertos seleccionados o el intervalo de actualización
4. Haz clic en **Enviar** — la integración se recargará automáticamente

---

## Solución de problemas

**Los sensores no aparecen**
- Comprueba que tu instancia de Home Assistant tiene acceso a internet
- Verifica que la integración se cargó correctamente en **Configuración → Sistema → Registros**

**Error `cannot_connect` durante la configuración**
- La API de GitHub tiene un límite de 60 peticiones/hora para solicitudes no autenticadas. Espera unos minutos y vuelve a intentarlo.

**El sensor aparece como `no disponible`**
- El archivo JSON del puerto puede estar temporalmente inaccesible. La integración lo reintentará en el siguiente ciclo de actualización.

**Un sensor desapareció de los datos del puerto**
- HA mantiene la entidad como `no disponible`. Puedes eliminarla manualmente desde **Configuración → Entidades**.

---


## Contribuir

¡Las contribuciones son bienvenidas! Abre un issue o pull request en [GitHub](https://github.com/PuertoDeMogan/openharbor).

Para añadir un nuevo puerto, contribuye al [repositorio OpenHarbor Data](https://github.com/PuertoDeMogan/OpenHarbor_Data).

---

## Licencia

Licencia MIT — consulta el archivo [LICENSE](LICENSE) para más detalles.


