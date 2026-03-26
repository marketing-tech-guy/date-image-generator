import os
from flask import Flask, render_template, request, send_file
from generator import generate_images

app = Flask(__name__)

VALID_MONTHS = {
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
}


@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        month = request.form.get("month", "").strip()
        year = request.form.get("year", "").strip()

        if not month or not year:
            error = "Please enter both month and year."
            return render_template("index.html", error=error)

        if month.lower() not in VALID_MONTHS:
            error = "Please enter a valid full month name, like September."
            return render_template("index.html", error=error, month=month, year=year)

        try:
            year = int(year)
        except ValueError:
            error = "Year must be a number."
            return render_template("index.html", error=error, month=month, year=year)

        month = month.capitalize()
        zip_path = generate_images(month, year)

        return send_file(
            zip_path,
            as_attachment=True,
            download_name=f"{month}_{year}_images.zip",
            mimetype="application/zip"
        )

    return render_template("index.html", error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
