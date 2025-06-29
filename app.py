from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import uuid
import json
import os
import threading
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
EVENTS_FILE = 'events.json'
REMINDER_INTERVAL = 60

def load_events():
    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, 'r') as f:
                content = f.read().strip()
                return json.loads(content) if content else []
        except json.JSONDecodeError:
            return []
    return []

def save_events(events):
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=4)

def is_due_soon(event_time):
    now = datetime.now()
    event_dt = datetime.fromisoformat(event_time)
    return now <= event_dt <= now + timedelta(hours=1)

def expand_recurring_events(events):
    expanded = []
    for event in events:
        if not event.get('recurrence'):
            expanded.append(event)
        else:
            freq = event['recurrence'] 
            base_time = datetime.fromisoformat(event['start_time'])
            for i in range(1, 5):  
                delta = timedelta(days=1) if freq == 'daily' else \
                        timedelta(weeks=1) if freq == 'weekly' else \
                        timedelta(days=30)
                new_time = base_time + i * delta
                clone = event.copy()
                clone['start_time'] = new_time.isoformat()
                expanded.append(clone)
    return expanded

def reminder_check():
    while True:
        events = expand_recurring_events(load_events())
        for event in events:
            if is_due_soon(event['start_time']) and not event.get('notified'):
                print(f"🔔 Reminder: {event['title']} at {event['start_time']}")
                send_email_reminder(event)
                event['notified'] = True
        save_events(events)
        time.sleep(REMINDER_INTERVAL)

def send_email_reminder(event):
    try:
        msg = EmailMessage()
        msg.set_content(f"Reminder: {event['title']} at {event['start_time']}\n{event['description']}")
        msg['Subject'] = f"Event Reminder: {event['title']}"
        msg['From'] = "your-real-email@gmail.com"
        msg['To'] = "your-other-email@example.com"


        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login("your-real-email@gmail.com", "your-app-password")
            server.send_message(msg)
    except Exception as e:
        print("Email error:", e)

@app.route('/events', methods=['POST'])
def create_event():
    data = request.get_json()
    event = {
        'id': str(uuid.uuid4()),
        'title': data['title'],
        'description': data.get('description', ''),
        'start_time': data['start_time'],
        'end_time': data['end_time'],
        'recurrence': data.get('recurrence', None), 
        'notified': False
    }
    events = load_events()
    events.append(event)
    save_events(events)
    return jsonify({'message': 'Event created', 'event': event}), 201

@app.route('/events', methods=['GET'])
def list_events():
    title_query = request.args.get('title', '').lower()
    desc_query = request.args.get('description', '').lower()

    events = expand_recurring_events(load_events())

    if title_query:
        events = [e for e in events if title_query in e.get('title', '').lower()]
    if desc_query:
        events = [e for e in events if desc_query in e.get('description', '').lower()]

    return jsonify(sorted(events, key=lambda x: x['start_time'])), 200

@app.route('/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.get_json()
    events = load_events()
    for event in events:
        if event['id'] == event_id:
            for field in ['title', 'description', 'start_time', 'end_time', 'recurrence']:
                if field in data:
                    event[field] = data[field]
            save_events(events)
            return jsonify({'message': 'Event updated', 'event': event}), 200
    return jsonify({'message': 'Event not found'}), 404

@app.route('/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    events = load_events()
    updated_events = [event for event in events if event['id'] != event_id]
    if len(events) == len(updated_events):
        return jsonify({'message': 'Event not found'}), 404
    save_events(updated_events)
    return jsonify({'message': 'Event deleted'}), 200

import time
threading.Thread(target=reminder_check, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
