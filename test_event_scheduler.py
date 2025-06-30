# test_event_scheduler.py
import pytest
from app import app, EVENTS_FILE
import os
import json
from datetime import datetime, timedelta

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

    if os.path.exists(EVENTS_FILE):
        os.remove(EVENTS_FILE)


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
    assert len(expanded) >= 4



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

    def test_missing_title(client):
        response = client.post('/events', json={
            'description': 'No title',
            'start_time': '2025-07-01T10:00:00',
            'end_time': '2025-07-01T11:00:00'
        })
        assert response.status_code == 400

    def test_missing_start_time(client):
        response = client.post('/events', json={
            'title': 'No Start Time',
            'description': 'Missing start_time',
            'end_time': '2025-07-01T11:00:00'
        })
        assert response.status_code == 400

    def test_missing_end_time(client):
        response = client.post('/events', json={
            'title': 'No End Time',
            'description': 'Missing end_time',
            'start_time': '2025-07-01T10:00:00'
        })
        assert response.status_code == 400

    def test_update_nonexistent_event(client):
        response = client.put('/events/nonexistent-id', json={'title': 'Should Fail'})
        assert response.status_code == 404

    def test_delete_nonexistent_event(client):
        response = client.delete('/events/nonexistent-id')
        assert response.status_code == 404

    def test_get_event_by_id(client):
        post_resp = client.post('/events', json={
            'title': 'GetById',
            'description': 'Testing get by id',
            'start_time': '2025-07-01T10:00:00',
            'end_time': '2025-07-01T11:00:00'
        })
        event_id = post_resp.get_json()['event']['id']
        get_resp = client.get(f'/events/{event_id}')
        assert get_resp.status_code == 200
        assert get_resp.get_json()['title'] == 'GetById'

    def test_invalid_recurrence_value(client):
        response = client.post('/events', json={
            'title': 'Invalid Recurrence',
            'description': 'Bad recurrence',
            'start_time': '2025-07-01T10:00:00',
            'end_time': '2025-07-01T11:00:00',
            'recurrence': 'weeklyyy'
        })
        assert response.status_code == 400
