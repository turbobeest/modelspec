"""Execute the advertised MCP tools against explicitly configured API origins."""

from __future__ import annotations

import json
import re
from time import perf_counter
from urllib.parse import urlencode, urlparse

import httpx
from jsonschema import Draft202012Validator

USER_AGENT = "modelspec-agent-scenarios (+https://github.com/turbobeest/modelspec)"
PRODUCTION_HOSTS = {
    "modelspec.dev",
    "www.modelspec.dev",
    "api.modelspec.dev",
    "modelspec-7np.pages.dev",
}


def require_nonproduction(url: str) -> str:
    parsed = urlparse(url)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "API and export origins must be HTTP origins without credentials or queries"
        )
    if parsed.hostname.lower().rstrip(".") in PRODUCTION_HOSTS:
        raise ValueError("The scenario runner refuses production ModelSpec origins")
    return url.rstrip("/")


def tool_result(envelope: dict) -> dict:
    return {
        "content": [{"type": "text", "text": json.dumps(envelope)}],
        "isError": envelope["status"] == 0 or envelope["status"] >= 400,
    }


def attempted_facets(arguments) -> list[str]:
    """Extract identifiers, not enum values, from the contract's condition/objective forms."""
    ids = set()

    def condition(node):
        if isinstance(node, str):
            match = re.match(r"\s*([a-z][a-z0-9_.-]*)\s*(?:=|!=|<|>|\bin\b|\bnot\b|\bis\b)", node)
            if match:
                ids.add(match[1])
        elif isinstance(node, dict):
            for k, v in node.items():
                if k == "facet" and isinstance(v, str):
                    ids.add(v)
                elif k in ("all", "any", "not"):
                    condition(v)
        elif isinstance(node, list):
            for item in node:
                condition(item)

    if not isinstance(arguments, dict):
        return []
    condition(arguments.get("where", []))
    if isinstance(arguments.get("capabilities"), dict):
        ids.update(arguments["capabilities"])
    optimize = arguments.get("optimize", {})
    if isinstance(optimize, dict):
        for k, v in optimize.items():
            if k in ("max", "min") and isinstance(v, str):
                ids.add(v.lstrip("-").split(" @")[0])
            if k == "weights" and isinstance(v, dict):
                ids.update(x.lstrip("-").split(" @")[0] for x in v)
            if k == "pareto" and isinstance(v, list):
                ids.update(x.lstrip("-").split(" @")[0] for x in v if isinstance(x, str))
            if k == "lexicographic" and isinstance(v, list):
                for step in v:
                    if isinstance(step, dict):
                        ids.update(
                            step[side].split(" @")[0]
                            for side in ("max", "min")
                            if isinstance(step.get(side), str)
                        )
    return sorted(ids)


