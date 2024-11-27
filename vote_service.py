from flask import Flask, render_template, request, redirect, url_for
import matplotlib
from statistics import median

matplotlib.use('Agg')  # Use the Agg backend for non-GUI environments

import matplotlib.pyplot as plt
import json
import os

STATE_FILE = "voting_state.json"

def save_state_to_json():
    """Save the current state of votes to a JSON file."""
    with open(STATE_FILE, "w") as f:
        json.dump(votes, f)

def load_state_from_json():
    """Load the state of votes from a JSON file if it exists."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            loaded_data = json.load(f)
            # Convert keys back to integers
            return {int(k): v for k, v in loaded_data.items()}
    return {i: {"confidence": [], "months": []} for i in range(len(questions))}



app = Flask(__name__)

# Predefined questions
questions = [
    "Feeds interface",
    "EMEA Aggregation rules",
    "EOD Timers",
    "BATS ETR Liknk",
    "EMEA In-memory cache",
    "Figuration fee engine",
    "Gloss HK interface",
    "Core Client UI Actions",
    "Firm block processing",
    "Tiger client leg",
    "Client static enrichment",
    "Comission/Fees",
    "Confirms",
    "APAC CTM",
    "Financial fees",
    "Client file loader",
    "Apac in memory cache",
    "US Pre allocations methods",
    "US CTM",
    "Power principal",
    "Back2back legs",
    "Bonds",
    "Options/OCC",
    "US in-memory cache",
    "Power client leg",
    "Ops checks",
    "Give-up",
    "Brokers2Custody",
    "EMEA block reshaping",
    "Gloss HK",
    "OTA",
    "Gloss JP",
    "APAC boocking model",
    "SOPA",
    "KOSMOS",
    "TRIANA",
    "Dolphin feed",
    "Power hedge booking",
    "Done with",
    "GBA tech debt (<5) 2028",
    "APAC TRIANA",
    "APAC Donw away",
    "Transparency reporting",
    "LSA",
    "Done away",
    "Rebalancing",
    "APAC client gloss JP",
    "FX exposure Mgt",
    "D1 Integration",
    "Apac client japan Rebalancinfg",
    "Shell swap",
    "Option delta",
    "Risk checks",
    "GBA tech debt <5 2030",
    "FIX post allocations",
]

# Data storage
votes = load_state_from_json()

@app.route("/")
def index():
    return redirect(url_for("vote", qid=0))

@app.route("/vote/<int:qid>", methods=["GET", "POST"])
def vote(qid):
    if qid >= len(questions):
        return redirect(url_for("results"))

    if request.method == "POST":
        # Save the vote
        confidence = request.form.get("confidence")
        months = request.form.get("months")

        if confidence and months.isdigit():
            votes[qid]["confidence"].append(confidence)
            votes[qid]["months"].append(int(months))
            save_state_to_json()  # Save state after updating

        return redirect(url_for("vote", qid=qid + 1))

    return render_template("vote.html", question=questions[qid], qid=qid)


from statistics import median


@app.route("/results")
def results():
    results = []
    median_months = []
    median_confidence_scores = []
    question_titles = []

    # Map confidence levels to numerical values
    confidence_mapping = {"none": 0, "medium": 1, "full": 2}

    for qid, data in votes.items():
        median_month = median(data["months"]) if data["months"] else 0
        median_months.append(median_month)

        numerical_confidence = [confidence_mapping[c] for c in data["confidence"]]
        median_confidence = median(numerical_confidence) if numerical_confidence else 0
        median_confidence_scores.append(median_confidence)

        question_titles.append(questions[qid])

        # Generate Voter ID vs. Months chart
        months_chart_path = f"static/months_chart_{qid}.png"
        plt.figure(figsize=(14, 7))  # Set chart size to 1024x512
        plt.bar(range(len(data["months"])), data["months"])
        plt.title(f"Voter Months for Question {qid + 1}")
        plt.xlabel("Voter ID")
        plt.ylabel("Months of Experience")
        plt.savefig(months_chart_path)
        plt.close()

        # Generate Voter ID vs. Confidence chart
        confidence_chart_path = f"static/confidence_chart_{qid}.png"
        plt.figure(figsize=(14, 7))  # Set chart size to 1024x512
        plt.bar(range(len(numerical_confidence)), numerical_confidence)
        plt.title(f"Voter Confidence for Question {qid + 1}")
        plt.xlabel("Voter ID")
        plt.ylabel("Confidence Level (0=None, 1=Medium, 2=Full)")
        plt.savefig(confidence_chart_path)
        plt.close()

        results.append({
            "question": questions[qid],
            "months_chart_path": months_chart_path,
            "confidence_chart_path": confidence_chart_path,
        })

    # Generate overall median months chart
    overall_months_chart_path = "static/overall_median_months.png"
    plt.figure(figsize=(14, 7))  # Set chart size to 1024x512
    plt.bar(question_titles, median_months)
    plt.title("Median Months by Question")
    plt.xlabel("Questions")
    plt.ylabel("Median Months")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(overall_months_chart_path)
    plt.close()

    # Generate overall median confidence chart
    overall_confidence_chart_path = "static/overall_median_confidence.png"
    plt.figure(figsize=(14, 7))  # Set chart size to 1024x512
    plt.bar(question_titles, median_confidence_scores)
    plt.title("Median Confidence by Question")
    plt.xlabel("Questions")
    plt.ylabel("Median Confidence (0=None, 1=Medium, 2=Full)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(overall_confidence_chart_path)
    plt.close()

    return render_template(
        "results.html",
        results=results,
        overall_months_chart=overall_months_chart_path,
        overall_confidence_chart=overall_confidence_chart_path,
    )


if __name__ == "__main__":
    # Ensure static directory exists for charts
    os.makedirs("static", exist_ok=True)
    app.run(debug=True)