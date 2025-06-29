# 📅 Event Scheduler API

A simple Flask-based event scheduler with support for recurring events, email reminders, and search functionality.

## ✨ Features

- 📝 Create, update, delete, and list events
- 🔁 Support for recurring events (daily, weekly, monthly)
- 📧 Email reminders for upcoming events
- 🔍 Search events by title or description
- 🛠️ RESTful API endpoints

## ⚙️ Requirements

- 🐍 Python 3.7+
- 🌶️ Flask
- 🧪 pytest (for testing)

## 🚀 Setup

1. **Clone the repository**  
   ```
   git clone https://github.com/shubham032/Event_Scheduler_System.git
   cd Event_Scheduler_System
   ```

2. **Install dependencies**  
   ```
   pip install -r requirements.txt
   ```

3. **Configure Email**  
   Edit `app.py` and set your real Gmail address and app password in the `send_email_reminder` function.

4. **Run the app**  
   ```
   python app.py
   ```

   The API will be available at `http://127.0.0.1:5000/`.

## 📚 API Endpoints

- `POST /events`  
  Create a new event.  
  JSON body:  
  ```json
  {
    "title": "Event Title",
    "description": "Event Description",
    "start_time": "YYYY-MM-DDTHH:MM:SS",
    "end_time": "YYYY-MM-DDTHH:MM:SS",
    "recurrence": "daily" | "weekly" | "monthly" | null
  }
  ```

- `GET /events`  
  List all events. Supports query params: `title`, `description`.

- `PUT /events/<event_id>`  
  Update an event.

- `DELETE /events/<event_id>`  
  Delete an event.

## 🧪 Running Tests

```
pytest
```

## 📝 Notes

- 📧 Email reminders require a valid Gmail account and app password (Use App Passwords-(https://support.google.com/accounts/answer/185833?visit_id=638867834786739463-370313180&p=InvalidSecondFactor&rd=1) if 2FA is enabled.).
- 💾 Events are stored in `events.json` in the project directory.

---