# UHB Phone Directory

A desktop application dedicated to searching and managing contacts. Developed using Python and the PyQt6 framework, it relies on an Excel file as a flexible and easily updatable database.

# 📌 Features
* Quick Search: Instant filtering by name or phone number.
* Flexible Database: The Excel file (`Phone directory.xlsx`) located in the `data` folder serves as the database. You can open it to edit or add names at any time, and the application will update instantly without requiring any code modifications.
* Interactive Cards: Displays contact information in a professionally designed digital business card.
* Direct Integration: Open WhatsApp chats or send an email with a single click.
* Export & Share: Save the card as an image (PNG) or PDF (A4 or business card size), with direct copying and sharing capabilities.

# 📂 Project Structure (For Developers)

The project is structured professionally to facilitate reading and development:

* `main.py`: The entry point to run the application.
* `src/`: The main source code folder, containing:
  * `ui/`: User interface files (main window and business card dialog).
  * `core/`: Background operations and data processing (e.g., reading Excel in the background).
  * `utils/`: Helper functions.
* `data/`: Contains the database (the directly editable `Phone directory.xlsx` file).
* `assets/`: Contains static resources like icons and fonts.

# ⚙️ Requirements (Development Environment)
To run the source code, ensure the following libraries are installed via `pip`:
* `PyQt6`
* `pandas`
* `openpyxl`
* `reportlab`
