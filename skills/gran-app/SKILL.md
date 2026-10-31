---
name: gran-app
description: Build or adapt a desktop application for GranArch with Qt Quick, the Gran theme and an Arch package or desktop launcher. Use when the user requests a new Gran desktop app or theme integration, not for unrelated web apps.
---

# Gran desktop applications

Use the user's chosen language/framework when specified. For a new native app
without an established stack, prefer C++ with Qt Quick and a small qmake or
CMake project. Keep application logic in C++/QObject properties and the
interface in QML. Use an app-specific Wayland ID and `.desktop` launcher.

Read `~/.local/state/gran/current/theme/colors.toml` for palette tokens and
watch it for live theme changes. Use `~/.config/gran/shell.toml` only for shell
appearance overrides; do not make a standalone app depend on shell internals.
Use `Text.PlainText` for untrusted content. Ask for app behavior only when the
request leaves a material decision unresolved.

Source Qt and build tools from official Arch packages. Package a native binary
with a PKGBUILD when installation is requested; never add a distribution repo.
Test the application's actual behavior and theme reload before installing it.
Keep source and build output separate. Do not install or publish without scope
from the user's request, and do not copy credentials into templates.
