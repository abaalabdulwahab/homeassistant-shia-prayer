#!/usr/bin/env python3
"""
اختبار مباشر لـ HaqibatProvider على الـ Raspberry Pi.
شغّل: python3 test_haqibat.py
"""
import asyncio
import sys
import json
from datetime import date

# ── إعدادات الموقع (عدّلها حسب موقعك) ──────────────────────────────────────
LATITUDE        = 25.3  # خط العرض (الرياض مثلاً)
LONGITUDE       = 49.6  # خط الطول (الأحساء)
TIMEZONE_OFFSET = 3.0   # UTC+3 (السعودية)
# ─────────────────────────────────────────────────────────────────────────────

async def test_client():
    """Test the API client directly."""
    import aiohttp
    
    print("\n━━━ 1. اختبار API Client ━━━")
    
    from api.client import HmomenApiClient
    async with aiohttp.ClientSession() as session:
        client = HmomenApiClient(session)

        print("\n▶ Hijri Adjustment:")
        adj = await client.get_hijri_adjustment()
        print(json.dumps(adj, ensure_ascii=False, indent=2))

        print("\n▶ Ramadan Config:")
        ram = await client.get_ramadan_config()
        print(json.dumps(ram, ensure_ascii=False, indent=2))

        print("\n▶ Adhan Audio (أول 2):")
        audio = await client.get_adhan_audio()
        print(json.dumps(audio[:2], ensure_ascii=False, indent=2))
        print(f"  إجمالي: {len(audio)} صوت")


def test_hijri():
    """Test Hijri date calculation."""
    print("\n━━━ 2. اختبار التاريخ الهجري ━━━")
    
    from api.hijri import gregorian_to_hijri
    
    today = date.today()
    hijri = gregorian_to_hijri(today, adjustment_days=-1)  # -1 من API
    
    print(f"  الميلادي:  {today}")
    print(f"  الهجري:    {hijri.full_date_ar}")
    print(f"  المناسبة:  {hijri.event or 'لا توجد'}")
    print(f"  هيكل كامل: {hijri.to_dict()}")


def test_prayer_times():
    """Test prayer time calculation."""
    print("\n━━━ 3. اختبار أوقات الصلاة ━━━")
    
    from api.prayer_calc import calculate_prayer_times
    from datetime import datetime
    
    today = date.today()
    prayers = calculate_prayer_times(
        target_date=today,
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone_offset=TIMEZONE_OFFSET,
    )
    
    times = prayers.to_dict()
    labels = {
        "fajr": "الفجر", "sunrise": "الشروق", "dhuhr": "الظهر",
        "asr": "العصر", "maghrib": "المغرب", "isha": "العشاء",
    }
    for key, label in labels.items():
        print(f"  {label:10} {times[key]}")
    
    now = datetime.now()
    next_p = prayers.next_prayer(now)
    if next_p:
        print(f"\n  الصلاة القادمة: {next_p[0]} في {next_p[1].strftime('%H:%M')}")


async def test_provider():
    """Test the full provider."""
    print("\n━━━ 4. اختبار Provider الكامل ━━━")
    
    from providers.haqibat import HaqibatProvider
    
    provider = HaqibatProvider(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        timezone_offset=TIMEZONE_OFFSET,
    )
    
    data = await provider.async_update()
    
    print("\n  ✅ البيانات الكاملة:")
    for key, value in data.items():
        print(f"  {key:25} = {value}")
    
    await provider.close()


async def main():
    print("╔══════════════════════════════════════╗")
    print("║   اختبار Haqibat Provider            ║")
    print("╚══════════════════════════════════════╝")
    
    # تأكد إنك في مجلد shia_prayer
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(script_dir, ".."))
    
    try:
        test_hijri()
    except Exception as e:
        print(f"  ❌ خطأ في الهجري: {e}")

    try:
        test_prayer_times()
    except Exception as e:
        print(f"  ❌ خطأ في الصلاة: {e}")

    try:
        await test_client()
    except Exception as e:
        print(f"  ❌ خطأ في API Client: {e}")

    try:
        await test_provider()
    except Exception as e:
        print(f"  ❌ خطأ في Provider: {e}")

    print("\n✅ انتهى الاختبار")


if __name__ == "__main__":
    asyncio.run(main())
