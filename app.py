#!/usr/bin/env python3
"""
Server REST API & Web GUI Mandiri untuk STRIPS Tour Planner Kota Batu
Mata Kuliah: Artificial Intelligence | Kelompok 8 (Kelas A)
Menggunakan pustaka standar Python (http.server) - Zero External Dependency.
"""

import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

# Import engine STRIPS lokal
try:
    from strips_planner import (
        DESTINATIONS,
        TRAVEL_TIME_MATRIX,
        STRIPSTourPlanner,
        fmt_time,
        get_travel_time
    )
except ImportError:
    print("Error: file strips_planner.py tidak ditemukan di direktori saat ini.")
    sys.exit(1)

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class TourPlannerAPIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        
        # Route: Serve root atau GUI
        if parsed_url.path == "/" or parsed_url.path == "/gui":
            gui_path = os.path.join(BASE_DIR, "tour_planner_gui.html")
            if os.path.exists(gui_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(gui_path, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "File tour_planner_gui.html tidak ditemukan")
                return

        # Route: GET /api/destinations
        elif parsed_url.path == "/api/destinations":
            data = []
            for dest_id, d in DESTINATIONS.items():
                data.append({
                    "id": d.id,
                    "name": d.name,
                    "category": d.category,
                    "open_time": fmt_time(d.open_time),
                    "close_time": fmt_time(d.close_time),
                    "ticket_price": d.ticket_price,
                    "parking_motor": d.parking_motor,
                    "parking_car": d.parking_car,
                    "duration_min": d.duration,
                    "lat": d.lat,
                    "lng": d.lng,
                    "is_attraction": d.is_attraction
                })
            
            res_json = json.dumps({"status": "success", "total": len(data), "data": data}, indent=2)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(res_json.encode("utf-8"))
            return

        # Fallback to static file server
        super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        
        # Route: POST /api/plan
        if parsed_url.path == "/api/plan":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode("utf-8"))
            except Exception as e:
                self.send_error(400, f"Payload JSON tidak valid: {str(e)}")
                return

            # Ekstraksi parameter
            start_location = payload.get("start_location", "Stasiun_Malang")
            start_time_str = payload.get("start_time", "08:30")
            budget = int(payload.get("budget", 500000))
            goals = payload.get("goals", ["Jatim_Park_2", "Museum_Angkut", "BNS"])
            final_location = payload.get("final_location", "Hotel_Batu")
            max_end_time = int(payload.get("max_end_time", 1320))

            # Konversi jam mulai ke menit
            try:
                h, m = map(int, start_time_str.split(":"))
                start_time_min = h * 60 + m
            except Exception:
                start_time_min = 510 # default 08:30

            # Eksekusi STRIPS Planner
            planner = STRIPSTourPlanner(
                start_location=start_location,
                start_time_min=start_time_min,
                budget=budget,
                goals=goals,
                final_location=final_location,
                max_end_time=max_end_time
            )
            
            steps = planner.solve()

            if steps is None:
                res = {
                    "status": "failed",
                    "message": "Tidak dapat menemukan sekuens aksi yang memenuhi seluruh batasan (jam buka, anggaran, atau durasi)."
                }
            else:
                formatted_steps = []
                for s in steps:
                    formatted_steps.append({
                        "step_no": s.step_no,
                        "operator": s.operator_name,
                        "action_type": s.action_type,
                        "description": s.description,
                        "location": s.location,
                        "start_time": s.start_time_str,
                        "end_time": s.end_time_str,
                        "duration_min": s.duration_min,
                        "cost_rp": s.cost_rp,
                        "remaining_budget_rp": s.remaining_budget_rp,
                        "fol_precondition": s.precondition,
                        "fol_add_effect": s.add_effect,
                        "fol_delete_effect": s.delete_effect
                    })
                
                res = {
                    "status": "success",
                    "meta": {
                        "algorithm": "STRIPS (Stanford Research Institute Problem Solver)",
                        "start_location": DESTINATIONS.get(start_location, start_location).name if hasattr(DESTINATIONS.get(start_location), 'name') else start_location,
                        "start_time": fmt_time(start_time_min),
                        "initial_budget_rp": budget,
                        "target_count": len(goals),
                        "steps_count": len(formatted_steps),
                        "final_remaining_budget_rp": formatted_steps[-1]["remaining_budget_rp"] if formatted_steps else budget
                    },
                    "plan": formatted_steps
                }

            res_json = json.dumps(res, indent=2)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(res_json.encode("utf-8"))
            return

        self.send_error(404, "Endpoint POST tidak ditemukan")

    def do_OPTIONS(self):
        # Support CORS pre-flight
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def main():
    print("=" * 68)
    print("🚀 STRIPS TOUR PLANNER BACKEND SERVER & REST API (KELOMPOK 8)")
    print(f"📡 Server berjalan di http://localhost:{PORT}")
    print(f"🌐 Buka Web GUI di    : http://localhost:{PORT}/gui")
    print(f"📚 Endpoint Data Wisata: http://localhost:{PORT}/api/destinations")
    print(f"⚡ Endpoint Perencana  : POST http://localhost:{PORT}/api/plan")
    print("=" * 68)
    print("Tekan Ctrl + C untuk mematikan server.")
    
    server = HTTPServer(("0.0.0.0", PORT), TourPlannerAPIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server dihentikan dengan aman.")
        server.server_close()

if __name__ == "__main__":
    main()
