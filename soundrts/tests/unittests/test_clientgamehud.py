from soundrts.clientgamehud import HudPanel


class DummyOrder:
    keyword = "go"


class DummyUnit:
    type_name = "peasant"
    number = 3
    hp = 12
    hp_max = 20
    orders = [DummyOrder()]


class DummyInterface:
    display_is_active = False
    resources = [500, 200]
    used_food = 3
    available_food = 10
    last_virtual_time = 125
    speed = 1.0
    group = [1]
    dobjets = {1: DummyUnit()}

    def _get_relative_speed(self):
        return 1.5


def test_hud_snapshot_collects_gameplay_data():
    panel = HudPanel(DummyInterface())

    snapshot = panel.get_snapshot()

    assert snapshot.resources == ["Resource 1: 500", "Resource 2: 200"]
    assert snapshot.food == "Pop: 3/10"
    assert snapshot.time == "Time: 02:05"
    assert snapshot.speed == "Speed: x1.5"
    assert len(snapshot.units) == 1
    assert snapshot.units[0].label == "peasant #3"
    assert snapshot.units[0].hit_points == 12
    assert snapshot.units[0].max_hit_points == 20
    assert snapshot.units[0].status == "go"


def test_hud_event_buffer_keeps_recent_events_first():
    panel = HudPanel(DummyInterface())
    entity = DummyUnit()
    entity.place = type("Place", (), {"col": 2, "row": 4})()

    panel.on_event(entity, "complete")
    panel.on_event(entity, "under_attack")

    snapshot = panel.get_snapshot()

    assert snapshot.events[0] == "under attack: peasant at 2,4"
    assert snapshot.events[1] == "complete: peasant at 2,4"


def test_hud_event_buffer_is_bounded():
    panel = HudPanel(DummyInterface())
    entity = DummyUnit()

    for index in range(panel.max_events + 3):
        panel.on_event(entity, "event_{}".format(index))

    snapshot = panel.get_snapshot()

    assert len(snapshot.events) == panel.max_events
    assert snapshot.events[0].startswith("event {}".format(panel.max_events + 2))