class LiveTools:
    def __init__(self, config: dict, tools: list[dict], key: str | None, client: httpx.Client):
        self.api = require_nonproduction(config["api_base_url"])
        self.export = require_nonproduction(config["export_base_url"])
        self.vocabulary_path, self.split = config["vocabulary_path"], config["data_split"]
        if self.vocabulary_path not in ("/v1/vocabulary", "/api/decision/vocabulary.json"):
            raise ValueError("Unsupported vocabulary path")
        self.definitions = {t["name"]: t for t in tools}
        self.key, self.client = key, client
        self.valid_ids: set[str] | None = None

    def validate(self, name: str, arguments) -> dict | None:
        errors = []
        if name not in self.definitions:
            errors = ["Unknown MCP tool"]
        else:
            validator = Draft202012Validator(self.definitions[name]["input_schema"])
            errors = [f"{e.json_path}: {e.message[:300]}" for e in validator.iter_errors(arguments)]
        if errors:
            return {
                "result": tool_result(
                    {
                        "origin": None,
                        "status": 400,
                        "body": {"error": {"code": "mcp_validation", "issues": errors}},
                    }
                ),
                "latency_ms": None,
                "validation_errors": errors,
                "unknown_facets": [],
                "api_call": False,
            }
        return None

    def prepare(self, name: str, arguments: dict) -> dict:
        # Zod objects strip unknown keys unless .passthrough() or .strict() is
        # declared. The decision Spec and feedback are already strict.
        if name in ("vocab", "model_info", "list_use_cases"):
            known = self.definitions[name]["input_schema"].get("properties", {})
            return {k: v for k, v in arguments.items() if k in known}
        if name not in ("rank", "policy_check"):
            return arguments
        value = json.loads(json.dumps(arguments))
        properties = self.definitions[name]["input_schema"]["properties"]
        for key in ("environment", "constraints") if name == "rank" else ("policy",):
            if not isinstance(value.get(key), dict):
                continue
            allowed = properties[key]["properties"]
            if key == "policy":
                for block, fields in allowed.items():
                    if isinstance(value[key].get(block), dict):
                        value[key][block] = {
                            k: v
                            for k, v in value[key][block].items()
                            if k in fields.get("properties", {})
                        }
            else:
                value[key] = {k: v for k, v in value[key].items() if k in allowed}
        return value

    def execute(self, name: str, arguments) -> dict:
        started = perf_counter()
        invalid = self.validate(name, arguments)
        if invalid:
            return invalid
        arguments = self.prepare(name, arguments)
        headers = {"accept": "application/json", "user-agent": USER_AGENT}
        method, body = "GET", None
        if name in ("rank", "policy_check", "decide"):
            if not self.key:
                envelope = {
                    "origin": self.api,
                    "status": 401,
                    "body": {"error": {"code": "missing_api_key"}},
                }
                return {
                    "result": tool_result(envelope),
                    "latency_ms": None,
                    "validation_errors": [],
                    "unknown_facets": [],
                    "api_call": False,
                }
            headers["Authorization"] = f"Bearer {self.key}"
            path = {"rank": "/v1/rank", "policy_check": "/v1/policy-check", "decide": "/v1/decide"}[
                name
            ]
            url, method, body = self.api + path, "POST", arguments
        elif name == "feedback":
            url, method, body = self.api + "/v1/feedback", "POST", arguments | {"client": "mcp"}
        elif name == "list_use_cases":
            url = self.export + "/api/rank/profiles.json"
        elif name == "model_info":
            model_id = arguments["model_id"].strip()
            if not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", model_id) or ".." in model_id:
                return {
                    "result": tool_result(
                        {
                            "origin": None,
                            "status": 400,
                            "body": {"error": {"code": "invalid_model_id"}},
                        }
                    ),
                    "latency_ms": None,
                    "validation_errors": ["Invalid model_id"],
                    "unknown_facets": [],
                    "api_call": False,
                }
            url = (
                self.api + self.vocabulary_path
                if self.split
                else self.export + "/api/models/" + model_id + ".json"
            )
        else:
            url = (
                self.api if self.vocabulary_path == "/v1/vocabulary" else self.export
            ) + self.vocabulary_path
        if name == "vocab" and self.vocabulary_path == "/v1/vocabulary":
            query = {"section": arguments.get("section", "starter"), "detail": arguments.get("detail", "compact")}
            query.update({key: value for key, value in arguments.items() if key != "section"})
            url += "?" + urlencode(query, doseq=True)
        try:
            response = self.client.request(method, url, json=body, headers=headers)
            try:
                response_body = response.json()
            except ValueError:
                response_body = response.text
            envelope = {"origin": url, "status": response.status_code, "body": response_body}
        except httpx.HTTPError:
            envelope = {
                "origin": url,
                "status": 0,
                "body": {"error": {"code": "origin_unreachable"}},
            }
        return self.finish(name, arguments, envelope, (perf_counter() - started) * 1000)

    def finish(self, name: str, arguments, envelope: dict, latency: float) -> dict:
        if self.key:
            envelope = json.loads(json.dumps(envelope).replace(self.key, "[REDACTED]"))
        body = envelope["body"]
        if envelope["status"] < 400 and isinstance(body, dict):
            if name == "vocab":
                from api.worker.src.display_vocabulary import lookup, vocabulary_response

                self.valid_ids = self.valid_ids or set()
                for section in ("facets", "benchmarks", "domains", "refinements"):
                    rows = body.get(section)
                    if isinstance(rows, list):
                        for row in rows:
                            if isinstance(row, dict):
                                for key in ("id", "weight_key"):
                                    if isinstance(row.get(key), str):
                                        self.valid_ids.add(row[key])
                if self.vocabulary_path == "/v1/vocabulary" and "vocabulary_version" not in body:
                    selected = body.get(arguments.get("section", "starter"))
                else:
                    selected = lookup(body, section=arguments.get("section", "starter"),
                                      search=arguments.get("search", ""),
                                      ids=[*arguments.get("ids", []), *([arguments["id"]] if "id" in arguments else [])],
                                      detail=arguments.get("detail", "compact"),
                                      offset=arguments.get("offset", 0), limit=arguments.get("limit", 20))[arguments.get("section", "starter")]
                if arguments.get("section", "starter") in {"starter", "facets", "benchmarks", "domains", "refinements"} and isinstance(selected, list):
                    self.valid_ids.update(row["id"] for row in selected if isinstance(row, dict) and isinstance(row.get("id"), str))
                envelope = envelope | {"body": vocabulary_response(selected, arguments.get("section", "starter"))}
            elif name == "model_info" and self.split and isinstance(body.get("models"), dict):
                envelope = envelope | {"body": body.get("models", {}).get(arguments["model_id"])}
        validation = []
        if envelope["status"] in (400, 422):
            error = body.get("error", {}) if isinstance(body, dict) else {}
            validation = error.get("issues", []) or [error.get("message", error.get("code", body))]
        unknown = []
        unadvertised = []
        if self.valid_ids is not None and name == "decide":
            unadvertised = sorted(set(attempted_facets(arguments)) - self.valid_ids)
        # API validation issues can identify unknown ids even before vocab was read.
        for issue in validation:
            if isinstance(issue, dict) and any(
                word in str(issue.get("reason", issue.get("message", ""))).lower()
                for word in ("unknown", "not registered", "unregistered")
            ):
                value = issue.get("field", issue.get("facet"))
                if isinstance(value, str):
                    unknown.append(value)
        result = tool_result(envelope)
        if name == "decide" and not result["isError"] and isinstance(body, dict):
            rows = body.get("results")
            models = (
                list(
                    dict.fromkeys(
                        r["offering"]["model"]
                        for r in rows
                        if isinstance(r, dict)
                        and isinstance(r.get("offering"), dict)
                        and isinstance(r["offering"].get("model"), str)
                    )
                )[:5]
                if isinstance(rows, list)
                else []
            )
            may_qualify = body.get("may_qualify")
            may_count = len(may_qualify) if isinstance(may_qualify, list) else 0
            summary = (
                f"status: {body.get('status', 'unknown')}; top models: "
                f"{', '.join(models) or 'none'}; may qualify: {may_count}"
            )
            result["content"].append({"type": "text", "text": summary})
        return {
            "result": result,
            "latency_ms": latency,
            "validation_errors": validation,
            "unknown_facets": sorted(set(unknown)),
            "unadvertised_facets": unadvertised,
            "api_call": True,
        }
