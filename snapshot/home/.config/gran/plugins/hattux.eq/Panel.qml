import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Io
import qs.Ui
import qs.Commons

// Plugin: hattux.eq — Equalizador de 5 bandas em tempo real.
// Replica a estrutura visual do audio panel: hero com ícone/título/switch,
// seção de bandas com slider dedicado por banda. Cada mudança aplica o ganho
// imediatamente via pw-cli e persiste no config para sobreviver a restart.
Panel {
  id: root
  moduleName: "hattux.eq"
  ipcTarget: "hattux.eq"

  // ---- ganhos atuais (dB, -12..+12) ----
  property int bassGain: 0
  property int lowmidGain: 0
  property int midGain: 0
  property int presenceGain: 0
  property int trebleGain: 0

  // false até os valores reais chegarem do PipeWire
  property bool loaded: false
  // true enquanto transição de enable/disable está em voo
  property bool eqBusy: false
  // estado do equalizador: true se sink padrão é gran.equalizer
  property bool eqEnabled: false

  // Nominal das bandas: key (nome no PipeWire), label, frequência.
  readonly property var bands: [
    { key: "bass",     label: "Graves",       freq: "90 Hz" },
    { key: "lowmid",   label: "Médio-graves", freq: "300 Hz" },
    { key: "mid",      label: "Médios",       freq: "1 kHz" },
    { key: "presence", label: "Presença",     freq: "3.3 kHz" },
    { key: "treble",   label: "Agudos",       freq: "11 kHz" }
  ]

  readonly property bool anyBoosted: bassGain !== 0 || lowmidGain !== 0 ||
                                     midGain !== 0 || presenceGain !== 0 || trebleGain !== 0

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  // ---- cursor model ----
  // focusedBand: -1 = hero toggle, 0..4 = bandas
  property int focusedBand: -1
  property bool cursorActive: false

  readonly property bool headerHasCursor: cursorActive && focusedBand === -1

  function moveCursor(dy) {
    focusedBand = Math.max(-1, Math.min(bands.length - 1, focusedBand + dy))
  }

  function adjustFocused(dx) {
    if (focusedBand < 0 || focusedBand >= bands.length) return
    var band = bands[focusedBand]
    var cur = bandValue(band.key)
    var nv = Math.max(-12, Math.min(12, cur + (dx > 0 ? 1 : -1)))
    setBand(band.key, nv)
  }

  function activateCursor() {
    if (focusedBand === -1) {
      toggleEq()
    } else {
      resetBand(bands[focusedBand].key)
    }
  }

  // ---- funções de ganho ----

  function bandValue(key) {
    switch (key) {
      case "bass": return bassGain
      case "lowmid": return lowmidGain
      case "mid": return midGain
      case "presence": return presenceGain
      case "treble": return trebleGain
    }
    return 0
  }

  function setBand(key, newValue) {
    var v = Math.max(-12, Math.min(12, Math.round(newValue)))
    switch (key) {
      case "bass": bassGain = v; break
      case "lowmid": lowmidGain = v; break
      case "mid": midGain = v; break
      case "presence": presenceGain = v; break
      case "treble": trebleGain = v; break
    }
    Quickshell.execDetached(["gran-eq-control", "set",
      String(bassGain), String(lowmidGain), String(midGain),
      String(presenceGain), String(trebleGain)
    ])
  }

  function resetBand(key) {
    setBand(key, 0)
    persistAll()
  }

  function persistAll() {
    Quickshell.execDetached(["gran-eq-control", "persist",
      String(bassGain), String(lowmidGain), String(midGain),
      String(presenceGain), String(trebleGain)
    ])
  }

  function resetAll() {
    bassGain = 0; lowmidGain = 0; midGain = 0; presenceGain = 0; trebleGain = 0
    persistAll()
  }

  // ---- enable/disable do equalizador ----

  function toggleEq() {
    if (eqBusy) return
    eqBusy = true
    toggleProc.running = false
    toggleProc.command = ["gran-eq-control", eqEnabled ? "disable" : "enable"]
    toggleProc.running = true
  }

  // Estado do equalizador via script.
  function refreshState() {
    if (!stateProc.running) stateProc.running = true
  }

  // ---- leitura de dados ----

  onOpenedChanged: {
    if (opened) {
      loaded = false
      readProc.running = true
      refreshState()
      Qt.callLater(() => { if (keyCatcher) keyCatcher.forceActiveFocus() })
    }
  }

  // Roda enable/disable; ao terminar, refresh ao estado (knob e rótulos).
  Process {
    id: toggleProc
    running: false
    command: []
    onExited: function() {
      root.stateDelay.restart()
    }
  }

  Process {
    id: readProc
    command: ["gran-eq-control", "read"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        var parts = String(text).trim().split(/\s+/)
        if (parts.length >= 5) {
          root.bassGain = Number(parts[0]) || 0
          root.lowmidGain = Number(parts[1]) || 0
          root.midGain = Number(parts[2]) || 0
          root.presenceGain = Number(parts[3]) || 0
          root.trebleGain = Number(parts[4]) || 0
        }
        root.loaded = true
      }
    }
  }

  Process {
    id: stateProc
    command: ["gran-eq-control", "state"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        root.eqEnabled = String(text).trim() === "on"
        root.eqBusy = false
      }
    }
  }

  // Breve delay para o PipeWire propagar a mudança de sink antes de reler.
  Timer {
    id: stateDelay
    interval: 300
    onTriggered: refreshState()
  }

  // Mantém ícone e estado sincronizados com o painel fechado.
  Timer {
    interval: 5000
    running: !root.opened
    repeat: true
    triggeredOnStart: true
    onTriggered: {
      if (!readProc.running) readProc.running = true
      refreshState()
    }
  }

  // ---- botão na barra ----

  readonly property color barIconColor: eqEnabled ? bar.barForeground : Qt.darker(bar.barForeground, 1.55)

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    // Font Awesome "music": two connected eighth notes, immediately
    // recognizable in the compact status-bar treatment.
    text: "\uF001"
    foreground: root.barIconColor
    tooltipText: root.eqEnabled ? "Equalizador (ativo)" : "Equalizador (desativado)"

    onPressed: root.toggle()

    HoverHandler {
      onHoveredChanged: if (hovered) {
        root.cursorActive = true
        root.focusedBand = -1
      }
    }
  }

  // ---- painel popup ----
  KeyboardPanel {
    id: panel
    anchorItem: button
    owner: root
    bar: root.bar
    open: root.opened
    focusTarget: keyCatcher
    contentWidth: panel.fittedContentWidth(Style.space(340))
    contentHeight: panel.fittedContentHeight(panelColumn.implicitHeight, Style.space(540))

    PanelKeyCatcher {
      id: keyCatcher
      anchors.fill: parent
      onMoveRequested: function(dx, dy) {
        if (dy !== 0) {
          root.cursorActive = true
          root.moveCursor(dy)
        } else if (dx !== 0) {
          root.adjustFocused(dx)
        }
      }
      onActivateRequested: root.activateCursor()
      onCloseRequested: root.close()
      onTabRequested: function(direction) { root.switchPanel(direction) }
      onTextKey: function(t) {
        if (t === "r" || t === "R") root.resetAll()
      }

      ScrollView {
        id: scrollArea
        anchors.fill: parent
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.policy: panelColumn.implicitHeight > height
                                   ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff
        Binding {
          target: scrollArea.contentItem
          property: "interactive"
          value: panelColumn.implicitHeight > scrollArea.height
        }

        Column {
          id: panelColumn
          width: scrollArea.availableWidth
          spacing: Style.space(14)

          // ---- Hero: ícone + título + switch (igual ao audio) ----
          Item {
            id: heroItem
            width: parent.width
            implicitHeight: Math.max(heroIcon.implicitHeight, heroLabels.implicitHeight, eqToggle.implicitHeight)

            Text {
              id: heroIcon
              textFormat: Text.PlainText
              text: "\uF001"
              color: root.bar.foreground
              font.family: root.bar.fontFamily
              font.pixelSize: Style.font.display
              opacity: root.eqEnabled ? 1 : 0.5
              anchors.left: parent.left
              anchors.verticalCenter: parent.verticalCenter
            }

            ToggleSwitch {
              id: eqToggle
              checked: root.eqEnabled
              busy: root.eqBusy
              hasCursor: root.headerHasCursor
              foreground: root.bar.foreground
              anchors.right: parent.right
              anchors.verticalCenter: parent.verticalCenter
              onHovered: function(on) { if (on) root.cursorActive = true; root.focusedBand = -1 }
              onToggled: root.toggleEq()

              PanelToolTip {
                visible: eqToggle.containsMouse
                text: root.eqEnabled ? "Desativar equalizador" : "Ativar equalizador"
                fontFamily: root.bar.fontFamily
              }
            }

            Column {
              id: heroLabels
              anchors.left: heroIcon.right
              anchors.leftMargin: Style.space(14)
              anchors.right: parent.right
              anchors.rightMargin: eqToggle.width + Style.space(12)
              anchors.verticalCenter: parent.verticalCenter
              spacing: Style.space(2)

              Text {
                text: "Equalizador"
                color: root.bar.foreground
                font.family: root.bar.fontFamily
                font.pixelSize: Style.font.title
                font.bold: true
                elide: Text.ElideRight
                width: parent.width
              }

              Text {
                textFormat: Text.PlainText
                text: {
                  if (!root.eqEnabled) return "DESATIVADO"
                  return root.anyBoosted ? "ATIVO" : "PLANO"
                }
                color: Qt.darker(root.bar.foreground, 1.4)
                font.family: root.bar.fontFamily
                font.pixelSize: Style.font.caption
                font.bold: true
                font.letterSpacing: 1.2
                elide: Text.ElideRight
                width: parent.width
              }
            }
          }

          PanelSeparator {
            foreground: root.bar.foreground
          }

          // Keep the controls in one compact group, as in the native Audio
          // panel. Each row owns its height, so labels and sliders cannot
          // overlap when the panel is constrained.
          Column {
            width: parent.width
            spacing: Style.space(6)

            PanelSectionHeader {
              text: "BANDAS"
              foreground: root.bar.foreground
              fontFamily: root.bar.fontFamily
            }

            BandControl { bandKey: "bass";     label: "Graves";       freq: "90 Hz";   value: root.bassGain;     index: 0; hasCursor: root.cursorActive && root.focusedBand === 0 }
            BandControl { bandKey: "lowmid";   label: "Médio-graves"; freq: "300 Hz";  value: root.lowmidGain;   index: 1; hasCursor: root.cursorActive && root.focusedBand === 1 }
            BandControl { bandKey: "mid";      label: "Médios";       freq: "1 kHz";   value: root.midGain;      index: 2; hasCursor: root.cursorActive && root.focusedBand === 2 }
            BandControl { bandKey: "presence"; label: "Presença";     freq: "3.3 kHz"; value: root.presenceGain; index: 3; hasCursor: root.cursorActive && root.focusedBand === 3 }
            BandControl { bandKey: "treble";   label: "Agudos";       freq: "11 kHz";  value: root.trebleGain;   index: 4; hasCursor: root.cursorActive && root.focusedBand === 4 }
          }

          PanelSeparator {
            foreground: root.bar.foreground
          }

          Text {
            text: "R = zerar todos · ←→ ajusta banda · Enter = alternar EQ"
            color: Qt.darker(root.bar.foreground, 1.4)
            font.family: root.bar.fontFamily
            font.pixelSize: Style.font.caption
            wrapMode: Text.WordWrap
            width: parent.width
          }
        }
      }
    }
  }

  // ---- componente: uma banda ----

  component BandControl: CursorSurface {
    id: band
    required property string bandKey
    required property string label
    required property string freq
    required property int value
    required property int index

    width: parent.width
    height: controls.implicitHeight + Style.spacing.controlGap
    foreground: root.bar.foreground
    opacity: root.eqEnabled ? 1 : 0.5
    outline: true

    Column {
      id: controls
      anchors.fill: parent
      anchors.leftMargin: Style.space(6)
      anchors.rightMargin: Style.space(6)
      spacing: Style.space(3)

      // Label and frequency form a single left-aligned unit; the live dB
      // value has a reserved trailing column, keeping every row aligned.
      Item {
        width: parent.width
        implicitHeight: Math.max(captionName.implicitHeight, captionFreq.implicitHeight, captionValue.implicitHeight)

        Text {
          id: captionName
          textFormat: Text.PlainText
          text: band.label
          color: root.bar.foreground
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.body
          font.bold: true
          anchors.left: parent.left
          anchors.verticalCenter: parent.verticalCenter
          elide: Text.ElideRight
          width: parent.width - captionFreq.implicitWidth - captionValue.width - Style.space(16)
        }

        Text {
          id: captionFreq
          textFormat: Text.PlainText
          text: band.freq
          color: Qt.darker(root.bar.foreground, 1.5)
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.caption
          anchors.right: captionValue.left
          anchors.rightMargin: Style.space(6)
          anchors.verticalCenter: parent.verticalCenter
        }

        Text {
          id: captionValue
          textFormat: Text.PlainText
          text: (band.value > 0 ? "+" : "") + band.value + " dB"
          color: band.value === 0
            ? Qt.darker(root.bar.foreground, 1.5)
            : root.bar.foreground
          font.family: root.bar.fontFamily
          font.pixelSize: Style.font.caption
          font.bold: true
          width: Style.space(42)
          anchors.right: parent.right
          anchors.verticalCenter: parent.verticalCenter
          horizontalAlignment: Text.AlignRight
        }
        }

      PanelSlider {
        id: slider
        bar: root.bar
        width: parent.width
        minimum: -12
        maximum: 12
        step: 1
        integer: true
        tickCount: 5
        value: band.value
        enabled: root.loaded && root.eqEnabled

        onMoved: function(v) { root.setBand(band.bandKey, v) }
        onReleased: function(v) { root.persistAll() }
      }
    }

    HoverHandler {
      onHoveredChanged: if (hovered) {
        root.cursorActive = true
        root.focusedBand = band.index
      }
    }
  }
}
