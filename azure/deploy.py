#!/usr/bin/env python3
# azure/deploy.py
"""
Python deployment script for the LinkedIn MCP Server on Azure Functions
Flexible Consumption plan.

Usage
-----
    python azure/deploy.py --app-name my-mcp-app --resource-group my-rg

    # Deploy infrastructure first (Bicep), then deploy code
    python azure/deploy.py --app-name my-mcp-app --resource-group my-rg --infra

    # Deploy code only (infrastructure already provisioned)
    python azure/deploy.py --app-name my-mcp-app --resource-group my-rg --code-only

Prerequisites
-------------
- Azure CLI installed and logged in  (``az login``)
- Python 3.12+
- The function app must already exist (created via Bicep or manually) unless
  ``--infra`` is also passed.

Bicep templates are in ``azure/bicep/``.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# Repository root = parent of this file's directory
REPO_ROOT = Path(__file__).resolve().parent.parent
BICEP_MAIN = REPO_ROOT / "azure" / "bicep" / "main.bicep"

# Files/dirs to include in the deployment ZIP
INCLUDE_PATTERNS = [
    "function_app.py",
    "host.json",
    "requirements.txt",
    "linkedin_mcp_server/**/*.py",
    "mcp_platform/**/*.py",
]

# Files/dirs to always exclude
EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "_archived", "azure", "tests"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(
    cmd: list[str], check: bool = True, capture: bool = False
) -> subprocess.CompletedProcess:
    """Run a subprocess command, logging and optionally raising on failure."""
    log.debug("Running: %s", " ".join(str(c) for c in cmd))
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=capture,
        text=True,
    )
    if check and result.returncode != 0:
        log.error(
            "Command failed (exit %d): %s",
            result.returncode,
            " ".join(str(c) for c in cmd),
        )
        if result.stderr:
            log.error("stderr: %s", result.stderr.strip())
        sys.exit(result.returncode)
    return result


def _az(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    """Run an Azure CLI command."""
    return _run(["az", *args], capture=capture)


def _check_az_login() -> None:
    """Verify the user is logged in to Azure CLI."""
    result = _az("account", "show", capture=True)
    if result.returncode != 0:
        log.error("Not logged in to Azure CLI.  Run: az login")
        sys.exit(1)
    account = json.loads(result.stdout)
    log.info("Azure subscription: %s (%s)", account["name"], account["id"])


def _check_dependencies() -> None:
    """Check that required CLI tools are available."""
    for tool in ("az",):
        result = subprocess.run(["which", tool], capture_output=True)
        if result.returncode != 0:
            log.error("Required tool not found: %s", tool)
            sys.exit(1)


# ---------------------------------------------------------------------------
# Infrastructure provisioning (Bicep)
# ---------------------------------------------------------------------------


def deploy_infrastructure(
    resource_group: str,
    location: str,
    app_name: str,
    linkedin_client_id: str = "",
    linkedin_client_secret: str = "",
    linkedin_access_token: str = "",
) -> dict:
    """
    Deploy Azure infrastructure using the Bicep templates.

    Creates (if not present):
    - Resource group
    - Storage account + deployment blob container
    - Service Bus namespace + queue
    - Log Analytics workspace + Application Insights
    - Function app (Flex Consumption plan)

    Returns:
        dict: Bicep deployment outputs (function app hostname, etc.)
    """
    log.info("Creating resource group '%s' in '%s' ...", resource_group, location)
    _az(
        "group",
        "create",
        "--name",
        resource_group,
        "--location",
        location,
        "--output",
        "none",
    )

    log.info("Deploying Bicep infrastructure ...")
    params = [
        f"appName={app_name}",
        f"location={location}",
    ]
    if linkedin_client_id:
        params.append(f"linkedInClientId={linkedin_client_id}")
    if linkedin_client_secret:
        params.append(f"linkedInClientSecret={linkedin_client_secret}")
    if linkedin_access_token:
        params.append(f"linkedInAccessToken={linkedin_access_token}")

    result = _az(
        "deployment",
        "group",
        "create",
        "--resource-group",
        resource_group,
        "--template-file",
        str(BICEP_MAIN),
        "--parameters",
        *params,
        "--output",
        "json",
        capture=True,
    )
    outputs = json.loads(result.stdout).get("properties", {}).get("outputs", {})
    log.info("Infrastructure deployed.  Outputs: %s", list(outputs.keys()))
    return {k: v["value"] for k, v in outputs.items()}


# ---------------------------------------------------------------------------
# Code packaging and deployment
# ---------------------------------------------------------------------------


def _build_zip(output_path: Path) -> None:
    """
    Build a deployment ZIP containing only the files needed by the function app.

    Flex Consumption plan deploys from a blob-stored ZIP package.
    """
    log.info("Building deployment package: %s", output_path)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for pattern in INCLUDE_PATTERNS:
            for path in REPO_ROOT.glob(pattern):
                # Skip excluded dirs and file types
                if any(part in EXCLUDE_DIRS for part in path.parts):
                    continue
                if path.suffix in EXCLUDE_SUFFIXES:
                    continue
                arcname = path.relative_to(REPO_ROOT)
                zf.write(path, arcname)
                log.debug("  + %s", arcname)
    log.info("Deployment package ready (%d bytes)", output_path.stat().st_size)


def deploy_code(resource_group: str, app_name: str) -> None:
    """
    Deploy the function code to an existing Flex Consumption function app.

    Uploads a ZIP package to the storage account and triggers a remote build.
    """
    zip_path = REPO_ROOT / "_build" / "deployment.zip"
    zip_path.parent.mkdir(exist_ok=True)
    _build_zip(zip_path)

    log.info("Deploying code to function app '%s' ...", app_name)
    _az(
        "functionapp",
        "deployment",
        "source",
        "config-zip",
        "--resource-group",
        resource_group,
        "--name",
        app_name,
        "--src",
        str(zip_path),
        "--build-remote",
        "true",
        "--output",
        "none",
    )
    log.info("Code deployment complete.")


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------


def smoke_test(hostname: str) -> bool:
    """Perform a basic health-check GET against the deployed function app."""
    import urllib.request
    import urllib.error

    url = f"https://{hostname}/api/health"
    log.info("Smoke test: GET %s", url)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            body = json.loads(resp.read())
            if body.get("status") == "healthy":
                log.info("✅ Health check passed: %s", body)
                return True
            log.warning("Health check returned unexpected body: %s", body)
    except urllib.error.URLError as exc:
        log.warning("Health check failed (function may still be warming up): %s", exc)
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deploy LinkedIn MCP Server to Azure Functions Flex Consumption plan"
    )
    parser.add_argument(
        "--app-name", required=True, help="Function app name (globally unique)"
    )
    parser.add_argument(
        "--resource-group", required=True, help="Azure resource group name"
    )
    parser.add_argument(
        "--location", default="eastus", help="Azure region (default: eastus)"
    )
    parser.add_argument(
        "--infra",
        action="store_true",
        help="Deploy infrastructure (Bicep) before deploying code",
    )
    parser.add_argument(
        "--code-only",
        action="store_true",
        help="Skip infrastructure, deploy code only",
    )
    parser.add_argument(
        "--no-smoke-test",
        action="store_true",
        help="Skip post-deployment health check",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    _check_dependencies()
    _check_az_login()

    hostname: str = f"{args.app_name}.azurewebsites.net"

    if args.infra and not args.code_only:
        outputs = deploy_infrastructure(
            resource_group=args.resource_group,
            location=args.location,
            app_name=args.app_name,
            linkedin_client_id=os.environ.get("LINKEDIN_CLIENT_ID", ""),
            linkedin_client_secret=os.environ.get("LINKEDIN_CLIENT_SECRET", ""),
            linkedin_access_token=os.environ.get("LINKEDIN_ACCESS_TOKEN", ""),
        )
        hostname = outputs.get("functionAppHostname", hostname)

    if not args.infra or not args.code_only:
        deploy_code(resource_group=args.resource_group, app_name=args.app_name)

    if not args.no_smoke_test:
        import time

        log.info("Waiting 15 s for the function app to start ...")
        time.sleep(15)
        smoke_test(hostname)

    log.info("")
    log.info("🎉 Deployment complete!")
    log.info("   Health:  https://%s/api/health", hostname)
    log.info("   MCP:     https://%s/api/mcp", hostname)


if __name__ == "__main__":
    main()
