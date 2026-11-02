#!/usr/bin/env python3
"""
Unit Test Suite Formal untuk Engine STRIPS Tour Planner Kota Batu
Mata Kuliah: Artificial Intelligence | Kelompok 8 (Kelas A)
Framework: unittest (Python Standard Library - Zero Dependency)
"""

import unittest
from strips_planner import (
    DESTINATIONS,
    STRIPSTourPlanner,
    WorldState,
    STRIPSOperator,
    get_travel_time,
    fmt_time
)

class TestSTRIPSKnowledgeBase(unittest.TestCase):
    """Pengujian validitas basis pengetahuan 14 destinasi wisata Kota Batu."""

    def test_destination_count(self):
        """Memastikan seluruh 14 titik lokasi terdaftar dalam basis pengetahuan."""
        self.assertGreaterEqual(len(DESTINATIONS), 14)

    def test_operating_hours_integrity(self):
        """Memastikan jam buka selalu lebih awal dari jam tutup untuk wahana wisata."""
        for dest_id, d in DESTINATIONS.items():
            if d.is_attraction and d.close_time > 0:
                self.assertLess(d.open_time, d.close_time, f"Jam operasional {d.name} tidak konsisten!")

    def test_travel_time_symmetry(self):
        """Memastikan fungsi get_travel_time simetris dan bernilai positif."""
        time_ab = get_travel_time("Stasiun_Malang", "Hotel_Batu")
        time_ba = get_travel_time("Hotel_Batu", "Stasiun_Malang")
        self.assertGreater(time_ab, 0)
        self.assertEqual(time_ab, time_ba)


class TestSTRIPSOperators(unittest.TestCase):
    """Pengujian formal terhadap model operator PAD (Precondition, Action, Delete, Add)."""

    def setUp(self):
        self.initial_state = WorldState(
            current_location="Hotel_Batu",
            current_time=510, # 08:30 WIB
            current_budget=500000,
            visited=set(),
            tickets=set(),
            had_lunch=False,
            had_dinner=False
        )

    def test_buy_ticket_insufficient_budget(self):
        """Operator BUY_TICKET harus menolak eksekusi jika budget tidak mencukupi."""
        poor_state = self.initial_state.clone()
        poor_state.current_budget = 10000 # Cuma 10rb
        poor_state.current_location = "Jatim_Park_2"
        
        op = STRIPSOperator(
            name="BUY_TICKET(Jatim_Park_2)",
            action_type="BUY_TICKET",
            target="Jatim_Park_2",
            preconditions_desc="BUDGET>=110000",
            add_list_desc="HAS_TICKET",
            delete_list_desc="BUDGET",
            duration_cost=5,
            money_cost=110000
        )
        applicable, reason = op.is_applicable(poor_state)
        self.assertFalse(applicable)
        self.assertTrue("Budget tidak cukup" in reason or "Budget tidak mencukupi" in reason)

    def test_visit_precondition_requires_ticket(self):
        """Operator VISIT harus menolak eksekusi jika pengunjung belum memegang tiket."""
        state = self.initial_state.clone()
        state.current_location = "Jatim_Park_2"
        # tiket belum dibeli (tickets kosong)
        
        op = STRIPSOperator(
            name="VISIT(Jatim_Park_2)",
            action_type="VISIT",
            target="Jatim_Park_2",
            preconditions_desc="HAS_TICKET",
            add_list_desc="VISITED",
            delete_list_desc="HAS_TICKET",
            duration_cost=180,
            money_cost=0
        )
        applicable, reason = op.is_applicable(state)
        self.assertFalse(applicable)
        self.assertIn("Belum membeli tiket", reason)

    def test_state_transition_delete_and_add_effects(self):
        """Memastikan efek Add-List dan Delete-List mengubah state secara tepat."""
        state = self.initial_state.clone()
        state.current_location = "Jatim_Park_2"
        state.tickets.add("Jatim_Park_2")
        
        op = STRIPSOperator(
            name="VISIT(Jatim_Park_2)",
            action_type="VISIT",
            target="Jatim_Park_2",
            preconditions_desc="",
            add_list_desc="VISITED(Jatim_Park_2)",
            delete_list_desc="HAS_TICKET(Jatim_Park_2)",
            duration_cost=180,
            money_cost=0
        )
        next_state = op.apply(state)
        self.assertIn("Jatim_Park_2", next_state.visited)
        self.assertNotIn("Jatim_Park_2", next_state.tickets)
        self.assertEqual(next_state.current_time, 510 + 180)


class TestSTRIPSPlannerIntegration(unittest.TestCase):
    """Pengujian integrasi perencanaan otomatis rute nyata Kota Batu."""

    def test_solve_popular_tour_itinerary(self):
        """Menguji kasus nyata: Stasiun Malang -> JTP 2 -> Museum Angkut -> BNS -> Hotel."""
        planner = STRIPSTourPlanner(
            start_location="Stasiun_Malang",
            start_time_min=510, # 08:30 WIB
            budget=500000,
            goals=["Jatim_Park_2", "Museum_Angkut", "BNS"],
            final_location="Hotel_Batu",
            max_end_time=1320 # 22:00 WIB
        )
        plan = planner.solve()
        self.assertIsNotNone(plan, "STRIPS Planner gagal menemukan solusi rencana yang valid!")
        self.assertGreater(len(plan), 0)

        # Verifikasi bahwa semua target destinasi tercapai
        actions = [p.action_type for p in plan]
        self.assertIn("BUY_TICKET", actions)
        self.assertIn("VISIT", actions)
        self.assertIn("TRAVEL", actions)

        # Verifikasi destinasi akhir adalah Hotel
        last_step = plan[-1]
        self.assertIn("Hotel", last_step.location)

        # Verifikasi sisa saldo tidak minus
        self.assertGreaterEqual(last_step.remaining_budget_rp, 0)


if __name__ == "__main__":
    print("=" * 65)
    print("🧪 MENJALANKAN AUTOMATED UNIT TESTING STRIPS TOUR PLANNER")
    print("=" * 65)
    unittest.main(verbosity=2)
