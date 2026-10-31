import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Services.UPower
import Quickshell.Wayland

Item {
  id: root

  // Owns the screen-off policy.  On AC power or above 25% battery, the
  // stay-awake state is forced on so the normal idle service never opens a
  // screensaver or locks the session.  Only in battery-saving mode (discharging
  // at 25% or less) does the screen turn off after the idle timeout.  The
  // lid-close binding continues to lock normally.
  readonly property int thresholdPercent: 25
  readonly property int timeoutSeconds: 20 * 60
  readonly property real batteryPercent: Number(UPower.displayDevice.percentage)
  readonly property bool batterySavingActive: UPower.onBattery
    && UPower.displayDevice.state === UPowerDeviceState.Discharging
    && isFinite(batteryPercent) && batteryPercent <= thresholdPercent

  property bool displayIsOff: false
  property bool desiredDisplayOn: true

  function setDisplayPower(on) {
    desiredDisplayOn = on
    if (dpmsProcess.running) return
    dpmsProcess.command = ["hyprctl", "dispatch", "dpms", on ? "on" : "off"]
    dpmsProcess.running = true
  }

  function applyStayAwakePolicy() {
    if (stayAwakeProcess.running) return
    if (batterySavingActive) {
      // Low battery: hand stay-awake control back to the media watchdog.
      stayAwakeProcess.command = ["bash", "-c", "if [[ ! -f $HOME/.local/state/gran/indicators/watchdog-media-awake ]]; then rm -f $HOME/.local/state/gran/indicators/stay-awake; fi"]
    } else {
      // AC power or above 25%: stay-awake must never turn off.
      stayAwakeProcess.command = ["bash", "-c", "mkdir -p $HOME/.local/state/gran/indicators && [[ -f $HOME/.local/state/gran/indicators/stay-awake ]] || touch $HOME/.local/state/gran/indicators/stay-awake"]
    }
    stayAwakeProcess.running = true
  }

  function updatePolicy() {
    applyStayAwakePolicy()
    // Charging, AC power, or more than 25% immediately wakes the displays.
    if (!batterySavingActive) {
      displayIsOff = false
      setDisplayPower(true)
    }
  }

  IdleMonitor {
    id: idleMonitor
    enabled: root.batterySavingActive
    timeout: root.timeoutSeconds
    respectInhibitors: true
    onIsIdleChanged: {
      if (!root.batterySavingActive) return
      root.displayIsOff = idleMonitor.isIdle
      root.setDisplayPower(!idleMonitor.isIdle)
    }
  }

  Timer {
    // UPower signals are not exposed uniformly by all laptop firmware; polling
    // makes threshold transitions dependable without relying on a notification.
    interval: 30000
    running: true
    repeat: true
    triggeredOnStart: true
    onTriggered: root.updatePolicy()
  }

  onBatterySavingActiveChanged: updatePolicy()

  Process {
    id: dpmsProcess
    onExited: {
      // Apply the newest state when battery/activity changed while hyprctl ran.
      var commandIsOn = dpmsProcess.command.length > 3 && dpmsProcess.command[3] === "on"
      if (commandIsOn !== root.desiredDisplayOn) root.setDisplayPower(root.desiredDisplayOn)
    }
  }

  Process {
    id: stayAwakeProcess
  }

  Component.onCompleted: updatePolicy()
}
