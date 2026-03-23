DOMAIN = "open_harbor"

DATA_REPO_OWNER = "PuertoDeMogan"
DATA_REPO_NAME = "OpenHarbor_Data"
DATA_REPO_BRANCH = "main"

PORTS_INDEX_URL = (
    f"https://api.github.com/repos/{DATA_REPO_OWNER}/{DATA_REPO_NAME}/contents/ports"
)
DATA_REPO_BASE_URL = (
    f"https://raw.githubusercontent.com/{DATA_REPO_OWNER}/{DATA_REPO_NAME}/{DATA_REPO_BRANCH}/ports"
)

DEFAULT_SCAN_INTERVAL = 15
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 1440

CONF_PORT_IDS = "port_ids"
CONF_SCAN_INTERVAL = "scan_interval"

ATTR_WRITABLE = "writable"
ATTR_SUBMISSION_ENDPOINT = "submission_endpoint"
