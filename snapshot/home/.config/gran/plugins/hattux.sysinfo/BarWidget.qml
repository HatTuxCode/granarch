import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "hattux.sysinfo"

  readonly property int intervalMs: Math.max(500, Number(root.setting("intervalMs", 1000)))
  readonly property real attack: Math.max(0, Math.min(1, Number(root.setting("attack", 0))))
  readonly property real releaseRatio: Math.max(0.05, Math.min(1, Number(root.setting("releaseRatio", 0.3))))
  readonly property real release: root.attack * root.releaseRatio
  readonly property bool filtered: root.attack > 0

  property string tempPath: ""
  property real rawCpuPct: -1
  property real rawTempC: -1
  property real rawMemUsed: 0

  property real cpuPct: -1
  property real tempC: -1
  property real memTotalBytes: 0
  property real memUsedBytes: -1

  readonly property bool ready: cpuPct >= 0
  readonly property real memPct: memTotalBytes > 0 ? (memUsedBytes / memTotalBytes) * 100 : -1

  readonly property bool tempHot: tempC >= 80
  readonly property bool tempWarm: tempC >= 65

  readonly property color tempColor: tempHot
    ? (root.bar && root.bar.urgent ? root.bar.urgent : Color.urgent)
    : root.bar && root.bar.foreground ? root.bar.foreground : Color.foreground

  function fmtBytes(bytes) {
    if (!(bytes > 0)) return "--"
    var gb = bytes / 1073741824
    if (gb >= 10) return gb.toFixed(1) + " GB"
    if (gb >= 1) return gb.toFixed(2) + " GB"
    return (bytes / 1048576).toFixed(0) + " MB"
  }

  function fmtPct(value) {
    return value >= 0 ? Math.round(value) + "%" : "--"
  }

  function fmtTemp(value) {
    return value >= 0 ? Math.round(value) + "°C" : "--"
  }

  function reread(view, path) {
    if (!path) return ""
    view.path = ""
    view.path = path
    return view.text()
  }

  function smooth(prev, sample) {
    if (!(sample >= 0)) return prev
    if (!(prev >= 0)) return sample
    if (root.attack <= 0) return sample
    var alpha = sample > prev ? root.attack : root.release
    return prev + alpha * (sample - prev)
  }

  function parseCpu(text) {
    if (!text) return null
    var lines = text.split("\n")
    for (var i = 0; i < lines.length; i++) {
      if (lines[i].indexOf("cpu ") !== 0) continue
      var f = lines[i].trim().split(/\s+/)
      if (f.length < 5) return null
      var user = parseInt(f[1], 10)
      var nice = parseInt(f[2], 10)
      var system = parseInt(f[3], 10)
      var idle = parseInt(f[4], 10)
      var iowait = parseInt(f[5], 10)
      var irq = f.length > 6 ? parseInt(f[6], 10) : 0
      var softirq = f.length > 7 ? parseInt(f[7], 10) : 0
      var steal = f.length > 8 ? parseInt(f[8], 10) : 0
      return { total: user + nice + system + idle + iowait + irq + softirq + steal, idle: idle + iowait }
    }
    return null
  }

  function parseMem(text) {
    if (!text) return null
    var total = 0
    var avail = 0
    var lines = text.split("\n")
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i]
      if (line.indexOf("MemTotal:") === 0) {
        total = parseInt(line.split(/\s+/)[1], 10) * 1024
      } else if (line.indexOf("MemAvailable:") === 0) {
        avail = parseInt(line.split(/\s+/)[1], 10) * 1024
      }
    }
    if (total <= 0 || avail < 0) return null
    return { total: total, used: total - avail }
  }

  function poll() {
    var cpu = parseCpu(reread(statView, "/proc/stat"))
    if (cpu) {
      if (prevCpu && cpu.total > prevCpu.total) {
        var dTotal = cpu.total - prevCpu.total
        var dIdle = cpu.idle - prevCpu.idle
        var sample = Math.max(0, Math.min(100, 100 * (1 - dIdle / dTotal)))
        root.rawCpuPct = sample
        root.cpuPct = root.smooth(root.cpuPct, sample)
      }
      prevCpu = cpu
    }

    var mem = parseMem(reread(memView, "/proc/meminfo"))
    if (mem) {
      root.memTotalBytes = mem.total
      root.rawMemUsed = mem.used
      root.memUsedBytes = root.smooth(root.memUsedBytes, mem.used)
    }

    if (root.tempPath !== "") {
      var raw = reread(tempView, root.tempPath)
      var millis = parseInt(String(raw).trim(), 10)
      if (!isNaN(millis) && millis > 1000) {
        root.rawTempC = millis / 1000
        root.tempC = root.smooth(root.tempC, millis / 1000)
      }
    }
  }

  property var prevCpu: null

  Component.onCompleted: {
    tempResolver.running = true
    poll()
  }

  Process {
    id: tempResolver
    command: ["/bin/sh", "-c",
      "for t in /sys/class/thermal/thermal_zone*/type; do [ -r \"$t\" ] || continue; " +
      "n=$(cat \"$t\" 2>/dev/null); " +
      "case \"$n\" in x86_pkg_temp|coretemp|k10temp|cpu_thermal|soc_thermal) " +
      "echo \"${t%/type}/temp\"; exit 0;; esac; done; " +
      "for h in /sys/class/hwmon/hwmon*/name; do [ -r \"$h\" ] || continue; " +
      "n=$(cat \"$h\" 2>/dev/null); " +
      "case \"$n\" in coretemp|k10temp|zenpower) echo \"${h%/name}/temp1_input\"; exit 0;; esac; done"]
    stdout: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        var p = String(text || "").trim().split("\n")[0]
        if (p && p.indexOf("/") === 0) root.tempPath = p.trim()
      }
    }
  }

  FileView {
    id: statView
    watchChanges: false
    blockLoading: true
    printErrors: false
  }

  FileView {
    id: memView
    watchChanges: false
    blockLoading: true
    printErrors: false
  }

  FileView {
    id: tempView
    watchChanges: false
    blockLoading: true
    printErrors: false
  }

  Timer {
    interval: root.intervalMs
    running: true
    repeat: true
    triggeredOnStart: false
    onTriggered: root.poll()
  }

  IpcHandler {
    target: "hattux.sysinfo"

    function refresh(): void {
      root.prevCpu = null
      root.cpuPct = -1
      root.tempC = -1
      root.memUsedBytes = -1
      root.poll()
    }

    function state(): string {
      return JSON.stringify({
        cpu: root.cpuPct, temp: root.tempC,
        memUsed: root.memUsedBytes, memTotal: root.memTotalBytes,
        rawCpu: root.rawCpuPct, rawTemp: root.rawTempC, rawMem: root.rawMemUsed,
        attack: root.attack, release: root.release, tempPath: root.tempPath
      })
    }
  }

  visible: root.ready
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  readonly property string label: root.ready
    ? "󰍛 " + root.fmtPct(root.cpuPct) + "  " + root.fmtTemp(root.tempC) + "  " + root.fmtBytes(root.memUsedBytes)
    : "󰍛 --"

  WidgetButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: root.label
    fontSize: Style.font.caption
    pressable: false
    tooltipText: root.ready
      ? "SysInfo\n"
        + "CPU:       " + root.fmtPct(root.cpuPct) + "\n"
        + "Temp:      " + root.fmtTemp(root.tempC) + "\n"
        + "RAM:       " + root.fmtBytes(root.memUsedBytes) + " / " + root.fmtBytes(root.memTotalBytes)
        + "  (" + root.fmtPct(root.memPct) + ")"
      : "SysInfo — coletando..."
  }
}
