import streamlit as st
import json
import google.generativeai as genai

genai.configure(api_key="AIzaSyAzXtTdw5aqfy3vBXfcLaHOa4kks4q5xmQ")

def generate_quiz(topic, difficulty):
    RESPONSE_JSON = {
        "mcqs": [
            {
                "mcq": "What is the capital of France?",
                "options": {
                    "a": "Berlin",
                    "b": "Madrid",
                    "c": "Paris",
                    "d": "Rome",
                },
                "correct": "c"
            }
        ]
    }
    PROMPT_TEMPLATE = f"""
    You are an expert quiz creator. Generate a 5-question MCQ quiz on "{topic}" with difficulty "{difficulty}".
    Return the output strictly in JSON format as follows:

    {json.dumps(RESPONSE_JSON, indent=2)}
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(PROMPT_TEMPLATE)
        extracted_response = response.text.strip()

        extracted_response = extracted_response.strip("```json").strip("```").strip()
        quiz_data = json.loads(extracted_response)

        if "mcqs" not in quiz_data:
            raise KeyError("Invalid response format from API.")

        return quiz_data["mcqs"]

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

if "questions" not in st.session_state:
    st.session_state.questions = []
if "selected_options" not in st.session_state:
    st.session_state.selected_options = {}

def get_detailed_feedback(score, total, correct_topics, incorrect_topics):
    feedback_prompt = f"""
    A student completed a {total}-question quiz and scored {score}.
    Correct topics: {correct_topics}
    Incorrect topics: {incorrect_topics}

    Provide:
    1. Strengths analysis.
    2. Weaknesses analysis.
    3. Topics to focus on for improvement.
    4. Motivational feedback.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(feedback_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error fetching feedback: {str(e)}"


def ask_tutor(question):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(question)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("AI-Powered Personalized Learning System")

    topic = st.text_input("Enter quiz topic:")
    difficulty = st.selectbox("Select difficulty:", ['easy', 'medium', 'hard'])

    if st.button("Generate Quiz"):
        st.session_state.questions = generate_quiz(topic, difficulty)
        st.session_state.selected_options = {}

    if st.session_state.questions:
        st.subheader("Quiz Questions:")
        for idx, question in enumerate(st.session_state.questions, start=1):
            options = list(question["options"].values())
            selected_option = st.radio(
                f"**Q{idx}. {question['mcq']}**",
                options,
                index=None,
                key=f"q{idx}"
            )
            st.session_state.selected_options[idx] = selected_option

        if st.button("Submit"):
            marks = 0
            correct_topics = []
            incorrect_topics = []

            for i, question in enumerate(st.session_state.questions, start=1):
                selected_option_text = st.session_state.selected_options.get(i, None)
                correct_option_key = question["correct"]
                correct_option_text = question["options"][correct_option_key]

                is_correct = selected_option_text == correct_option_text
                if is_correct:
                    marks += 1
                    correct_topics.append(question["mcq"])
                else:
                    incorrect_topics.append(question["mcq"])

                st.markdown(f'<p style="font-size:16px;"><b>Q{i}. {question["mcq"]}</b></p>', unsafe_allow_html=True)

                if selected_option_text:
                    color = "green" if is_correct else "red"
                    st.markdown(
                        f'<p style="font-size:14px; color:{color};">You selected: <b>{selected_option_text}</b></p>',
                        unsafe_allow_html=True)
                else:
                    st.markdown(f'<p style="font-size:14px; color:orange;">You did not select an answer.</p>',
                                unsafe_allow_html=True)

                st.markdown(f'<p style="font-size:14px; color:green;">Correct answer: <b>{correct_option_text}</b></p>',
                            unsafe_allow_html=True)

            st.markdown(f"### **Quiz Result:**")
            st.markdown(
                f'<p style="font-size:19px;">You scored <strong>{marks}/{len(st.session_state.questions)}</strong></p>',
                unsafe_allow_html=True)

            feedback = get_detailed_feedback(marks, len(st.session_state.questions), correct_topics, incorrect_topics)

            cleaned_feedback = feedback.replace("#", "").strip()

            st.markdown(f'<p style="font-size:14px;"><b>Feedback:</b> {cleaned_feedback}</p>', unsafe_allow_html=True)

    st.subheader("AI Tutor")
    student_query = st.text_input("Ask a question:")
    if st.button("Get Answer"):
        answer = ask_tutor(student_query)
        st.write("AI Tutor Answer:", answer)

if __name__ == "__main__":
    main()
