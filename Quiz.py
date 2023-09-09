import customtkinter as ctk  # Importiere das "customtkinter" Modul für die Benutzeroberfläche.
import sqlite3  # Importiere das "sqlite3" Modul für die Datenbankverbindung.

class App(ctk.CTk):
    def __init__(self):
        super().__init__()  # Initialisiere die App.

        # Einstellungen für das Hauptfenster der App
        self.title('Abschlussprüfung Quiz')  # Titel des Fensters
        self.geometry('600x350')  # Größe des Fensters (Breite x Höhe)
        self.resizable(False, False)  # Deaktiviere die Größenänderung des Fensters.

        ctk.set_appearance_mode("dark")  # Setze das Erscheinungsbild der Benutzeroberfläche auf "dark" (dunkel).
        ctk.set_default_color_theme("dark-blue")  # Setze das Farbthema auf "dark-blue" (dunkelblau).

        # Verbindung zur SQLite-Datenbank "Fragen.db" herstellen
        conn = sqlite3.connect("Fragen.db")
        self.cursor = conn.cursor()

        # Globale Variablen initialisieren
        global i
        global id
        id = 1  # Aktuelle Frage-ID
        i = -1  # Anzahl der richtig beantworteten Fragen

        # Labels für Rückmeldungen
        self.l2 = ctk.CTkLabel(self, font=("Arial", 14), text="Richtig!")
        self.l3 = ctk.CTkLabel(self, font=("Arial", 14), text="Falsch!")
        self.l4 = ctk.CTkLabel(self, font=("Arial", 14),
                               text="Keine Frage wurde richtig beantwortet, \ndu hast keine Ahnung von Fachinformatik")

        # Die erste Frage laden
        self.load_question()

    def load_question(self):
        global id
        self.selected_answer = ctk.StringVar()

        try:
            # Frage aus der Datenbank abrufen
            self.cursor.execute("SELECT Frage FROM Quiz WHERE Nummer = ?", (id,))
            question = self.cursor.fetchone()[0]

            # Antwortmöglichkeiten aus der Datenbank abrufen
            self.cursor.execute("SELECT Antwort1, Antwort2, Antwort3, Antwort4 FROM Quiz WHERE Nummer = ?", (id,))
            answers = self.cursor.fetchone()

            # Richtige Antwort aus der Datenbank abrufen
            self.cursor.execute("SELECT RichtigeAntwort FROM Quiz WHERE Nummer = ?", (id,))
            correct_answer = self.cursor.fetchone()[0]
        except TypeError:
            # Wenn es keine weiteren Fragen gibt, zeige eine Abschlussmeldung an.
            for widget in self.winfo_children():
                if widget is not self.l2 and widget is not self.l3 and widget is not self.l4 and (
                        isinstance(widget, (ctk.CTkRadioButton, ctk.CTkLabel))):
                    widget.destroy()
            self.hide_l3()
            self.l4.pack(pady=150)
            return

        # Lösche vorherige Frage-Widgets
        for widget in self.winfo_children():
            if widget is not self.l2 and widget is not self.l3 and widget is not self.l4 and (
                    isinstance(widget, (ctk.CTkRadioButton, ctk.CTkLabel))):
                widget.destroy()

        # Formatieren der Frage, um sie lesbar darzustellen
        words = question.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 80:
                if current_line:
                    current_line += " "
                current_line += word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Frage-Text für das Label erstellen
        question_text = '\n'.join(lines)
        question_label_text = f"Frage {id} von 20:\n{question_text}"

        l1 = ctk.CTkLabel(self, font=("Arial", 14), text=question_label_text)

        l1.place(relx=0.5, rely=0.2, anchor="center")
        self.columnconfigure(0, weight=1)

        # Antwortoptionen als Radio-Buttons anzeigen
        for idx, answer in enumerate(answers):
            ctk.CTkRadioButton(self, text=answer, value=answer, variable=self.selected_answer,
                               command=self.antwort).place(relx=0.5, rely=0.35 + idx * 0.1, anchor="center")

        self.correct_answer = correct_answer

    def antwort(self):
        global id
        global i
        selected_answer = self.selected_answer.get().strip()

        if selected_answer == self.correct_answer.strip():
            # Wenn die Antwort richtig ist
            self.l3.place_forget()
            self.l2.place(relx=0.5, rely=0.8, anchor="center")
            self.after(2000, self.hide_l2)

            i += 1

            # Berechnung des Prozentsatzes der richtigen Antworten
            percentage = (i / id) * 100
            rounded_percentage = round(percentage)
            if rounded_percentage < 50:
                self.l4.configure(
                    text=f"LOL du hast nicht bestanden! \nAnteil der richtig beantworteten Fragen: {rounded_percentage}%")
            elif 50 <= rounded_percentage < 80:
                self.l4.configure(
                    text=f"Nicht schlecht! \nAnteil der richtig beantworteten Fragen: {rounded_percentage}%")
            else:
                self.l4.configure(
                    text=f"Gut gemacht! \nAnteil der richtig beantworteten Fragen: {rounded_percentage}%")

        else:
            # Wenn die Antwort falsch ist
            self.l2.pack_forget()
            self.l3.place(relx=0.5, rely=0.8, anchor="center")

            # Richtige Antwort formatieren
            self.cursor.execute("SELECT RichtigeAntwort FROM Quiz WHERE Nummer = ?", (id,))
            richtige_antwort = self.cursor.fetchone()[0]
            r2 = richtige_antwort.split()
            lines = []
            current_line = ""

            for word in r2:
                if len(current_line) + len(word) + 1 <= 80:
                    if current_line:
                        current_line += " "
                    current_line += word
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            formatted_text = '\n'.join(lines)
            correct_answer_text = f"Falsch! Die richtige Antwort war:\n{formatted_text}"

            self.l3.configure(text=correct_answer_text)

        id = id + 1
        self.load_question()

    def hide_l2(self):
        self.l2.place_forget()

    def hide_l3(self):
        self.l3.place_forget()

if __name__ == "__main__":
    app = App()
    app.mainloop()  # Starte die GUI-Anwendung
