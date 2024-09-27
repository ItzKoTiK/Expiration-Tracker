# Expiration Tracker
A thing to manage food items by tracking their expiration dates and stuff

## Features

- **Add Items**: Input the name and expiration time (e.g: 5d, 1w, 12m, inf) for new food items.
- **Edit Items**: Modify existing item details, including names and expiration times.
- **Delete Items**: Remove specific items or all expired items from the list.
- **Copy Items**: Copy all item names to the clipboard for easy sharing or reference.
- **Scrollable Interface**: Navigate through the list of items using a scrollable frame.
- **Persistent Settings**: Remembers the last window size and position for a seamless user experience.

## Installation

1. Ensure you have Python installed on your machine.
2. Download the source code from the repository.
3. Install any required libraries, primarily Tkinter (usually included with Python).

OR

1. Download release.zip
2. Unzip it
3. Run

## Default Expiration Times
The application includes preset expiration times for common food items, which can be referenced if a user does not provide an expiration time when adding a new item (lower case singular - e.g apple, banana).

## File Management

- **Data File**: Items are stored in `data.json`, which can be manually edited if necessary.
- **Settings File**: The window size and position are stored in `settings.json`.
