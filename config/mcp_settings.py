# -*- coding: utf-8 -*-
"""
Модуль для хранения конфигураций для запуска MCP-серверов.

Этот файл содержит словарь MCP_CONFIGS, который определяет команды
и аргументы для запуска различных MCP-серверов.

Безопасность:
    Секретные ключи и токены не должны храниться в этом файле.
    Для них следует использовать переменные окружения и secrets_manager.
"""
from typing import Dict, Any

# Словарь с конфигурациями для запуска MCP-серверов.
MCP_CONFIGS: Dict[str, Dict[str, Any]] = {
    "server-sequential-thinking": {
        "command": "cmd",
        "args": [
            "/c", "npx", "-y", "@smithery/cli@latest", "run",
            "@smithery-ai/server-sequential-thinking", "--key", "far-angelfish-LeI7K9"
        ],
        "description": "Сервер для последовательного мышления."
    },
    "context7": {
        "command": "npx",
        "args": ["-y", "@monotool/context7-mcp@latest"],
        "description": "Сервер для контекста context7."
    },
    "playwright-mcp": {
        "command": "npx",
        "args": ["@playwright/mcp@latest"],
        "description": "MCP-сервер для Playwright."
    },
    "github.com/modelcontextprotocol/servers/tree/main/src/filesystem": {
        "command": "cmd",
        "args": [
            "/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", "d:\\Bll_tests\\"
        ],
        "description": "Сервер, предоставляющий доступ к локальной файловой системе."
    },
    "wcgw": {
        "command": "npx",
        "args": ["-y", "@somepackage/wcgw-mcp@latest"],
        "description": "Сервер wcgw."
    },
    "firecrawl-mcp": {
        "command": "npx",
        "args": ["-y", "firecrawl-mcp"],
        "env": {
            # ВАЖНО: Значение этого ключа должно быть установлено как
            # переменная окружения перед запуском.
            "FIRECRAWL_API_KEY": "FIRECRAWL_API_KEY"
        },
        "description": "MCP-сервер для Firecrawl, требует API ключ."
    }
}

def get_mcp_config(server_name: str) -> Dict[str, Any]:
    """
    Возвращает конфигурацию для указанного MCP-сервера.

    Args:
        server_name: Имя сервера, для которого нужна конфигурация.

    Returns:
        Словарь с параметрами запуска сервера.

    Raises:
        KeyError: Если сервер с таким именем не найден.
    """
    if server_name not in MCP_CONFIGS:
        raise KeyError(f"Конфигурация для MCP-сервера '{server_name}' не найдена.")
    return MCP_CONFIGS[server_name]
