from flask import Flask, render_template, send_from_directory, abort
from pathlib import Path
import pandas as pd

app = Flask(__name__)

# ==========================================
# PROJECT FOLDERS
# ==========================================

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
RESULTS_FOLDER = PROJECT_FOLDER / "Results"


# ==========================================
# DATA LOADING FUNCTION
# ==========================================

def load_data(filename):
    file_path = RESULTS_FOLDER / filename

    if file_path.is_file():
        return pd.read_csv(file_path)

    print(f"WARNING: Dataset not found: {filename}")
    return pd.DataFrame()


# ==========================================
# LOAD RESEARCH DATASETS
# ==========================================

corrosion_data = load_data("corrosion_rate_predictions.csv")
service_data = load_data("service_life_analysis.csv")
lcc_data = load_data("integrated_lcc_results_v2.csv")
environment_data = load_data("annual_environmental_data.csv")

thickness_data = load_data("steel_thickness_assessment.csv")
thickness_summary = load_data("steel_thickness_50_year_summary.csv")


# ==========================================
# TABLE GENERATION
# ==========================================

def make_table(data):

    if data.empty:
        return "<p>No data available. Check the dataset.</p>"

    return data.to_html(
        index=False,
        classes="data-table",
        border=0,
        float_format=lambda x: f"{x:.2f}"
    )


# ==========================================
# MAIN DASHBOARD
# ==========================================

@app.route("/")
def dashboard():

    locations = ["Tema", "Kumasi"]

    if not corrosion_data.empty and "Location" in corrosion_data.columns:
        locations = corrosion_data["Location"].dropna().unique().tolist()

    summary = {
        "locations": len(locations),
        "corrosion_records": len(corrosion_data),
        "service_records": len(service_data),
        "economic_records": len(lcc_data),
        "analysis_period": 50,
        "study_locations": locations
    }

    return render_template("index.html", summary=summary)


# ==========================================
# ENVIRONMENTAL DATA
# ==========================================

@app.route("/environment")
def environment():

    location_count = 0

    if not environment_data.empty and "Location" in environment_data.columns:
        location_count = environment_data["Location"].nunique()

    return render_template(
        "environment.html",
        records_html=make_table(environment_data),
        row_count=len(environment_data),
        location_count=location_count
    )


# ==========================================
# CORROSION PREDICTION
# ==========================================

@app.route("/corrosion")
def corrosion():

    location_count = 0
    scenario_count = 0

    if not corrosion_data.empty:

        if "Location" in corrosion_data.columns:
            location_count = corrosion_data["Location"].nunique()

        if "Scenario" in corrosion_data.columns:
            scenario_count = corrosion_data["Scenario"].nunique()

    return render_template(
        "corrosion.html",
        records_html=make_table(corrosion_data),
        row_count=len(corrosion_data),
        location_count=location_count,
        scenario_count=scenario_count
    )


# ==========================================
# STEEL THICKNESS ASSESSMENT
# ==========================================

@app.route("/thickness")
def thickness():

    return render_template(
        "thickness.html",
        thickness_table=make_table(thickness_data),
        summary_table=make_table(thickness_summary),
        thickness_rows=len(thickness_data),
        summary_rows=len(thickness_summary)
    )


# ==========================================
# SERVICE-LIFE ANALYSIS
# ==========================================

@app.route("/service-life")
def service_life():

    location_count = 0

    if not service_data.empty and "Location" in service_data.columns:
        location_count = service_data["Location"].nunique()

    return render_template(
        "service_life.html",
        records_html=make_table(service_data),
        record_count=len(service_data),
        location_count=location_count
    )


# ==========================================
# ECONOMIC ANALYSIS
# ==========================================

@app.route("/economics")
def economics():

    return render_template(
        "economics.html",
        records_html=make_table(lcc_data),
        record_count=len(lcc_data)
    )


# ==========================================
# GRAPHS AND VISUALISATION
# ==========================================

@app.route("/graphs")
def graphs():

    return render_template("graphs.html")


# ==========================================
# REPORTS AND RESULTS
# ==========================================

@app.route("/reports")
def reports():

    return render_template("reports.html")


# ==========================================
# DATASET DOWNLOADS
# ==========================================

DOWNLOADABLE_FILES = {
    "annual_environmental_data.csv",
    "corrosion_rate_predictions.csv",
    "service_life_analysis.csv",
    "integrated_lcc_results_v2.csv"
}


@app.route("/download/<filename>")
def download_file(filename):

    if filename not in DOWNLOADABLE_FILES:
        abort(404)

    file_path = RESULTS_FOLDER / filename

    if not file_path.is_file():
        print(f"DOWNLOAD ERROR: {file_path}")
        abort(404)

    return send_from_directory(
        str(RESULTS_FOLDER),
        filename,
        as_attachment=True
    )


# ==========================================
# START APPLICATION
# ==========================================

if __name__ == "__main__":

    print("------------------------------------")
    print("ATMOSPHERIC CORROSION RESEARCH PORTAL")
    print("------------------------------------")
    print(f"Project folder: {PROJECT_FOLDER}")
    print(f"Results folder: {RESULTS_FOLDER}")

    app.run(debug=True)