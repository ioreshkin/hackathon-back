from fastapi import FastAPI, APIRouter, HTTPException
import httpx
import asyncio
import time
from datetime import datetime, timedelta
from config import settings
from data_module import data

app = FastAPI()
router = APIRouter(prefix="/devices", tags=["devices"])

SIGNAL_TYPES = ['hum', 'term', 'co2', 'lux', 'air-iaq']
NOTIFY_SETTINGS = {'hum': True, 'term': True, 'co2': True, 'lux': True, 'air-iaq': True}

HUMAN_PARAMETER_NAMES = {
    'term': 'температуры',
    'co2': 'CO₂',
    'hum': 'влажности',
    'lux': 'освещённости',
    'air-iaq': 'качества воздуха'
}

EG = [
    'a6353755-751e-463c-9832-fc8611d70e32',
    '7c207da1-633c-409b-8269-a24d9134f57e',
    'e0c5a923-fbe2-48a2-90cd-b33dec7bd257',
    '8853034c-5afc-4a9c-9481-e6012f3bd97b',
    'ac267939-9376-43b9-b374-6c1eec93af97'
]

SERIAL = [
    '17036925610005156',
    '17048841600013400',
    '17048877610019909',
    '17038509610000005',
    '17038365640000008'
]

APARTMENT_ID = [2112, 2113, 2114, 2116, 2117]

