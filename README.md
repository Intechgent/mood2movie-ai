# 🎬 Mood2Movie AI

**Mood-Aware Movie Recommendations Powered by LLM**

Mood2Movie AI is a small but thoughtful project I built to explore how large language models can improve everyday recommendation systems. Instead of relying only on rigid genres, the app suggests movies based on how a user is feeling and explains *why* a particular film fits that mood.

The goal was not just to recommend a movie, but to make the recommendation feel reasonable and human.

## Purpose of the project

Most movie apps categorize films into fixed genres and stop there. But that’s not how people actually choose what to watch. A sci-fi movie can be intense, comforting, slow, emotional, or even relaxing, depending on the story and on the viewer’s mindset.

I built Mood2Movie AI to experiment with a more natural approach. The user selects their mood, optionally narrows things down by genre, and the system uses **Google’s Gemini 3 Flash** to explain why a specific movie makes sense for that moment. The explanation matters just as much as the recommendation itself.

This project reflects how I think about AI: not as a replacement for logic, but as a layer that adds context, reasoning, and meaning.

---

## Application Working

### 1. Single-Page App Logic with Streamlit

Streamlit reruns the entire script every time the user interacts with the app, which makes building multi-step flows challenging. To handle this, I used `session_state` to simulate a single-page application experience.

* Navigation between views (landing, login, dashboard) is handled entirely through state, without page reloads.
* Movie recommendations are cached in memory so that user actions (like saving a movie) don’t trigger unnecessary API calls or reset the UI.

This approach helped me understand state management in reactive Python apps.

---

### 2. Persistence Using JSON

Instead of using a database server, I implemented a simple JSON-based storage layer to keep the project lightweight and easy to understand.

* Each user has a separate JSON file stored locally.
* The app supports basic CRUD operations: saving movies, updating watch status, adding notes, and removing entries.
* All changes stay synchronized with the UI and session state.

This allowed me to focus on application logic without introducing unnecessary infrastructure.

---

### 3. AI Integration and Failure Handling

Because LLM APIs are not always perfectly reliable, I designed the recommendation flow to fail gracefully.

* Each AI call is wrapped in error handling so the app does not crash if the API times out or returns an unexpected response.
* If an explanation cannot be generated, the system falls back to a predefined description instead of breaking the user experience.
* Safety settings are applied to keep responses appropriate and consistent.

This part of the project taught me a lot about defensive programming when working with external AI services.

---

## User Library Structure

Each saved movie entry is stored with context, not just a title:

| Field          | Description                                       |
| -------------- | ------------------------------------------------- |
| `status`       | Watch progress (Watching, Watched, Planned, etc.) |
| `comments`     | Personal notes or reflections                     |
| `mood_context` | Mood selected when the movie was recommended      |
| `added_at`     | Timestamp for tracking                            |

## Tech Stack

* **Language:** Python
* **Framework:** Streamlit
* **LLM:** Google Gemini 3 Flash
* **Data Handling:** Pandas
* **Environment Management:** Python-Dotenv

---

## Setup & Installation

1. **Clone the repository**

```bash
git clone [https://github.com/Intechgent/mood2movie-ai.git](https://github.com/Intechgent/mood2movie-ai.git)
cd mood2movie-ai
```

2. **Install dependencies**
```
pip install -r requirements.txt
```
3. **Configure API key**

Create a .env file in the project root
```
API_KEY=your_api_key
```
4. **Run the application**
```
streamlit run movies.py
```
