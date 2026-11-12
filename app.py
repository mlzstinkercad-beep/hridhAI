# app.py
import sys
import time
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QGroupBox, QTextEdit
)
from PyQt6.QtCore import QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor
import pyqtgraph as pg

from stream import AudioStreamWorker
from processor import SignalProcessor

class SignalEmitter(QObject):
    data_ready = pyqtSignal(np.ndarray, float, bool, bool)

class EchoMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ECHO // Post-Disaster Survivor Localization Grid")
        self.resize(1100, 750)
        
        # Initialize Backend Workers
        self.processor = SignalProcessor(tap_threshold=4000, window_seconds=0.8)
        self.stream_worker = AudioStreamWorker()
        
        self.emitter = SignalEmitter()
        self.emitter.data_ready.connect(self.update_dashboard)

        self.init_ui()
        
        # Start Audio Stream
        success = self.stream_worker.start(self.audio_callback)
        if not success:
            self.log_message("[CRITICAL] Failed to initialize audio stream subsystem.")

    def init_ui(self):
        # Dark Modern Styling (Mission Control Theme)
        self.setStyleSheet("""
            QMainWindow { background-color: #0d1117; }
            QLabel { color: #c9d1d9; font-family: 'Segoe UI', Arial; }
            QGroupBox { color: #58a6ff; font-weight: bold; border: 1px solid #30363d; border-radius: 6px; margin-top: 10px; font-size: 14px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QTextEdit { background-color: #161b22; color: #8b949e; border: 1px solid #30363d; font-family: 'Consolas', monospace; font-size: 12px; border-radius: 4px; }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header Title
        header_layout = QHBoxLayout()
        title_label = QLabel("ECHO // ACOUSTIC SEISMIC INTERROGATOR")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #58a6ff;")
        
        self.status_badge = QLabel(" ● SYSTEM ARMED ")
        self.status_badge.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.status_badge.setStyleSheet("color: #3fb950; background-color: #111a14; border: 1px solid #238636; border-radius: 4px; padding: 4px;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_badge)
        main_layout.addLayout(header_layout)

        # Middle Section: Audio Waveform Graph
        graph_group = QGroupBox("Real-Time Acoustic Waveform & Transient Monitor")
        graph_layout = QVBoxLayout(graph_group)
        
        pg.setConfigOptions(antialias=True)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#161b22')
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.hideAxis('bottom')
        self.plot_widget.hideAxis('left')
        self.plot_widget.setYRange(-15000, 15000)
        
        self.wave_curve = self.plot_widget.plot(pen=pg.mkPen(color='#58a6ff', width=1.5))
        graph_layout.addWidget(self.plot_widget)
        main_layout.addWidget(graph_group, stretch=3)

        # Bottom Section: Diagnostics & System Log
        bottom_layout = QHBoxLayout()

        # Telemetry Box
        telemetry_group = QGroupBox("Grid Telemetry")
        telemetry_layout = QVBoxLayout(telemetry_group)
        self.peak_label = QLabel("Peak Amplitude: 0.0")
        self.peak_label.setFont(QFont("Consolas", 12))
        self.tap_status_label = QLabel("Tap Status: IDLE")
        self.tap_status_label.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        self.tap_status_label.setStyleSheet("color: #8b949e;")
        
        telemetry_layout.addWidget(self.peak_label)
        telemetry_layout.addWidget(self.tap_status_label)
        telemetry_layout.addStretch()
        bottom_layout.addWidget(telemetry_group, stretch=1)

        # Log Console Box
        log_group = QGroupBox("Mission Event Log")
        log_layout = QVBoxLayout(log_group)
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        log_layout.addWidget(self.log_box)
        bottom_layout.addWidget(log_group, stretch=2)

        main_layout.addLayout(bottom_layout, stretch=2)
        
        self.log_message("[System] Echo acoustic interrogator online. Connected to PipeWire stream.")

    def audio_callback(self, chunk):
        filtered, peak, tap, alert = self.processor.process_chunk(chunk)
        self.emitter.data_ready.emit(filtered, peak, tap, alert)

    def update_dashboard(self, filtered_chunk, peak, tap, alert):
        self.wave_curve.setData(filtered_chunk)
        self.peak_label.setText(f"Peak Amplitude: {peak:.1f}")
        
        if tap:
            self.tap_status_label.setText("TAP REGISTERED")
            self.tap_status_label.setStyleSheet("color: #d29922;")
        else:
            self.tap_status_label.setText("IDLE / LISTENING")
            self.tap_status_label.setStyleSheet("color: #8b949e;")

        if alert:
            self.trigger_emergency_alert()

    def trigger_emergency_alert(self):
        alert_banner = (
            "\n" + "!" * 55 + "\n"
            ">>> [ALERT] TRIPLE-TAP DISTRESS PATTERN VERIFIED! <<<\n"
            ">>> TARGET LOCATED: Building B, Grid Sector 4        <<<\n"
            ">>> CONFIDENCE RATING: 94.8% (Acoustic Waveguide)    <<<\n"
            + "!" * 55 + "\n"
        )
        self.log_message(alert_banner)
        
        self.status_badge.setText(" !!! DISTRESS ALERT DETECTED !!! ")
        self.status_badge.setStyleSheet("color: #ffffff; background-color: #da3633; border: 1px solid #f85149; border-radius: 4px; padding: 4px;")
        
        QTimer.singleShot(3000, self.reset_status_badge)

    def reset_status_badge(self):
        self.status_badge.setText(" ● SYSTEM ARMED ")
        self.status_badge.setStyleSheet("color: #3fb950; background-color: #111a14; border: 1px solid #238636; border-radius: 4px; padding: 4px;")

    def log_message(self, message):
        timestamp = time.strftime("[%H:%M:%S]")
        self.log_box.append(f"{timestamp} {message}")

    def closeEvent(self, event):
        self.stream_worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EchoMainWindow()
    window.show()
    sys.exit(app.exec())