client = httpx.AsyncClient(
    base_url=settings.API_HOST,
    headers={
        "Authorization": f"Bearer {settings.API_TOKEN}",
        "Content-Type": "application/json"
    },
    timeout=20,
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
event_ends = [{} for _ in range(5)]
new_events_buffer = []
last_alerts = [{} for _ in range(5)]
current_time_step = -1
alert_log = []
alert_id_counter = 1
simulation_complete = False

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
    global alert_id_counter

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

            if level == 1 and name in event_firsts[flat_idx] and name not in event_ends[flat_idx]:
                event_ends[flat_idx][name] = time_idx

            prev = last_alerts[flat_idx].get(name)
            prev = last_alerts[flat_idx].get(name)
            if prev is None or prev["level"] != level:
                if level >= 2:
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

        check_tasks = [check_and_log(flat_idx, time_idx) for flat_idx in range(5)]
        await asyncio.gather(*check_tasks)
        current_time_step = time_idx
    print("\n📝 Симуляция завершена. Записей в отчёте:", len(report))

@router.post("/simulate")
async def run_simulation():
    await simulate_day()
    global simulation_complete
    simulation_complete = True
    return {"status": "ok", "message": "Симуляция завершена"}

@router.get("/report_data")
async def get_report_data():
    result = []
    for param_idx, param_name in enumerate(SIGNAL_TYPES):
        entry = {
            "parameter": param_name,
            "flats": [
                {
                    "id": flat_idx + 1,
                    "values": chart_data[param_idx][flat_idx]
                } for flat_idx in range(5)
            ]
        }
        result.append(entry)
    return result

@router.get("/anomalies")
async def get_anomalies():
    global new_events_buffer
    response = new_events_buffer.copy()
    new_events_buffer.clear()

    enriched_response = []
    for event in response:
        if event['level'] == 'critical' or (
            event['parameter'] in NOTIFY_SETTINGS and NOTIFY_SETTINGS[event['parameter']]
        ):
            human_name = HUMAN_PARAMETER_NAMES.get(event["parameter"], event["parameter"])
            level_text = "значительно повысилось" if event["level"] == "critical" else "повысилось"
            text = f"В квартире №{event['flat']} {level_text} значение {human_name}"
            enriched_response.append({
                **event,
                "text": text
            })

    return enriched_response

@router.get("/report")
async def get_structured_report():
    if not simulation_complete:
        return {"date": datetime.now().date().isoformat(), "events": []}

    report_output = []
    base_day = datetime.combine(datetime.now().date(), datetime.min.time())
    now = base_day + timedelta(minutes=30 * current_time_step)

    for flat_idx in range(5):
        for param, times in event_firsts[flat_idx].items():
            for level in [2, 3]:
                if level not in times:
                    continue

                time_idx = times[level]
                start_dt = base_day + timedelta(minutes=30 * time_idx)
                start_str = start_dt.strftime("%H:%M")

                end_time_idx = event_ends[flat_idx].get(param)
                if end_time_idx:
                    end_dt = base_day + timedelta(minutes=30 * end_time_idx)
                    end_str = end_dt.strftime("%H:%M")
                    duration_td = end_dt - start_dt
                else:
                    end_dt = None
                    end_str = None
                    duration_td = now - start_dt

                hours = duration_td.seconds // 3600
                minutes = (duration_td.seconds % 3600) // 60
                duration = f"{hours} ч. {minutes} мин."

                level_text = "Критическое" if level == 3 else "Аномальное"
                param_name = HUMAN_PARAMETER_NAMES.get(param, param)
                title = f"{level_text} превышение {param_name} в квартире №{flat_idx + 1}"
                summary = (
                    f"Превышение {param_name} в квартире №{flat_idx + 1} началось в {start_str} "
                    + (f"и закончилось в {end_str}." if end_str else f"и продолжается уже {duration}.")
                )

                report_output.append({
                    "flat": flat_idx + 1,
                    "parameter": param_name,
                    "level": "critical" if level == 3 else "warning",
                    "start_time": start_str,
                    "end_time": end_str,
                    "duration": duration,
                    "title": title,
                    "summary": summary
                })

    return {"date": now.date().isoformat(), "events": report_output}

@router.get("/report_text")
async def get_text_summary():
    get_structured_report()
    if not simulation_complete:
        return {"text": "Симуляция ещё не завершена."}

    # Собираем данные из report
    grouped = {}
    for entry in report:
        if entry["level"] < 2:
            continue
        flat = entry["flat"] + 1
        param = entry["signal"]
        level = "критическое" if entry["level"] == 3 else "аномальное"
        human_name = HUMAN_PARAMETER_NAMES.get(param, param)

        key = (flat, param, level)
        if key not in grouped:
            grouped[key] = entry["time"]

    # Сортируем по времени
    sorted_events = sorted(grouped.items(), key=lambda x: x[1])

    # Строим текст
    current_flat = None
    text = f"🧾 Хронология чрезвычайных ситуаций на {datetime.now().date()}:\n\n"
    for (flat, param, level), time_idx in sorted_events:
        human_name = HUMAN_PARAMETER_NAMES.get(param, param)
        time_str = f"{time_idx // 2:02}:{'30' if time_idx % 2 else '00'}"
        prefix = "Затем также" if current_flat == flat else "В квартире №" + str(flat)
        text += f"{prefix} {level} превышение {human_name} с {time_str}.\n"
        current_flat = flat

    return {"text": text.strip()}

@router.get("/status")
async def get_current_status():
    param_map = {
        'term': 'temp',
        'co2': 'co2',
        'hum': 'hum',
        'lux': 'lux',
        'air-iaq': 'airIaq'
    }
    flat_status = {
        i + 1: {
            "id": i + 1,
            "hum": "normal",
            "temp": "normal",
            "co2": "normal",
            "lux": "normal",
            "airIaq": "normal"
        } for i in range(5)
    }

    for entry in report:
        if entry["time"] != current_time_step:
            continue
        param_key = param_map.get(entry["signal"])
        if not param_key:
            continue

        level = "normal"
        if entry["level"] == 2:
            level = "warning"
        elif entry["level"] == 3:
            level = "critical"

        flat_status[entry["flat"] + 1][param_key] = level

    return list(flat_status.values())

@router.patch("/notify-settings")
async def update_notify_settings(settings: dict):
    for key in settings:
        if key not in NOTIFY_SETTINGS:
            raise HTTPException(status_code=400, detail=f"Недопустимый параметр: {key}.")
        if not isinstance(settings[key], bool):
            raise HTTPException(status_code=400, detail=f"Значение {key} должно быть True/False")
    NOTIFY_SETTINGS.update(settings)
    return {"message": "Настройки обновлены", "new_settings": NOTIFY_SETTINGS}

app.include_router(router, prefix="/api")