# codex-token-usage

Глобальный skill для Codex, который показывает накопительное использование токенов текущей задачи.

```text
Input tokens 2 184
Output tokens 742
Estimated total 2 926
```

Skill читает локальные JSONL-журналы Codex и берёт последнее записанное событие `token_count`. Если задача запускала subagents, их токены также рекурсивно добавляются к результату без повторного учёта.

## Что учитывается

- `Input tokens` — все входные токены, включая cached input.
- `Output tokens` — все выходные токены, включая reasoning output.
- `Estimated total` — сумма input и output.
- Каждый основной агент и subagent учитывается один раз.
- При недоступной или несовместимой статистике выводится `N/A`.

Skill работает только по явному вызову `$codex-token-usage` и не запускается автоматически при обычном разговоре о токенах.

## Требования

- Локальная сессия Codex с сохранением журналов в `.codex/sessions`.
- Python 3.10 или новее.
- Команда `python` должна быть доступна из терминала Codex.
- Git — для установки способом ниже.

Проверить Python:

```powershell
python --version
```

## Установка из GitHub на Windows

Откройте PowerShell и создайте папку пользовательских skills:

```powershell
New-Item -ItemType Directory -Force `
  -Path "$env:USERPROFILE\.agents\skills" | Out-Null
```

Клонируйте репозиторий прямо в папку skills:

```powershell
git clone https://github.com/Web3Zak/codex-token-usage.git `
  "$env:USERPROFILE\.agents\skills\codex-token-usage"
```

Проверьте установку:

```powershell
Test-Path "$env:USERPROFILE\.agents\skills\codex-token-usage\SKILL.md"
```

Команда должна вернуть `True`.

Codex обычно обнаруживает новый skill автоматически. Если он не появился, откройте новую задачу или перезапустите Codex.

## Установка без Git

1. Откройте страницу [Web3Zak/codex-token-usage](https://github.com/Web3Zak/codex-token-usage).
2. Нажмите **Code → Download ZIP**.
3. Распакуйте архив.
4. Переименуйте папку `codex-token-usage-main` в `codex-token-usage`.
5. Переместите её в `%USERPROFILE%\.agents\skills\`.

Итоговый путь должен быть таким:

```text
C:\Users\<имя>\.agents\skills\codex-token-usage\SKILL.md
```

Не должно быть двойной вложенности вида `codex-token-usage\codex-token-usage\SKILL.md`.

## Использование

В новой или текущей задаче Codex вызовите:

```text
$codex-token-usage
```

Skill вернёт только три строки со статистикой токенов.

## Обновление

Если skill установлен через Git:

```powershell
git -C "$env:USERPROFILE\.agents\skills\codex-token-usage" pull --ff-only
```

После обновления при необходимости перезапустите Codex.

## macOS и Linux

Пользовательские skills хранятся в `~/.agents/skills`:

```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Web3Zak/codex-token-usage.git \
  ~/.agents/skills/codex-token-usage
```

Команда `python` должна запускать Python 3.10 или новее.

## Ограничения

- Отчёт отражает последнее состояние, уже записанное Codex в журнал.
- Токены ответа, который ещё генерируется, заранее посчитать невозможно.
- Стоимость, rate limits и размер контекстного окна не выводятся.
- Skill предназначен для локальных задач Codex; в облачной среде без локальных rollout-журналов статистика может быть недоступна.

Скрипт использует только стандартную библиотеку Python, читает журналы в режиме read-only и не отправляет их по сети.
