document.addEventListener('DOMContentLoaded', function () {
    // Initial data loading
    loadAlarms();
    loadMemos();

    // Form submit event listeners
    document.getElementById('alarmForm').addEventListener('submit', handleAlarmSubmit);
    document.getElementById('memoForm').addEventListener('submit', handleMemoSubmit);
});

// Alarm-related functions
async function loadAlarms() {
    try {
        const response = await fetch('/api/alarms');
        const alarms = await response.json();
        displayAlarms(alarms);
    } catch (error) {
        console.error('Error while loading alarms:', error);
        alert('Failed to load alarms.');
    }
}

function displayAlarms(alarms) {
    const alarmsList = document.getElementById('alarmsList');
    alarmsList.innerHTML = '';

    alarms.forEach(alarm => {
        const item = document.createElement('div');
        item.className = 'list-group-item';

        const daysText = alarm.days ?
            alarm.days.split(',').map(d => ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][parseInt(d)]).join(', ') :
            (alarm.specific_date ? `${alarm.specific_date}` : 'No Repeat');

        item.innerHTML = `
            <div class="alarm-info">
                <div class="alarm-time">${alarm.time}</div>
                <div class="alarm-label">${alarm.label || 'Alarm'}</div>
                <div class="alarm-days">${daysText}</div>
            </div>
            <div class="alarm-actions">
                <button class="btn btn-sm btn-outline-danger" onclick="deleteAlarm(${alarm.id})">Delete</button>
                <button class="btn btn-sm btn-outline-primary" onclick="toggleAlarm(${alarm.id}, ${!alarm.is_active})">
                    ${alarm.is_active ? 'Deactivate' : 'Activate'}
                </button>
            </div>
        `;
        alarmsList.appendChild(item);
    });
}

async function handleAlarmSubmit(event) {
    event.preventDefault();

    const time = document.getElementById('alarmTime').value;
    const label = document.getElementById('alarmLabel').value;
    const specificDate = document.getElementById('specificDate').value;

    const days = Array.from(document.querySelectorAll('.btn-check'))
        .map((checkbox, index) => checkbox.checked ? index : null)
        .filter(day => day !== null)
        .join(',');

    try {
        const response = await fetch('/api/alarms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                time,
                label,
                days: days || null,
                specific_date: specificDate || null
            })
        });

        if (response.ok) {
            event.target.reset();
            loadAlarms();
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        console.error('Error while adding alarm:', error);
        alert('Failed to add alarm.');
    }
}

async function deleteAlarm(id) {
    if (!confirm('Do you want to delete this alarm?')) return;

    try {
        const response = await fetch(`/api/alarms/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadAlarms();
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        console.error('Error while deleting alarm:', error);
        alert('Failed to delete alarm.');
    }
}

async function toggleAlarm(id, isActive) {
    try {
        const response = await fetch(`/api/alarms/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                is_active: isActive
            })
        });

        if (response.ok) {
            loadAlarms();
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        console.error('Error while toggling alarm status:', error);
        alert('Failed to update alarm status.');
    }
}

// Memo-related functions
async function loadMemos() {
    try {
        const response = await fetch('/api/memos');
        const memos = await response.json();
        displayMemos(memos);
    } catch (error) {
        console.error('Error while loading memos:', error);
        alert('Failed to load memos.');
    }
}

function displayMemos(memos) {
    const memosList = document.getElementById('memosList');
    memosList.innerHTML = '';

    memos.forEach(memo => {
        const item = document.createElement('div');
        item.className = 'list-group-item';

        item.innerHTML = `
            <div class="memo-info">
                <div class="memo-content">${memo.content}</div>
                ${memo.date ? `<div class="memo-date">${memo.date}</div>` : ''}
            </div>
            <div class="memo-actions">
                <button class="btn btn-sm btn-outline-danger" onclick="deleteMemo(${memo.id})">Delete</button>
            </div>
        `;
        memosList.appendChild(item);
    });
}

async function handleMemoSubmit(event) {
    event.preventDefault();

    const content = document.getElementById('memoContent').value;
    const date = document.getElementById('memoDate').value;

    try {
        const response = await fetch('/api/memos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content,
                date: date || null
            })
        });

        if (response.ok) {
            event.target.reset();
            loadMemos();
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        console.error('Error while adding memo:', error);
        alert('Failed to add memo.');
    }
}

async function deleteMemo(id) {
    if (!confirm('Do you want to delete this memo?')) return;

    try {
        const response = await fetch(`/api/memos/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadMemos();
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        console.error('Error while deleting memo:', error);
        alert('Failed to delete memo.');
    }
}