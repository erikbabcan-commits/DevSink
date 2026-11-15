//
//  DevSinkApp.swift
//  DevSink Pro for macOS — Native Menu Bar Developer Appliance Switcher
//  Copyright © 2026 DevSink Team. All rights reserved.
//

import SwiftUI
import CoreWLAN
import Foundation

@main
struct DevSinkProApp: App {
    @StateObject private var monitor = DevSinkMonitor()

    var body: some Scene {
        MenuBarExtra("DevSink Pro", systemImage: monitor.isConnected ? "bolt.fill" : "bolt.slash") {
            VStack(alignment: .leading, spacing: 4) {
                Text("⚡ DevSink Pro v1.0.0")
                    .font(.headline)
                
                if monitor.isLicensed {
                    Text("Licencia: Aktívna (Doživotná)")
                        .font(.caption)
                        .foregroundColor(.green)
                } else {
                    Text("Skúšobná verzia")
                        .font(.caption)
                        .foregroundColor(.orange)
                }

                Divider()

                HStack {
                    Circle()
                        .fill(monitor.isConnected ? Color.green : Color.gray)
                        .frame(width: 8, height: 8)
                    Text(monitor.statusText)
                        .font(.subheadline)
                }

                Text("Wi-Fi: \(monitor.currentSSID)")
                    .font(.caption2)
                    .foregroundColor(.secondary)

                Divider()

                Button("Zapnúť LAN Cache (devsink on)") {
                    monitor.runCommand("on")
                }
                .disabled(monitor.isConnected)

                Button("Prepnúť na verejné (devsink off)") {
                    monitor.runCommand("off")
                }
                .disabled(!monitor.isConnected)

                Divider()

                Button("🧹 Uvoľniť miesto na Macu (Purge)") {
                    monitor.runCommand("purge")
                }

                Button("Otvoriť Mission Control Web") {
                    if let url = URL(string: "http://\(monitor.serverHost):3333") {
                        NSWorkspace.shared.open(url)
                    }
                }

                Divider()

                Button("Zadať licenčný kľúč...") {
                    monitor.promptLicense()
                }

                Button("Ukončiť") {
                    NSApplication.shared.terminate(nil)
                }
            }
            .padding(8)
        }
        .menuBarExtraStyle(.menu)
    }
}

class DevSinkMonitor: ObservableObject {
    @Published var isConnected = false
    @Published var currentSSID = "Neznáma"
    @Published var statusText = "Overujem stav..."
    @Published var isLicensed = false
    @Published var serverHost = "vorkei.local"

    private var timer: Timer?

    init() {
        checkLicense()
        startNetworkMonitoring()
    }

    func checkLicense() {
        let licensePath = ("~/.config/devsink/license.key" as NSString).expandingTildeInPath
        if FileManager.default.fileExists(atPath: licensePath),
           let content = try? String(contentsOfFile: licensePath, encoding: .utf8),
           content.contains("DEVSINK-PRO-") {
            self.isLicensed = true
        }
    }

    func startNetworkMonitoring() {
        checkStatus()
        timer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { [weak self] _ in
            self?.checkStatus()
        }
    }

    func checkStatus() {
        // Fetch current Wi-Fi SSID
        if let interface = CWWiFiClient.shared().interface() {
            self.currentSSID = interface.ssid() ?? "Odpojené"
        }

        // Probe DevSink appliance port 4873 (NPM cache)
        let url = URL(string: "http://\(serverHost):4873")!
        var request = URLRequest(url: url)
        request.timeoutInterval = 1.5

        URLSession.shared.dataTask(with: request) { [weak self] _, response, error in
            DispatchQueue.main.async {
                if let http = response as? HTTPURLResponse, http.statusCode == 200 {
                    self?.isConnected = true
                    self?.statusText = "Pripojené k SSD (LAN)"
                } else {
                    self?.isConnected = false
                    self?.statusText = "Verejné registre (WAN)"
                }
            }
        }.resume()
    }

    func runCommand(_ action: String) {
        let task = Process()
        task.launchPath = "/bin/bash"
        task.arguments = ["-c", "devsink \(action)"]
        try? task.run()
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) { [weak self] in
            self?.checkStatus()
        }
    }

    func promptLicense() {
        let alert = NSAlert()
        alert.messageText = "Aktivácia DevSink Pro"
        alert.informativeText = "Vložte váš licenčný kľúč vo formáte DEVSINK-PRO-XXXX-XXXX-XXXX-XXXX:"
        let input = NSTextField(frame: NSRect(x: 0, y: 0, width: 280, height: 24))
        alert.accessoryView = input
        alert.addButton(withTitle: "Aktivovať")
        alert.addButton(withTitle: "Zrušiť")

        if alert.runModal() == .alertFirstButtonReturn {
            let key = input.stringValue.trimmingCharacters(in: .whitespacesAndNewlines)
            if key.hasPrefix("DEVSINK-PRO-") {
                let dir = ("~/.config/devsink" as NSString).expandingTildeInPath
                try? FileManager.default.createDirectory(atPath: dir, withIntermediateDirectories: true)
                try? key.write(toFile: "\(dir)/license.key", atomically: true, encoding: .utf8)
                self.isLicensed = true
            }
        }
    }
}
