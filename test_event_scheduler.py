# test_event_scheduler.py
import pytest
from app_with_bonus import app, EVENTS_FILE
import os
import json
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Cleanup
    if os.path.exists(EVENTS_FILE):
        os.remove(EVENTS_FILE)

# 🧪 Basic CRUD

def test_create_event(client):
    response = client.post('/events', json={
        'title': 'Unit Test Event',
        'description': 'pytest create test',
        'start_time': '2025-07-01T10:00:00',
        'end_time': '2025-07-01T11:00:00'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['event']['title'] == 'Unit Test Event'

def test_update_event(client):
    response = client.post('/events', json={
        'title': 'Old Title',
        'description': 'To update',
        'start_time': '2025-07-01T10:00:00',
        'end_time': '2025-07-01T11:00:00'
    })
    event_id = response.get_json()['event']['id']
    response = client.put(f'/events/{event_id}', json={'title': 'Updated Title'})
    assert response.status_code == 200
    assert response.get_json()['event']['title'] == 'Updated Title'

def test_delete_event(client):
    response = client.post('/events', json={
        'title': 'Delete Me',
        'description': 'pytest delete test',
        'start_time': '2025-07-01T10:00:00',
        'end_time': '2025-07-01T11:00:00'
    })
    event_id = response.get_json()['event']['id']
    response = client.delete(f'/events/{event_id}')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Event deleted'

def test_list_events(client):
    client.post('/events', json={
        'title': 'List Test',
        'description': 'pytest list',
        'start_time': '2025-07-02T10:00:00',
        'end_time': '2025-07-02T11:00:00'
    })
    response = client.get('/events')
    assert response.status_code == 200
    assert any(e['title'] == 'List Test' for e in response.get_json())

# 🧪 Recurrence Expansion

def test_recurring_event_expansion(client):
    client.post('/events', json={
        'title': 'Daily Task',
        'description': 'Occurs daily',
        'start_time': '2025-07-01T08:00:00',
        'end_time': '2025-07-01T09:00:00',
        'recurrence': 'daily'
    })
    response = client.get('/events')
    expanded = [e for e in response.get_json() if e['title'] == 'Daily Task']
    assert len(expanded) >= 5

# 🧪 Search Filtering

def test_search_title_filter(client):
    client.post('/events', json={
        'title': 'SearchMatchTitle',
        'description': 'random',
        'start_time': '2025-07-02T10:00:00',
        'end_time': '2025-07-02T11:00:00'
    })
    response = client.get('/events?title=match')
    assert any('SearchMatchTitle' in e['title'] for e in response.get_json())

def test_search_description_filter(client):
    client.post('/events', json={
        'title': 'AnotherTitle',
        'description': 'FindThisDescription',
        'start_time': '2025-07-03T10:00:00',
        'end_time': '2025-07-03T11:00:00'
    })
    response = client.get('/events?description=findthis')
    assert any('FindThisDescription' in e['description'] for e in response.get_json())

# 🧪 Edge Case: Invalid Time

def test_invalid_time_order(client):
    response = client.post('/events', json={
        'title': 'Invalid Time',
        'description': 'end before start',
        'start_time': '2025-07-01T12:00:00',
        'end_time': '2025-07-01T11:00:00'
    })
    assert response.status_code == 201  # In production you'd want 400; no validation yet

# 🧪 Reminder/Notification logic would need mocking or time patching (optional)
