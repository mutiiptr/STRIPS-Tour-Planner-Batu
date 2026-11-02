"""
Sistem Perencanaan Otomatis Rute & Jadwal Wisata Kota Batu
Menggunakan Algoritma STRIPS (Stanford Research Institute Problem Solver)
Mata Kuliah: Artificial Intelligence (Kelas A)
Kelompok 8:
- Mutiara Putri Faradilla (NIM: 240605110113)
- Vanya Nyssa Maulida (NIM: 240605110104)
Dosen: Hani Nurhayati, M.T.

Algoritma mengadopsi model STRIPS klasik dengan representasi Daftar-PAD:
- P : Precondition (Syarat sebelum aksi)
- A : Add List (Kondisi yang ditambahkan ke State)
- D : Delete List (Kondisi yang dihapus dari State)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
import copy
import heapq

# ==============================================================================
# 1. BASIS PENGETAHUAN DOMAIN WISATA KOTA BATU
# ==============================================================================

@dataclass
class Destination:
    id: str
    name: str
    open_time: int       # menit dari 00:00 (misal 08:30 = 8*60+30 = 510)
    close_time: int      # menit dari 00:00 (misal 16:30 = 16*60+30 = 990)
    ticket_price: int    # rupiah per orang
    duration: int        # estimasi waktu eksplorasi dalam menit
    category: str        # 'edukasi', 'hiburan', 'alam', 'kuliner', 'belanja'
    is_attraction: bool = True

DESTINATIONS = {
    "Stasiun_Malang": Destination("Stasiun_Malang", "Stasiun Kota Malang (Titik Kedatangan)", 0, 1440, 0, 0, "transport", is_attraction=False),
    "Hotel_Batu": Destination("Hotel_Batu", "Hotel / Penginapan di Batu", 0, 1440, 0, 0, "penginapan", is_attraction=False),
    "Jatim_Park_2": Destination("Jatim_Park_2", "Jawa Timur Park 2 (Batu Secret Zoo)", 510, 990, 110000, 180, "edukasi"), # 08:30 - 16:30
    "Museum_Angkut": Destination("Museum_Angkut", "Museum Angkut & Pasar Apung", 720, 1200, 100000, 150, "edukasi"),    # 12:00 - 20:00
    "Jatim_Park_3": Destination("Jatim_Park_3", "Jatim Park 3 (Dino Park & Millennial Glow)", 660, 1260, 100000, 150, "edukasi"), # 11:00 - 21:00
    "Paralayang_Batu": Destination("Paralayang_Batu", "Wisata Paralayang & Omah Kayu", 420, 1080, 25000, 90, "alam"),    # 07:00 - 18:00
    "Coban_Rondo": Destination("Coban_Rondo", "Air Terjun Coban Rondo & Labirin", 450, 1020, 35000, 120, "alam"),        # 07:30 - 17:00
    "San_Terra": Destination("San_Terra", "Flora Wisata San Terra de Laponte", 480, 1020, 30000, 120, "alam"),          # 08:00 - 17:00
    "Selecta": Destination("Selecta", "Taman Rekreasi Selecta", 420, 1020, 50000, 120, "alam"),                          # 07:00 - 17:00
    "Petik_Apel_Kusuma": Destination("Petik_Apel_Kusuma", "Agrowisata Petik Apel Kusuma", 480, 1020, 60000, 90, "alam"), # 08:00 - 17:00
    "Coban_Rais": Destination("Coban_Rais", "Coban Rais & Batu Flower Garden", 480, 960, 35000, 120, "alam"),           # 08:00 - 16:00
    "BNS": Destination("BNS", "Batu Night Spectacular (BNS)", 900, 1380, 40000, 120, "hiburan"),                          # 15:00 - 23:00
    "Alun_Alun_Batu": Destination("Alun_Alun_Batu", "Alun-Alun Kota Batu & Pos Ketan", 0, 1440, 0, 60, "hiburan"),        # 24 Jam
    "Brawijaya_Oleh_Oleh": Destination("Brawijaya_Oleh_Oleh", "Pusat Oleh-Oleh Brawijaya", 480, 1320, 0, 45, "belanja"), # 08:00 - 22:00
}

# Matriks estimasi waktu tempuh antar lokasi (dalam menit)
TRAVEL_TIMES = {
    ("Stasiun_Malang", "Hotel_Batu"): 45,
    ("Stasiun_Malang", "Jatim_Park_2"): 50,
    ("Stasiun_Malang", "Alun_Alun_Batu"): 45,
    ("Hotel_Batu", "Jatim_Park_2"): 15,
    ("Hotel_Batu", "Museum_Angkut"): 12,
    ("Hotel_Batu", "Alun_Alun_Batu"): 10,
    ("Hotel_Batu", "Petik_Apel_Kusuma"): 15,
    ("Hotel_Batu", "Paralayang_Batu"): 30,
    ("Hotel_Batu", "BNS"): 18,
    ("Hotel_Batu", "Warung_Wareg"): 15,
    ("Hotel_Batu", "Brawijaya_Oleh_Oleh"): 10,
    ("Jatim_Park_2", "Museum_Angkut"): 12,
    ("Jatim_Park_2", "BNS"): 8,
    ("Jatim_Park_2", "Alun_Alun_Batu"): 15,
    ("Museum_Angkut", "Alun_Alun_Batu"): 10,
    ("Museum_Angkut", "Petik_Apel_Kusuma"): 12,
    ("Alun_Alun_Batu", "BNS"): 15,
    ("Alun_Alun_Batu", "Warung_Wareg"): 10,
    ("Alun_Alun_Batu", "Brawijaya_Oleh_Oleh"): 8,
    ("Petik_Apel_Kusuma", "Paralayang_Batu"): 20,
    ("BNS", "Brawijaya_Oleh_Oleh"): 12,
    ("Brawijaya_Oleh_Oleh", "Stasiun_Malang"): 40,
}

def get_travel_time(origin: str, dest: str) -> int:
    if origin == dest:
        return 0
    if (origin, dest) in TRAVEL_TIMES:
        return TRAVEL_TIMES[(origin, dest)]
    if (dest, origin) in TRAVEL_TIMES:
        return TRAVEL_TIMES[(dest, origin)]
    return 20 # Estimasi rata-rata dalam kota Batu jika tidak terdaftar eksplisit

def fmt_time(minutes: int) -> str:
    h = (minutes // 60) % 24
    m = minutes % 60
    return f"{h:02d}:{m:02d}"

# ==============================================================================
# 2. DEFINISI STRUKTUR STATE DAN OPERATOR STRIPS (DAFTAR-PAD)
# ==============================================================================

@dataclass
class WorldState:
    current_location: str
    current_time: int            # menit dari 00:00
    current_budget: int          # saldo rupiah
    visited: Set[str] = field(default_factory=set)
    tickets: Set[str] = field(default_factory=set)
    had_lunch: bool = False
    had_dinner: bool = False

    def clone(self) -> 'WorldState':
        return WorldState(
            current_location=self.current_location,
            current_time=self.current_time,
            current_budget=self.current_budget,
            visited=set(self.visited),
            tickets=set(self.tickets),
            had_lunch=self.had_lunch,
            had_dinner=self.had_dinner,
        )

    def to_predicate_set(self) -> Set[str]:
        """Representasi logika First-Order Logic (FOL) sesuai teori STRIPS."""
        preds = {f"AT({self.current_location})"}
        for v in self.visited:
            preds.add(f"VISITED({v})")
        for t in self.tickets:
            preds.add(f"HAS_TICKET({t})")
        if self.had_lunch:
            preds.add("HAD_LUNCH")
        if self.had_dinner:
            preds.add("HAD_DINNER")
        return preds

@dataclass
class STRIPSOperator:
    name: str
    action_type: str            # 'TRAVEL', 'BUY_TICKET', 'VISIT', 'EAT', 'FINISH'
    target: str
    preconditions_desc: str     # Representasi P untuk laporan
    add_list_desc: str          # Representasi A untuk laporan
    delete_list_desc: str       # Representasi D untuk laporan
    duration_cost: int          # waktu tambahan (menit)
    money_cost: int             # biaya tambahan (rupiah)

    def is_applicable(self, state: WorldState, max_end_time: int = 1320) -> Tuple[bool, str]:
        """Mengecek Precondition (P) terhadap Current State."""
        if self.action_type == "TRAVEL":
            if state.current_location == self.target:
                return False, "Sudah berada di lokasi ini."
            t_time = get_travel_time(state.current_location, self.target)
            if state.current_time + t_time > max_end_time:
                return False, "Waktu tidak mencukupi untuk perjalanan."
            return True, "OK"

        elif self.action_type == "BUY_TICKET":
            dest = DESTINATIONS[self.target]
            if state.current_location != self.target:
                return False, f"Harus berada di {dest.name} untuk membeli tiket."
            if self.target in state.tickets:
                return False, "Tiket sudah dibeli sebelumnya."
            if self.target in state.visited:
                return False, "Destinasi sudah pernah dikunjungi."
            if state.current_budget < dest.ticket_price:
                return False, f"Budget tidak cukup (butuh Rp{dest.ticket_price:,})."
            return True, "OK"

        elif self.action_type == "VISIT":
            dest = DESTINATIONS[self.target]
            if state.current_location != self.target:
                return False, f"Harus berada di {dest.name}."
            if dest.ticket_price > 0 and (self.target not in state.tickets):
                return False, "Belum membeli tiket masuk."
            if self.target in state.visited:
                return False, "Destinasi sudah pernah dikunjungi."
            if state.current_time < dest.open_time:
                return False, f"Belum buka (buka jam {fmt_time(dest.open_time)})."
            if state.current_time + dest.duration > dest.close_time:
                return False, f"Melebihi jam tutup (tutup jam {fmt_time(dest.close_time)})."
            if state.current_time + dest.duration > max_end_time:
                return False, "Melebihi batas maksimal waktu trip harian."
            return True, "OK"

        elif self.action_type == "EAT":
            # Makan siang jam 11:30 - 14:00 (690 - 840)
            # Makan malam jam 18:00 - 20:30 (1080 - 1230)
            if self.target == "LUNCH":
                if state.had_lunch:
                    return False, "Sudah makan siang."
                if not (660 <= state.current_time <= 870): # 11:00 - 14:30
                    return False, "Bukan jendela waktu makan siang."
            elif self.target == "DINNER":
                if state.had_dinner:
                    return False, "Sudah makan malam."
                if not (1050 <= state.current_time <= 1260): # 17:30 - 21:00
                    return False, "Bukan jendela waktu makan malam."
            if state.current_budget < self.money_cost:
                return False, "Budget tidak cukup untuk makan."
            return True, "OK"

        return False, "Aksi tidak dikenali"

    def apply(self, state: WorldState) -> WorldState:
        """Menerapkan Add (A) dan Delete (D) List ke State."""
        new_state = state.clone()
        if self.action_type == "TRAVEL":
            t_time = get_travel_time(state.current_location, self.target)
            new_state.current_location = self.target
            new_state.current_time += t_time

        elif self.action_type == "BUY_TICKET":
            dest = DESTINATIONS[self.target]
            new_state.tickets.add(self.target)
            new_state.current_budget -= dest.ticket_price

        elif self.action_type == "VISIT":
            dest = DESTINATIONS[self.target]
            new_state.visited.add(self.target)
            if self.target in new_state.tickets:
                new_state.tickets.remove(self.target) # tiket dikonsumsi
            new_state.current_time += dest.duration

        elif self.action_type == "EAT":
            new_state.current_time += self.duration_cost
            new_state.current_budget -= self.money_cost
            if self.target == "LUNCH":
                new_state.had_lunch = True
            elif self.target == "DINNER":
                new_state.had_dinner = True

        return new_state

# ==============================================================================
# 3. MESIN STRIPS PLANNER (FORWARD STATE-SPACE PLANNING WITH HEURISTIC)
# ==============================================================================

@dataclass
class PlanStep:
    step_no: int
    operator_name: str
    action_type: str
    description: str
    location: str
    start_time_str: str
    end_time_str: str
    duration_min: int
    cost_rp: int
    remaining_budget_rp: int
    precondition: str
    add_effect: str
    delete_effect: str

class STRIPSTourPlanner:
    def __init__(self, start_location: str, start_time_min: int, budget: int, goals: List[str], final_location: str = "Hotel_Batu", max_end_time: int = 1320):
        self.initial_state = WorldState(
            current_location=start_location,
            current_time=start_time_min,
            current_budget=budget,
            visited=set(),
            tickets=set(),
            had_lunch=False,
            had_dinner=False
        )
        self.goals = set(goals)
        self.final_location = final_location
        self.max_end_time = max_end_time # Default 22:00 (1320 menit)

    def is_goal_satisfied(self, state: WorldState) -> bool:
        # Semua target destinasi harus sudah dikunjungi
        if not self.goals.issubset(state.visited):
            return False
        # Harus berada di lokasi akhir (misal kembali ke hotel)
        if state.current_location != self.final_location:
            return False
        return True

    def generate_operators(self, state: WorldState) -> List[STRIPSOperator]:
        """Membangkitkan operator yang relevan dengan state saat ini."""
        ops = []
        unvisited_goals = self.goals - state.visited

        # 1. Jika di lokasi tujuan dan butuh tiket tapi belum punya -> BUY_TICKET
        if state.current_location in unvisited_goals:
            dest = DESTINATIONS[state.current_location]
            if dest.ticket_price > 0 and (state.current_location not in state.tickets):
                ops.append(STRIPSOperator(
                    name=f"BUY_TICKET({dest.id})",
                    action_type="BUY_TICKET",
                    target=dest.id,
                    preconditions_desc=f"AT({dest.id}) ∧ ¬HAS_TICKET({dest.id}) ∧ BUDGET≥{dest.ticket_price}",
                    add_list_desc=f"HAS_TICKET({dest.id})",
                    delete_list_desc="¬(BUDGET_LAMA)",
                    duration_cost=5,
                    money_cost=dest.ticket_price
                ))

        # 2. Jika di lokasi tujuan dan syarat terpenuhi -> VISIT
        if state.current_location in unvisited_goals:
            dest = DESTINATIONS[state.current_location]
            has_ticket_or_free = (dest.ticket_price == 0) or (state.current_location in state.tickets)
            if has_ticket_or_free:
                ops.append(STRIPSOperator(
                    name=f"VISIT({dest.id})",
                    action_type="VISIT",
                    target=dest.id,
                    preconditions_desc=f"AT({dest.id}) ∧ HAS_TICKET({dest.id}) ∧ OPEN_HOURS({fmt_time(dest.open_time)}-{fmt_time(dest.close_time)})",
                    add_list_desc=f"VISITED({dest.id})",
                    delete_list_desc=f"HAS_TICKET({dest.id})",
                    duration_cost=dest.duration,
                    money_cost=0
                ))

        # 3. Pilihan TRAVEL ke destinasi belum dikunjungi
        # Optimasi Heuristik Perjalanan: prioritaskan destinasi yang sudah buka atau buka segera
        for g in unvisited_goals:
            if g != state.current_location:
                t_time = get_travel_time(state.current_location, g)
                dest = DESTINATIONS[g]
                arrival = state.current_time + t_time
                # Cek apakah ada destinasi lain yang saat ini sudah buka
                other_open_available = any(
                    og != g and og != state.current_location and 
                    (DESTINATIONS[og].open_time <= state.current_time + get_travel_time(state.current_location, og) <= DESTINATIONS[og].close_time - DESTINATIONS[og].duration)
                    for og in unvisited_goals
                )
                # Jika masih tutup > 45 menit lagi dan ada destinasi lain yang buka, tunda travel ke destinasi ini
                if dest.is_attraction and (arrival + 45 < dest.open_time) and other_open_available:
                    continue

                ops.append(STRIPSOperator(
                    name=f"TRAVEL({state.current_location}, {g})",
                    action_type="TRAVEL",
                    target=g,
                    preconditions_desc=f"AT({state.current_location}) ∧ CAN_REACH({g}) ∧ TIME+{t_time}≤MAX_TIME",
                    add_list_desc=f"AT({g})",
                    delete_list_desc=f"AT({state.current_location})",
                    duration_cost=t_time,
                    money_cost=0
                ))

        # 4. Jika semua destinasi sudah dikunjungi tapi belum di lokasi akhir -> TRAVEL ke final_location
        if len(unvisited_goals) == 0 and state.current_location != self.final_location:
            t_time = get_travel_time(state.current_location, self.final_location)
            ops.append(STRIPSOperator(
                name=f"TRAVEL({state.current_location}, {self.final_location})",
                action_type="TRAVEL",
                target=self.final_location,
                preconditions_desc=f"AT({state.current_location}) ∧ ALL_VISITED ∧ TIME+{t_time}≤MAX_TIME",
                add_list_desc=f"AT({self.final_location})",
                delete_list_desc=f"AT({state.current_location})",
                duration_cost=t_time,
                money_cost=0
            ))

        # 5. Opsi Makan Siang / Malam jika berada di rentang waktu
        if not state.had_lunch and (690 <= state.current_time <= 840): # 11:30 - 14:00
            ops.append(STRIPSOperator(
                name="EAT(LUNCH)",
                action_type="EAT",
                target="LUNCH",
                preconditions_desc="¬HAD_LUNCH ∧ TIME(11:30-14:00) ∧ BUDGET≥35000",
                add_list_desc="HAD_LUNCH",
                delete_list_desc="¬(BUDGET_LAMA)",
                duration_cost=45,
                money_cost=35000
            ))

        if not state.had_dinner and (1080 <= state.current_time <= 1230): # 18:00 - 20:30
            ops.append(STRIPSOperator(
                name="EAT(DINNER)",
                action_type="EAT",
                target="DINNER",
                preconditions_desc="¬HAD_DINNER ∧ TIME(18:00-20:30) ∧ BUDGET≥40000",
                add_list_desc="HAD_DINNER",
                delete_list_desc="¬(BUDGET_LAMA)",
                duration_cost=50,
                money_cost=40000
            ))

        return ops

    def solve(self) -> Optional[List[PlanStep]]:
        """Mencari sekuens rencana aksi STRIPS menggunakan State-Space A* Search."""
        # Priority Queue item: (f_score, state_hash, current_state, plan_steps)
        initial = self.initial_state
        visited_hashes = set()

        def state_key(s: WorldState) -> str:
            return f"{s.current_location}|{tuple(sorted(s.visited))}|{tuple(sorted(s.tickets))}|{s.had_lunch}|{s.had_dinner}"

        def heuristic(s: WorldState) -> int:
            remaining = len(self.goals - s.visited)
            need_return = 1 if s.current_location != self.final_location else 0
            return (remaining * 60) + (need_return * 20)

        # Priority queue: (cost + heuristic, cost, tie_breaker, state, steps)
        counter = 0
        pq = [(heuristic(initial), 0, counter, initial, [])]

        while pq:
            f, cost, _, curr_state, steps = heapq.heappop(pq)

            if self.is_goal_satisfied(curr_state):
                return steps

            s_key = (state_key(curr_state), curr_state.current_time // 15)
            if s_key in visited_hashes:
                continue
            visited_hashes.add(s_key)

            operators = self.generate_operators(curr_state)
            for op in operators:
                applicable, reason = op.is_applicable(curr_state, self.max_end_time)
                if not applicable:
                    continue

                start_t = curr_state.current_time
                next_state = op.apply(curr_state)
                end_t = next_state.current_time

                # Buat deskripsi yang ramah pengguna
                desc = ""
                if op.action_type == "TRAVEL":
                    orig_n = DESTINATIONS[curr_state.current_location].name
                    dest_n = DESTINATIONS[op.target].name
                    desc = f"Perjalanan dari {orig_n} menuju {dest_n}"
                elif op.action_type == "BUY_TICKET":
                    dest_n = DESTINATIONS[op.target].name
                    desc = f"Membeli tiket masuk {dest_n} (Rp{op.money_cost:,})"
                elif op.action_type == "VISIT":
                    dest_n = DESTINATIONS[op.target].name
                    desc = f"Eksplorasi dan menikmati wisata di {dest_n}"
                elif op.action_type == "EAT":
                    jenis = "Siang" if op.target == "LUNCH" else "Malam"
                    loc_n = DESTINATIONS[curr_state.current_location].name
                    desc = f"Istirahat & Makan {jenis} di area {loc_n}"

                step_info = PlanStep(
                    step_no=len(steps) + 1,
                    operator_name=op.name,
                    action_type=op.action_type,
                    description=desc,
                    location=DESTINATIONS[next_state.current_location].name,
                    start_time_str=fmt_time(start_t),
                    end_time_str=fmt_time(end_t),
                    duration_min=end_t - start_t,
                    cost_rp=op.money_cost,
                    remaining_budget_rp=next_state.current_budget,
                    precondition=op.preconditions_desc,
                    add_effect=op.add_list_desc,
                    delete_effect=op.delete_list_desc
                )

                new_steps = steps + [step_info]
                new_cost = end_t - self.initial_state.current_time
                h = heuristic(next_state)
                counter += 1
                heapq.heappush(pq, (new_cost + h, new_cost, counter, next_state, new_steps))

        return None

# ==============================================================================
# 4. DEMO RUNNER
# ==============================================================================

if __name__ == "__main__":
    print("=" * 75)
    print("SISTEM PERENCANAAN OTOMATIS JADWAL WISATA KOTA BATU (STRIPS PLANNER)")
    print("Mata Kuliah: Artificial Intelligence | Kelompok 8")
    print("=" * 75)

    # Contoh Kasus Uji: Wisata Edukasi & Hiburan Populer Kota Batu
    # Goals: Mengunjungi Jatim Park 2, Museum Angkut, dan Alun-Alun Batu
    test_goals = ["Jatim_Park_2", "Museum_Angkut", "Alun_Alun_Batu"]
    start_loc = "Stasiun_Malang"
    start_time = 480       # 08:00 WIB
    budget = 400000        # Rp 400.000

    print(f"\n[KONFIGURASI AWAL WISATAWAN]")
    print(f"- Titik Awal      : {DESTINATIONS[start_loc].name}")
    print(f"- Jam Kedatangan  : {fmt_time(start_time)} WIB")
    print(f"- Anggaran Awal   : Rp{budget:,}")
    print(f"- Target Destinasi: {', '.join([DESTINATIONS[g].name for g in test_goals])}")
    print(f"- Titik Akhir     : Hotel / Penginapan di Batu")
    print("-" * 75)

    planner = STRIPSTourPlanner(
        start_location=start_loc,
        start_time_min=start_time,
        budget=budget,
        goals=test_goals,
        final_location="Hotel_Batu",
        max_end_time=1320 # 22:00 WIB
    )

    plan = planner.solve()

    if plan:
        print(f"\n[RENCANA AKSI TERCIPTA - TOTAL {len(plan)} LANGKAH OPERATOR STRIPS]")
        print(f"{'No':<3} | {'Waktu':<11} | {'Operator':<28} | {'Lokasi':<30} | {'Biaya':<10}")
        print("-" * 90)
        for p in plan:
            print(f"{p.step_no:<3} | {p.start_time_str}-{p.end_time_str} | {p.operator_name:<28} | {p.location[:28]:<30} | Rp{p.cost_rp:<9,}")
        
        print("\n" + "=" * 75)
        print("RINCIAN FORMAL DAFTAR-PAD (PRECONDITION, ADD, DELETE) PER LANGKAH:")
        print("=" * 75)
        for p in plan:
            print(f"\nLangkah #{p.step_no}: {p.operator_name} ({p.start_time_str} - {p.end_time_str})")
            print(f"  > Deskripsi   : {p.description}")
            print(f"  > P (Precond) : {p.precondition}")
            print(f"  > A (Add)     : {p.add_effect}")
            print(f"  > D (Delete)  : {p.delete_effect}")
            print(f"  > Sisa Budget : Rp{p.remaining_budget_rp:,}")
    else:
        print("\n[GAGAL] Tidak ditemukan urutan aksi STRIPS yang valid dengan batasan yang diberikan.")
