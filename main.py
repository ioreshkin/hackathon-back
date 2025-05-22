from fastapi import FastAPI, APIRouter
import httpx
import asyncio
import time
from config import settings
from data_module import data

app = FastAPI()
router = APIRouter(prefix="/devices", tags=["devices"])

SIGNAL_TYPES = ['hum', 'term', 'co2', 'lux', 'air-iaq']
NOTIFY_SETTINGS = {'hum':True, 'term':True, 'co2':True, 'lux':True, 'air-iaq':True}

EG = ['a6353755-751e-463c-9832-fc8611d70e32',
      '7c207da1-633c-409b-8269-a24d9134f57e',
      'e0c5a923-fbe2-48a2-90cd-b33dec7bd257',
      '8853034c-5afc-4a9c-9481-e6012f3bd97b',
      'ac267939-9376-43b9-b374-6c1eec93af97']

SERIAL = ['17036925610005156',
          '17048841600013400',
          '17048877610019909',
          '17038509610000005',
          '17038365640000008']

APARTMENT_ID = [2112, 2113, 2114, 2116, 2117]

client = httpx.AsyncClient(
    base_url=settings.API_HOST,
    headers={
        "Authorization": f"Bearer {settings.API_TOKEN}",
        "Content-Type": "application/json"
    },
    timeout=10,
    follow_redirects=True
)

NORMAL_RANGES = {
    'hum': 2,
    'term': 2,
    'co2': 2,
    'lux': 2,
    'air-iaq': 2
}

report = []
chart_data = [[[] for _ in range(5)] for _ in SIGNAL_TYPES]
event_firsts = [{} for _ in range(5)]
new_events_buffer = []
last_alerts = [{} for _ in range(5)]
current_time_step = -1

def classify(value: float, normal: float) -> int:
    if value <= normal:
        return 1
    elif value <= normal + 5:
        return 2
    else:
        return 3

async def send_signal(signal_name, value, serial, eg):
    params = {
        "eg": eg, "egt": "6", "token": settings.API_TOKEN,
        "serialnumber": serial,
        "value": value,
        "signal_name": signal_name
    }
    await client.get("/api/huk/update_intensity_device/", params=params)

async def check_and_log(flat_idx: int, time_idx: int):
    params = {
        "eg": EG[flat_idx],
        "egt": "6",
        "token": settings.API_TOKEN,
        "apartment_id": APARTMENT_ID[flat_idx]
    }

    try:
        response = await client.get("/api/huk/get-device-signals/", params=params)
        response.raise_for_status()
        payload = response.json()
    except Exception as e:
        print(f"⚠️ Ошибка при получении данных квартиры {flat_idx + 1}: {e}")
        return

    device_signals = payload.get("data", {}).get("signals", {})

    for serial, signals in device_signals.items():
        for signal in signals:
            name = signal.get("name")
            value = signal.get("intensity")

            if name not in SIGNAL_TYPES:
                continue

            if time_idx % 2 == 0:
                param_idx = SIGNAL_TYPES.index(name)
                chart_data[param_idx][flat_idx].append(value)

            level = classify(value, NORMAL_RANGES[name])

            report.append({
                "flat": flat_idx,
                "serial": serial,
                "signal": name,
                "value": value,
                "level": level,
                "time": time_idx
            })

            if name not in event_firsts[flat_idx]:
                event_firsts[flat_idx][name] = {}
            if level in (2, 3) and level not in event_firsts[flat_idx][name]:
                event_firsts[flat_idx][name][level] = time_idx

            alert_info = last_alerts[flat_idx].get(name, {})
            last_level = alert_info.get("level", 0)
            last_step = alert_info.get("last_alert_step", -999)

            should_alert = False
            if level > last_level:
                should_alert = True
            elif level == last_level and level >= 2 and time_idx - last_step >= 2:
                should_alert = True

            if should_alert and level >= 2:
                new_events_buffer.append({
                    "flat": flat_idx + 1,
                    "parameter": name,
                    "level": "critical" if level == 3 else "warning",
                    "timestamp": int(time.time())
                })
                last_alerts[flat_idx][name] = {
                    "level": level,
                    "last_alert_step": time_idx
                }

async def simulate_day():
    global current_time_step
    for time_idx in range(48):
        print(f"\n======= Цикл {time_idx + 1}/48 =======")
        send_tasks = []

        for flat_idx in range(5):
            for sig_idx, sig_name in enumerate(SIGNAL_TYPES):
                value = data[flat_idx][sig_idx][time_idx]
                send_tasks.append(send_signal(
                    signal_name=sig_name,
                    value=value,
                    serial=SERIAL[flat_idx],
                    eg=EG[flat_idx]
                ))

        await asyncio.gather(*send_tasks)
        await asyncio.sleep(0.2)

        check_tasks = [
            check_and_log(flat_idx, time_idx)
            for flat_idx in range(5)
        ]
        await asyncio.gather(*check_tasks)

        current_time_step = time_idx

    print("\n📝 Симуляция завершена. Записей в отчёте:", len(report))

@router.post("/simulate")
async def run_simulation():
    await simulate_day()
    return {"status": "ok", "message": "Симуляция завершена"}

@router.get("/report_data")
async def get_report_data():
    result = {}
    for param_idx, param_name in enumerate(SIGNAL_TYPES):
        result[param_name] = {
            f"flat_{flat_idx + 1}": chart_data[param_idx][flat_idx]
            for flat_idx in range(5)
        }
    return result

@router.get("/anomalies")
async def get_anomalies():
    global new_events_buffer
    response = new_events_buffer.copy()
    new_events_buffer.clear()
    filtered_response = [
        event for event in response
        if event['level'] == 'critical' or 
            (event['parameter'] in NOTIFY_SETTINGS and NOTIFY_SETTINGS[event['parameter']])
    ]
    return filtered_response

@router.get("/report")
async def get_human_readable_report():
    output = []
    for flat_idx, events in enumerate(event_firsts):
        flat_title = f"🏠 Квартира №{flat_idx + 1}:"
        lines = [flat_title]

        for param, times in events.items():
            if 2 in times:
                lines.append(f"Аномалия параметра '{param}' началась в {round(times[2] * 0.5, 1)} ч.")
            if 3 in times:
                lines.append(f"Критическое превышение параметра '{param}' зафиксировано в {round(times[3] * 0.5, 1)} ч.")
        
        if len(lines) == 1:
            lines.append("✅ Без отклонений за сутки.")

        output.append("\n".join(lines))
    
    return {"summary": output}

@router.get("/status")
async def get_current_status():
    relevant = [entry for entry in report if entry["time"] == current_time_step and entry["level"] >= 2]

    unique = {}
    for entry in reversed(relevant):
        key = (entry["flat"], entry["signal"])
        if key not in unique:
            unique[key] = {
                "flat": entry["flat"] + 1,
                "parameter": entry["signal"],
                "level": "critical" if entry["level"] == 3 else "warning",
                "timestamp": int(time.time())
            }

    return list(unique.values())

app.include_router(router)
