# Xiaomi Smart Pet Food Feeder 2 — Home Assistant Custom Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![PyPI version](https://img.shields.io/pypi/v/xiaomi-feeder-2.svg?style=for-the-badge&color=blue)](https://pypi.org/project/xiaomi-feeder-2/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](LICENSE)

A high-performance, 100% local **Home Assistant Community Store (HACS)** custom integration for the **Xiaomi Smart Pet Food Feeder 2 (`xiaomi.feeder.iv2001`)**, powered by the [`xiaomi-feeder-2`](https://pypi.org/project/xiaomi-feeder-2/) library.

---

## ✨ Features

- ⚡ **100% Local MIoT Control**: Zero cloud latency, works entirely on your local Wi-Fi network.
- ⚖️ **Real-time Bowl Scale & Intake**: Live bowl food weight in grams ($g$), cumulative daily food intake, last meal intake, and tare/zero calibration.
- 🕒 **Hybrid Offline Schedules**: Decodes and flashes internal device EEPROM schedules (`HHMMPPRR`) for safe offline execution without losing timing if Wi-Fi or HA goes down.
- 🛑 **Dynamic "Skip Next Meal"**: Temporarily pause upcoming scheduled feedings (e.g. when feeding wet food or treats) and automatically restore the recurring schedule afterwards.
- ⏳ **Persistent Desiccant Tracker**: Track desiccant lifespan with countdown days, replacement alerts, and one-click reset button saved permanently across HA restarts.
- 🌙 **Day/Night Screen Management**: Automated display sleep and wake triggers according to time of day or sun position.
- 🛡️ **Safety Protections**: Real-time sensors for food jams, motor stalls, dispense failures, and chute heap accumulation.
- 📊 **Rich Dashboard Compatibility**: Out-of-the-box support for [`cristianchelu/dispenser-schedule-card`](https://github.com/cristianchelu/dispenser-schedule-card) and [`m1xminus/petfeeder-card`](https://github.com/m1xminus/petfeeder-card).

---

## 📦 Installation

### Method 1: Via HACS (Recommended)
1. Open **HACS** in your Home Assistant UI.
2. Click the three dots in the upper right corner and select **Custom repositories**.
3. Add Repository URL: `https://github.com/DerSteph/ha-xiaomi-feeder`
4. Category: **Integration**
5. Click **Add**, find **Xiaomi Smart Pet Feeder 2**, and click **Download**.
6. Restart Home Assistant.

### Method 2: Manual Installation
1. Copy the `custom_components/xiaomi_feeder` folder into your Home Assistant `<config>/custom_components/` directory.
2. Restart Home Assistant.

---

## ⚙️ Configuration

1. In Home Assistant, go to **Settings** $\rightarrow$ **Devices & Services** $\rightarrow$ **Add Integration**.
2. Search for **Xiaomi Smart Pet Feeder 2**.
3. Enter your feeder's **IP Address** and **32-character Local Device Token**.
4. Click **Submit**.

---

## 📋 Entities Provided

### 📊 Telemetry & Sensors
| Entity | Name | Description |
| :--- | :--- | :--- |
| `sensor.<device>_bowl_weight` | Bowl Food Weight | Live weight in bowl ($g$) |
| `sensor.<device>_daily_eaten` | Daily Eaten Weight | Total grams eaten today ($g$) |
| `sensor.<device>_last_meal_intake` | Last Meal Intake | Grams consumed in last meal |
| `sensor.<device>_previous_meal_intake`| Previous Meal Intake | Grams consumed in prior meal |
| `sensor.<device>_next_feeding` | Next Feeding | Next meal timestamp & portion count |
| `sensor.<device>_schedule_count` | Schedule Meals Count | Number of EEPROM meals stored |
| `sensor.<device>_desiccant_days_left` | Desiccant Days Left | Days before desiccant change |
| `sensor.<device>_desiccant_expiry` | Desiccant Expiry Date | Exact expiry timestamp |
| `sensor.<device>_feed_history` | Feeding History | History array for timeline cards |
| `sensor.<device>_last_feed_event` | Last Feed Event | Summary of last feed event |
| `sensor.<device>_daily_progress` | Daily Plan Progress | % of today's schedule dispensed |

### 🚨 Binary Sensors & Alarms
| Entity | Name | Description |
| :--- | :--- | :--- |
| `binary_sensor.<device>_hopper_low` | Hopper Low | Food level empty/low warning |
| `binary_sensor.<device>_food_stuck` | Food Stuck / Motor Jam | Rotor blocked alert |
| `binary_sensor.<device>_dispense_error` | Dispense Error | Dispense failure |
| `binary_sensor.<device>_food_heap` | Food Heap Detected | Food accumulation at chute |
| `binary_sensor.<device>_dispensing` | Dispensing | Active during motor rotation |
| `binary_sensor.<device>_refill_alert` | Refill Alert | Refill interval timer expired |
| `binary_sensor.<device>_desiccant_expired` | Desiccant Expired | Desiccant replacement due |
| `binary_sensor.<device>_fault` | Device Fault | General hardware fault |

### 🎛️ Controls, Numbers & Switches
| Entity | Type | Description |
| :--- | :--- | :--- |
| `button.<device>_feed` | Button | Dispenses manual portions |
| `button.<device>_tare_scale` | Button | Tares/calibrates bowl weight scale |
| `button.<device>_reset_desiccant` | Button | Resets desiccant countdown timer |
| `button.<device>_clear_schedule` | Button | Wipes device EEPROM schedule memory |
| `number.<device>_manual_portions` | Number (1–30) | Configures portions for manual feed |
| `number.<device>_target_portions` | Number (1–30) | Feeder RAM default portion setting |
| `number.<device>_desiccant_lifespan`| Number (1–180d) | Desiccant lifespan duration in days |
| `switch.<device>_skip_next_meal` | Switch | Pauses next upcoming meal & auto-resumes |
| `switch.<device>_screen_auto_sleep` | Switch | Day/night display sleep mode |
| `switch.<device>_screen_progress` | Switch | Screen lights up during dispensing |
| `switch.<device>_child_lock` | Switch | Locks physical top dispenser button |
| `switch.<device>_anti_stacking` | Switch | Motor anti-accumulation reverse rotation |
| `switch.<device>_grain_compensation`| Switch | Kibble weight auto-compensation |
| `switch.<device>_schedule_enabled` | Switch | Master toggle for internal EEPROM schedule |
| `select.<device>_screen_display` | Select | Metric mode: `left`, `eaten`, `percentage` |
| `text.<device>_hardware_schedule` | Text | Hardware schedule hex string |

---

## 🎨 Lovelace Dashboard Examples

### 1. Dispenser Schedule Card Setup
Install [`cristianchelu/dispenser-schedule-card`](https://github.com/cristianchelu/dispenser-schedule-card) via HACS:

```yaml
type: custom:dispenser-schedule-card
device:
  type: xiaomi-smart-feeder-2
  entity: text.xiaomi_smart_pet_feeder_2_hardware_schedule
```

---

### 2. Petfeeder Rich Dashboard Card Setup
Install [`m1xminus/petfeeder-card`](https://github.com/m1xminus/petfeeder-card) via HACS:

```yaml
type: custom:petfeeder-card
main_title: "Xiaomi Pet Feeder 2"
today_grams_entity: sensor.xiaomi_smart_pet_feeder_2_daily_eaten
food_delivery_error_entity: binary_sensor.xiaomi_smart_pet_feeder_2_food_stuck
last_feed_entity: sensor.xiaomi_smart_pet_feeder_2_last_feed_event
left_status:
  - entity: sensor.xiaomi_smart_pet_feeder_2_bowl_weight
    icon: mdi:scale
    name: Bowl Weight
  - entity: binary_sensor.xiaomi_smart_pet_feeder_2_hopper_low
    icon: mdi:tray-alert
    name: Hopper
  - entity: sensor.xiaomi_smart_pet_feeder_2_desiccant_days_left
    icon: mdi:calendar-clock
    name: Desiccant
  - entity: binary_sensor.xiaomi_smart_pet_feeder_2_dispensing
    icon: mdi:cog-transfer-outline
    name: Status
tabs_config:
  show_tabs: true
  manual_feed:
    custom_doses_entity: number.xiaomi_smart_pet_feeder_2_manual_portions
    feed_button_entity: button.xiaomi_smart_pet_feeder_2_feed
  stats:
    items:
      - sensor.xiaomi_smart_pet_feeder_2_last_meal_intake
      - sensor.xiaomi_smart_pet_feeder_2_previous_meal_intake
      - sensor.xiaomi_smart_pet_feeder_2_daily_progress
      - sensor.xiaomi_smart_pet_feeder_2_schedule_count
  settings:
    - switch.xiaomi_smart_pet_feeder_2_skip_next_meal
    - switch.xiaomi_smart_pet_feeder_2_screen_auto_sleep
    - switch.xiaomi_smart_pet_feeder_2_child_lock
    - switch.xiaomi_smart_pet_feeder_2_anti_stacking
    - switch.xiaomi_smart_pet_feeder_2_grain_compensation
    - button.xiaomi_smart_pet_feeder_2_tare_scale
    - button.xiaomi_smart_pet_feeder_2_reset_desiccant

---

### 3. Beautiful Mushroom Dashboard Stack
For users of [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom):

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-title-card
    title: Xiaomi Pet Feeder 2
    subtitle: Local MIoT Control
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.xiaomi_smart_pet_feeder_2_bowl_weight
        name: Bowl Food
        icon: mdi:scale
        icon_color: green
      - type: custom:mushroom-entity-card
        entity: sensor.xiaomi_smart_pet_feeder_2_daily_eaten
        name: Eaten Today
        icon: mdi:food-drumstick
        icon_color: orange
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: binary_sensor.xiaomi_smart_pet_feeder_2_hopper_low
        name: Hopper Status
      - type: custom:mushroom-entity-card
        entity: sensor.xiaomi_smart_pet_feeder_2_desiccant_days_left
        name: Desiccant Days
        icon: mdi:calendar-clock
  - type: custom:mushroom-number-card
    entity: number.xiaomi_smart_pet_feeder_2_manual_portions
    name: Portions to Dispense
    icon: mdi:counter
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: button.xiaomi_smart_pet_feeder_2_feed
        name: Feed Now
        icon_color: deep-orange
        tap_action:
          action: call-service
          service: button.press
          target:
            entity_id: button.xiaomi_smart_pet_feeder_2_feed
      - type: custom:mushroom-entity-card
        entity: switch.xiaomi_smart_pet_feeder_2_skip_next_meal
        name: Skip Next Meal
        icon_color: red
```

### 3. Day / Night Screen Auto-Sleep Automation

```yaml
alias: "Pet Feeder: Day / Night Screen Dimming"
trigger:
  - platform: sun
    event: sunset
    id: night
  - platform: sun
    event: sunrise
    id: day
action:
  - choose:
      - conditions:
          - condition: trigger
            id: night
        sequence:
          - service: switch.turn_on
            target:
              entity_id: switch.xiaomi_smart_pet_feeder_2_screen_auto_sleep
      - conditions:
          - condition: trigger
            id: day
        sequence:
          - service: switch.turn_off
            target:
              entity_id: switch.xiaomi_smart_pet_feeder_2_screen_auto_sleep
```

---

## 🛠️ Custom Services (`services.yaml`)

- `xiaomi_feeder.feed`: Dispenses `portions` (1–30).
- `xiaomi_feeder.calibrate_scale`: Calibrates / zeroes the bowl scale.
- `xiaomi_feeder.skip_next_meal`: Skips 1 or $N$ upcoming scheduled meal(s).
- `xiaomi_feeder.reset_desiccant`: Resets the desiccant timer to current date.
- `xiaomi_feeder.set_refill_reminder`: Configures refill alert and interval hours.
- `xiaomi_feeder.set_intake_alarm`: Configures intake alarm threshold percentage.
- `xiaomi_feeder.clear_refill_alert`: Dismisses active refill alert.
- `xiaomi_feeder.clear_intake_alert`: Dismisses active intake alert.
- `xiaomi_feeder.clear_schedule`: Wipes all EEPROM meals.

---

## 📄 License
This project is licensed under the **GNU General Public License v3.0 or later (GPLv3+)**.
