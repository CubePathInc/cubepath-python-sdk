from __future__ import annotations

from cubepath.models.kubernetes import KubernetesPlan
from cubepath.models.vps import VPSPlan, VPSPlanOption


def test_vps_plan_discount_fields():
    p = VPSPlanOption.from_dict(
        {
            "plan_name": "gp.nano",
            "price_per_hour": 0.07639,
            "effective_price_per_hour": 0.03819,
            "discount_percent": 50,
            "discount_label": "Launch",
        }
    )
    assert p.price_per_hour == 0.07639
    assert p.effective_price_per_hour == 0.03819
    assert p.discount_percent == 50
    assert p.discount_label == "Launch"


def test_discount_fields_default_to_none():
    for cls in (VPSPlan, VPSPlanOption, KubernetesPlan):
        p = cls.from_dict({"price_per_hour": "0.1", "effective_price_per_hour": None})
        assert p.effective_price_per_hour is None
        assert p.discount_percent is None
        assert p.discount_label is None


def test_kubernetes_plan_location_id():
    assert KubernetesPlan.from_dict({"location_id": 5}).location_id == 5
    assert KubernetesPlan.from_dict({}).location_id is None
