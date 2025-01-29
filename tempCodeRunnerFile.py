@app.route("/results", methods=["GET"])
def display_results():
    return render_template("results.html", resumes=resume_data)
