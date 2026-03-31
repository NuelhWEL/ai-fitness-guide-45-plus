import streamlit as st
import requests
import os
import re

st.set_page_config(
    page_title="AI Fitness Guide 45+", page_icon="💪", layout="centered"
)
st.title("💪 AI Fitness Guide for 45+")
st.write("AI VERSION STABLE FINAL")

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
    "Content-Type": "application/json"
}

# Emoji colors
EMOJI_COLORS = {
    "💧": "#a7d8f0",  # Water/blue
    "🏋️": "#f5b041",  # Strength/orange
    "🏃": "#82e0aa",  # Cardio/green
    "🪑": "#d5dbdb",  # Chair/support/gray
    "💡": "#f7dc6f"   # General/yellow
}

# Streamlit input form
with st.form("fitness_form"):
    user_input = st.text_input(
        "Describe your fitness needs (e.g., improve mobility, lose weight, build strength, knee pains):"
    )
    submitted = st.form_submit_button("Get Recommendations")

if submitted:
    if not user_input.strip():
        st.warning("⚠️ Please enter your fitness needs")
    else:
        st.subheader("📝 AI Recommendations")

        payload = {
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "messages": [
                {"role": "system", "content": "You are a professional fitness coach."},
                {
                    "role": "user",
                    "content": (
                        "Provide 5-6 safe fitness tips for someone over 45. "
                        "Number the main tips. Include sub-points for instructions. "
                        "Use emojis: 💧 water, 🏋️ strength, 🏃 cardio, 🪑 chair/support, 💡 general tips. "
                        "Skip generic sentences. Output as plain text."
                    )
                }
            ],
            "temperature": 0.7,
            "max_tokens": 600
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            st.write("Status Code:", response.status_code)

            if response.status_code != 200:
                st.error(f"API returned an error: {response.text}")
            else:
                data = response.json()
                ai_text = data["choices"][0]["message"]["content"].strip()

                # Split tips
                tips = re.split(r'(?:Tip\s*\d+[:\s]*|\d+\.)', ai_text)
                tips = [t.strip() for t in tips if t.strip()]

                # Assign emoji to sub-points
                def assign_emoji(text):
                    lower = text.lower()
                    if any(w in lower for w in ["water", "swim"]):
                        return "💧 " + text
                    elif any(w in lower for w in ["squat", "strength", "weight", "push-up", "resistance"]):
                        return "🏋️ " + text
                    elif any(w in lower for w in ["walk", "run", "cardio", "pace", "brisk"]):
                        return "🏃 " + text
                    elif any(w in lower for w in ["chair", "support", "stability", "balance"]):
                        return "🪑 " + text
                    else:
                        return "💡 " + text

                # Display tips with collapsible sections
                for idx, tip in enumerate(tips, start=1):
                    sub_points = re.split(r'\n|[a-z]\.\s+', tip)
                    sub_points = [sp.strip(" *\n") for sp in sub_points if sp.strip(" *\n")]

                    if not sub_points:
                        continue

                    # Determine color from first emoji
                    first_emoji = sub_points[0][0] if sub_points[0][0] in EMOJI_COLORS else "💡"
                    color = EMOJI_COLORS.get(first_emoji, "#f7dc6f")

                    with st.expander(f"Tip {idx} {first_emoji}"):
                        st.markdown(
                            f"<div style='background-color:{color}; padding:10px; border-radius:10px;'>"
                            + "".join([f"<p>{assign_emoji(sp)}</p>" for sp in sub_points])
                            + "</div>", unsafe_allow_html=True
                        )

        except Exception as e:
            st.error(f"Request failed: {e}")